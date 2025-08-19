import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document
import re
import hashlib
import io
import uuid
import shutil
import os
import logging
import time
from datetime import datetime

from prompts import build_summary_prompt, build_chat_prompt
from patterns import detect_document_type

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

st.title("Copiloto Conversacional para PDFs")

# ===========================
# Configuración
# ===========================
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "")


# ===========================
# Funciones de mantenimiento
# ===========================

def remove_file_by_hash(filehash: str):
    try:
        vs = st.session_state.get("vectorstore")
        ids = st.session_state.get("doc_ids_by_filehash", {}).get(filehash, [])
        if vs is not None:
            if ids:
                try:
                    vs.delete(ids=ids)
                except Exception:
                    pass
            else:
                try:
                    vs.delete(where={"filehash": filehash})
                except Exception:
                    pass
    except Exception:
        pass

    st.session_state["pdf_chunks"] = [
        d for d in st.session_state.get("pdf_chunks", [])
        if d.metadata.get("filehash") != filehash
    ]

    st.session_state["summaries"] = [
        s for s in st.session_state.get("summaries", [])
        if s.get("filehash") != filehash
    ]

    st.session_state.get("processed_hashes", set()).discard(filehash)
    if "doc_ids_by_filehash" in st.session_state:
        st.session_state["doc_ids_by_filehash"].pop(filehash, None)


def remove_all_files_one_by_one():
    """Elimina uno a uno todos los archivos procesados."""
    for fh in list(st.session_state.get("processed_hashes", set())):
        remove_file_by_hash(fh)


def _delete_chroma_collection_if_possible():
    """Intenta borrar la colección actual de Chroma (si existe y hay cliente)."""
    try:
        vs = st.session_state.get("vectorstore")
        col_name = st.session_state.get("collection_name")
        if vs is not None and col_name:
            try:
                vs._client.delete_collection(name=col_name)
            except Exception:
                try:
                    coll = vs._client.get_collection(name=col_name)
                    vs._client.delete_collection(name=coll.name)
                except Exception:
                    pass
    except Exception:
        pass


def _delete_persist_dir_if_configured():
    """Si hay persistencia configurada, borra el directorio en disco."""
    try:
        if CHROMA_PERSIST_DIR:
            if os.path.isdir(CHROMA_PERSIST_DIR):
                shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)
    except Exception:
        pass


def _reset_core_state(regen_uploader: bool = True):
    st.session_state["vectorstore"] = None
    st.session_state["embeddings"] = None
    st.session_state["chat_messages"] = []
    st.session_state["pdf_chunks"] = []
    st.session_state["summaries"] = []
    st.session_state["processed_hashes"] = set()
    st.session_state["doc_ids_by_filehash"] = {}
    st.session_state["collection_name"] = f"langchain-{uuid.uuid4().hex[:8]}"
    if regen_uploader:
        st.session_state["uploader_key"] = f"uploader-{uuid.uuid4().hex[:6]}"


def _full_reset(regen_uploader: bool = True):
    remove_all_files_one_by_one()
    _delete_chroma_collection_if_possible()
    _delete_persist_dir_if_configured()
    _reset_core_state(regen_uploader=regen_uploader)


# ===========================
# Estado de sesión inicial
# ===========================

if "_fresh_session_initialized" not in st.session_state:
    _full_reset(regen_uploader=True)
    st.session_state["_fresh_session_initialized"] = True

if 'pdf_chunks' not in st.session_state:
    st.session_state.pdf_chunks = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'processed_hashes' not in st.session_state:
    st.session_state.processed_hashes = set()
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'summaries' not in st.session_state:
    st.session_state.summaries = []
if 'collection_name' not in st.session_state:
    st.session_state.collection_name = f"langchain-{uuid.uuid4().hex[:8]}"
if 'doc_ids_by_filehash' not in st.session_state:
    st.session_state.doc_ids_by_filehash = {}
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = f"uploader-{uuid.uuid4().hex[:6]}"

# ===========================
# Sidebar: Uploader y Reset
# ===========================

with st.sidebar:
    st.markdown("### 📥 Sube hasta 5 PDFs")
    uploaded_files = st.file_uploader(
        "Arrastra aquí tus archivos",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=st.session_state.uploader_key
    )
    st.caption("Límite 200 MB por archivo · PDF")

    st.divider()

    if st.button("🔄 Reiniciar sesión", use_container_width=True):
        _full_reset(regen_uploader=True)
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7;">
        <h4 style="margin-bottom: 10px;">👨‍💻 Desarrollado por</h4>
        <p style="font-size: 16px; margin-bottom: 8px;"><strong>Mauricio Arrieta</strong></p>
        <p style="font-size: 14px;">
            <a href="https://github.com/maweex" target="_blank" style="text-decoration: none; color: inherit;">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="display: inline-block; margin-right: 5px;">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                GitHub
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===========================
# Inicializar Llama3 local
# ===========================

ollama_base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Inicializar el modelo de lenguaje local
llm: Ollama = Ollama(
    model=ollama_model,
    temperature=0.1,
    base_url=ollama_base,
    num_predict=512,
    top_k=10,
    top_p=0.9,
    repeat_penalty=1.1
)

# ===========================
# Patterns
# ===========================


def create_adaptive_chunks(text: str, doc_type: str, filename: str, filehash: str):
    if doc_type == 'guion_pelicula':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=300,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
    elif doc_type == 'articulo_academico':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
    elif doc_type == 'curriculum_vitae':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
    elif doc_type == 'brochure_educativo':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
    elif doc_type == 'brochure_servicios':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )

    basic_chunks = splitter.split_text(text)
    documents = []
    for i, chunk in enumerate(basic_chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    'source': filename,
                    'filehash': filehash,
                    'doc_type': doc_type,
                    'chunk_id': i,
                    'chunk_size': len(chunk),
                    'total_chunks': len(basic_chunks)
                }
            )
        )
    return documents


def create_smart_summary(text: str, doc_type: str, filename: str) -> str:
    text_limited = text[:2000] if len(text) > 2000 else text
    logger.info(
        f"📝 Texto limitado a {len(text_limited)} caracteres para resumen")

    prompt = build_summary_prompt(text_limited, doc_type)
    return llm.invoke(prompt)


def unique_label(base_label: str, existing_labels: set, suffix: str) -> str:
    label = base_label
    if label not in existing_labels:
        return label
    alt = f"{base_label} ({suffix})"
    i = 2
    while alt in existing_labels:
        alt = f"{base_label} ({suffix}-{i})"
        i += 1
    return alt


# ===========================
# Procesamiento de PDFs
# ===========================

with st.sidebar:
    pass

if 'uploaded_files' not in locals():
    uploaded_files = None

if uploaded_files:
    if st.session_state.embeddings is None:
        st.session_state.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

    current_hashes = set()
    for f in uploaded_files:
        fb = f.getvalue()
        current_hashes.add(hashlib.md5(fb).hexdigest())

    removed_hashes = st.session_state.processed_hashes - current_hashes
    for fh in list(removed_hashes):
        remove_file_by_hash(fh)

    existing_labels = {item['label'] for item in st.session_state.summaries}

    for pdf_file in uploaded_files:
        start_time = time.time()
        logger.info(f"🚀 Iniciando procesamiento de: {pdf_file.name}")

        try:
            file_bytes = pdf_file.getvalue()
            filehash = hashlib.md5(file_bytes).hexdigest()
            logger.info(f"📄 Hash del archivo: {filehash[:8]}...")

            if filehash in st.session_state.processed_hashes:
                logger.info(f"⏭️ Archivo ya procesado: {pdf_file.name}")
                continue

            logger.info(f"📖 Extrayendo texto de {pdf_file.name}...")
            reader = PdfReader(io.BytesIO(file_bytes))
            full_text = ""
            total_pages = len(reader.pages)
            logger.info(f"📄 Total de páginas: {total_pages}")

            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
                    if i % 5 == 0:  # Log cada 5 páginas
                        logger.info(f"📄 Página {i}/{total_pages} procesada")

            logger.info(f"✅ Texto extraído: {len(full_text)} caracteres")

            logger.info(f"🔍 Detectando tipo de documento...")

            # Aquí se usa Patterns #

            doc_type = detect_document_type(full_text, pdf_file.name)
            logger.info(f"🏷️ Tipo detectado: {doc_type}")

            logger.info(f"✂️ Creando chunks adaptativos...")
            documents = create_adaptive_chunks(
                full_text, doc_type, pdf_file.name, filehash
            )
            logger.info(f"📦 Chunks creados: {len(documents)} chunks")

            ids = [f"{filehash}-{i}" for i in range(len(documents))]

            logger.info(f"🗄️ Indexando documentos en vectorstore...")
            if st.session_state.vectorstore is None:
                logger.info(
                    f"🆕 Creando nueva colección: {st.session_state.collection_name}")
                st.session_state.vectorstore = Chroma.from_documents(
                    documents,
                    embedding=st.session_state.embeddings,
                    collection_name=st.session_state.collection_name,
                    persist_directory=(CHROMA_PERSIST_DIR or None),
                    ids=ids
                )
                logger.info(f"✅ Colección creada exitosamente")
            else:
                logger.info(f"➕ Agregando documentos a colección existente")
                st.session_state.vectorstore.add_documents(documents, ids=ids)
                logger.info(f"✅ Documentos agregados a la colección")

            st.session_state.doc_ids_by_filehash[filehash] = ids
            st.session_state.pdf_chunks.extend(documents)

            logger.info(f"🤖 Generando resumen con IA...")
            summary_start = time.time()

            progress_text = f"Generando resumen para {pdf_file.name}..."
            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner(progress_text):
                try:
                    for i in range(5):
                        progress_bar.progress((i + 1) * 20)
                        status_text.text(f"Procesando... {20 * (i + 1)}%")
                        time.sleep(0.1)

                    summary = create_smart_summary(
                        full_text, doc_type, pdf_file.name)

                    summary_time = time.time() - summary_start
                    logger.info(f"✅ Resumen generado en {summary_time:.2f}s")

                    progress_bar.progress(100)
                    status_text.text("✅ Resumen completado!")

                except Exception as e:
                    logger.error(f"❌ Error generando resumen: {e}")
                    st.error(f"Error generando resumen: {e}")
                    summary = f"Error al procesar el resumen: {str(e)}"

                finally:
                    time.sleep(2)
                    progress_bar.empty()
                    status_text.empty()

            label = unique_label(
                pdf_file.name, existing_labels, suffix=filehash[:6])
            existing_labels.add(label)

            total_time = time.time() - start_time
            logger.info(
                f"🎉 Procesamiento completado: {pdf_file.name} en {total_time:.2f}s")

            st.session_state.processed_hashes.add(filehash)
            st.session_state.summaries.append({
                "label": label,
                "filename": pdf_file.name,
                "filehash": filehash,
                "summary": summary
            })

        except Exception as e:
            st.error(f"No se pudo procesar {pdf_file.name}: {e}")

# ===========================
# Interfaz principal
# ===========================

if st.session_state.summaries:
    st.subheader("🤖 Resúmenes Inteligentes")
    labels = [item["label"] for item in st.session_state.summaries]
    tabs = st.tabs(labels)
    for tab, item in zip(tabs, st.session_state.summaries):
        with tab:
            st.markdown(f"### 📄 {item['filename']}")
            st.markdown(item["summary"])

st.markdown("---")
st.subheader("💬 Chat con el Copiloto")

# Mostrar mensajes existentes del chat
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mostrar mensaje de bienvenida si no hay PDFs
if not st.session_state.pdf_chunks:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 ¡Hola! Sube algunos PDFs para poder ayudarte a responder preguntas sobre tu contenido.")
    st.warning(
        "⚠️ **No puedes hacer preguntas aún** - Primero debes subir al menos un archivo PDF en la barra lateral.")
    st.info("""
    **📋 Pasos para comenzar:**
    1. Sube 1-5 archivos PDF en la barra lateral
    2. Espera a que se procesen los documentos
    3. ¡Listo! Ya podrás hacer preguntas sobre tu contenido
    """)
    st.chat_input(
        "🚫 Sube PDFs primero para habilitar el chat", disabled=True, key="disabled_chat")
else:
    if prompt := st.chat_input("¡Hola! Pregúntame cualquier cosa sobre tu PDF.", key="active_chat"):
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            chat_start = time.time()
            logger.info(
                f"💬 Procesando pregunta del chat: {prompt[:50]}...")

            with st.spinner("🤔 Pensando..."):
                logger.info(f"🔍 Buscando chunks relevantes...")
                relevant_chunks = st.session_state.vectorstore.similarity_search(
                    prompt, k=5)
                logger.info(
                    f"📚 Chunks encontrados: {len(relevant_chunks)}")

                final_prompt = build_chat_prompt(prompt, relevant_chunks)
                logger.info(f"🤖 Generando respuesta con IA...")
                response = llm.invoke(final_prompt)
                chat_time = time.time() - chat_start
                logger.info(f"✅ Respuesta generada en {chat_time:.2f}s")
                st.markdown(response)

                with st.expander("🔍 Ver contexto usado para esta respuesta"):
                    for i, chunk in enumerate(relevant_chunks, 1):
                        md = chunk.metadata
                        st.markdown(
                            f"**Chunk {i}** - Fuente: {md.get('source', 'N/A')}")
                        st.markdown(
                            f"*Tipo: {md.get('doc_type', 'N/A')} | Tamaño: {md.get('chunk_size', 'N/A')} chars*")
                        st.text(chunk.page_content)
                        if i < len(relevant_chunks):
                            st.divider()

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response})
