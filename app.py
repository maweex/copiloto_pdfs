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

# Prompts externos
from prompts import build_summary_prompt, build_chat_prompt

st.title("Copiloto Conversacional para PDFs")

# ===========================
# Config persistencia Chroma
# ===========================
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "")

# ===========================
# Funciones de mantenimiento
# ===========================


def remove_file_by_hash(filehash: str):
    """Elimina TODO rastro del archivo identificado por 'filehash'."""
    # 1) Borrar del vectorstore por IDs o por metadatos
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

    # 2) Borrar de memoria: pdf_chunks
    st.session_state["pdf_chunks"] = [
        d for d in st.session_state.get("pdf_chunks", [])
        if d.metadata.get("filehash") != filehash
    ]

    # 3) Borrar de summaries
    st.session_state["summaries"] = [
        s for s in st.session_state.get("summaries", [])
        if s.get("filehash") != filehash
    ]

    # 4) Borrar índices auxiliares
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
    """Limpia claves principales de sesión y regenera IDs auxiliares."""
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
    """Equivalente al botón: limpia índice, memoria, colección y persistencia."""
    # 1) Eliminar uno a uno archivos del índice/memoria
    remove_all_files_one_by_one()

    # 2) Intentar borrar colección
    _delete_chroma_collection_if_possible()

    # 3) Si hay persistencia, borrar carpeta
    _delete_persist_dir_if_configured()

    # 4) Limpiar estado base / regenerar uploader
    _reset_core_state(regen_uploader=regen_uploader)


# ---------------------------
# Estado de sesión inicial
# ---------------------------
# Arranque "en limpio" al cargar una sesión nueva (tras refrescar la página)
if "_fresh_session_initialized" not in st.session_state:
    # Hace lo mismo que el botón Reiniciar sesión:
    _full_reset(regen_uploader=True)
    st.session_state["_fresh_session_initialized"] = True

# Asegurar llaves (por si el usuario modificó el orden del código)
if 'pdf_chunks' not in st.session_state:
    st.session_state.pdf_chunks = []           # lista de Document
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'processed_hashes' not in st.session_state:
    st.session_state.processed_hashes = set()  # hashes md5 ya procesados
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'summaries' not in st.session_state:
    # {label, filename, filehash, summary}
    st.session_state.summaries = []
if 'collection_name' not in st.session_state:
    st.session_state.collection_name = f"langchain-{uuid.uuid4().hex[:8]}"
if 'doc_ids_by_filehash' not in st.session_state:
    st.session_state.doc_ids_by_filehash = {}  # filehash -> [ids en Chroma]
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = f"uploader-{uuid.uuid4().hex[:6]}"

# ===========================
# SIDEBAR: Uploader + Reset
# ===========================
with st.sidebar:
    st.markdown("### 📥 Sube hasta 5 PDFs")
    uploaded_files = st.file_uploader(
        "Arrastra aquí tus archivos",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=st.session_state.uploader_key  # <- clave para poder resetear el widget
    )
    st.caption("Límite 200 MB por archivo · PDF")

    st.divider()

    if st.button("🔄 Reiniciar sesión", use_container_width=True):
        _full_reset(regen_uploader=True)
        st.rerun()

# ===========================
# Inicializar Llama3 local
# ===========================
ollama_base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")
llm = Ollama(model=ollama_model, temperature=0.1, base_url=ollama_base)


# ---------------------------
# Utilidades
# ---------------------------


def detect_document_type(text: str, filename: str) -> str:
    patterns = {
        'guion_pelicula': [
            r'\b(int\.|ext\.|int/|ext/|noche|día|night|day|morning|evening)\b',
            r'(fade in:|fade out\.|cut to:|dissolve to:|escena|scene|acto|act)',
            r'^[A-Z][A-Z0-9\s\-\'\.]{2,}$',
            r'\([^)]+\)',
            r'(screenplay|guion|script|dialogue|diálogo|personaje|voz en off|v\.o\.|o\.s\.)'
        ],
        'articulo_academico': [
            r'\b(abstract|resumen|introduction|introducción|conclusion|conclusión)\b',
            r'\b(references|bibliography|bibliografía|citation|cita)\b',
            r'\b(methodology|metodología|results|resultados|discussion|discusión)\b'
        ],
        'informe_tecnico': [
            r'\b(executive summary|resumen ejecutivo|technical|técnico)\b',
            r'\b(specifications|especificaciones|requirements|requisitos)\b',
            r'\b(implementation|implementación|deployment|despliegue)\b'
        ],
        'curriculum_vitae': [
            r'\b(experience|experiencia|education|educación|skills|habilidades)\b',
            r'\b(work history|historial laboral|professional|profesional)\b',
            r'\b(resume|cv|curriculum|curriculum vitae)\b'
        ],
        'manual_instrucciones': [
            r'\b(step|paso|instruction|instrucción|procedure|procedimiento)\b',
            r'\b(how to|cómo|tutorial|guide|guía|manual)\b',
            r'\b(installation|instalación|setup|configuración)\b'
        ]
    }
    flags = re.IGNORECASE | re.MULTILINE
    scores = {}
    for doc_type, pattern_list in patterns.items():
        score = 0
        for pattern in pattern_list:
            score += len(re.findall(pattern, text, flags=flags))
        scores[doc_type] = score

    if scores:
        detected_type = max(scores, key=scores.get)
        if scores[detected_type] > 0:
            return detected_type

    filename_lower = filename.lower()
    if any(w in filename_lower for w in ['script', 'guion', 'screenplay']):
        return 'guion_pelicula'
    if any(w in filename_lower for w in ['cv', 'resume', 'curriculum']):
        return 'curriculum_vitae'
    if any(w in filename_lower for w in ['manual', 'guide', 'tutorial']):
        return 'manual_instrucciones'
    if any(w in filename_lower for w in ['paper', 'article', 'research']):
        return 'articulo_academico'
    return 'documento_general'


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
                    'filehash': filehash,          # <- para limpieza selectiva
                    'doc_type': doc_type,
                    'chunk_id': i,
                    'chunk_size': len(chunk),
                    'total_chunks': len(basic_chunks)
                }
            )
        )
    return documents


def create_smart_summary(text: str, doc_type: str, filename: str) -> str:
    prompt = build_summary_prompt(text, doc_type)
    return llm(prompt)


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


# ---------------------------
# Subida y procesamiento
# ---------------------------
with st.sidebar:
    # 'uploaded_files' ya fue definido arriba en el sidebar
    pass

if 'uploaded_files' not in locals():
    uploaded_files = None  # por seguridad

if uploaded_files:
    if st.session_state.embeddings is None:
        st.session_state.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

    # 0) Detectar archivos eliminados con la X (comparando hashes actuales vs procesados)
    current_hashes = set()
    for f in uploaded_files:
        fb = f.getvalue()
        current_hashes.add(hashlib.md5(fb).hexdigest())

    removed_hashes = st.session_state.processed_hashes - current_hashes
    for fh in list(removed_hashes):
        remove_file_by_hash(fh)

    # 1) Procesar nuevos
    existing_labels = {item['label'] for item in st.session_state.summaries}

    for pdf_file in uploaded_files:
        try:
            file_bytes = pdf_file.getvalue()
            filehash = hashlib.md5(file_bytes).hexdigest()

            if filehash in st.session_state.processed_hashes:
                continue  # ya indexado

            reader = PdfReader(io.BytesIO(file_bytes))
            full_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"

            doc_type = detect_document_type(full_text, pdf_file.name)
            documents = create_adaptive_chunks(
                full_text, doc_type, pdf_file.name, filehash
            )

            # IDs por chunk para poder borrarlos después
            ids = [f"{filehash}-{i}" for i in range(len(documents))]

            if st.session_state.vectorstore is None:
                st.session_state.vectorstore = Chroma.from_documents(
                    documents,
                    embedding=st.session_state.embeddings,
                    collection_name=st.session_state.collection_name,
                    persist_directory=(CHROMA_PERSIST_DIR or None),
                    ids=ids
                )
            else:
                st.session_state.vectorstore.add_documents(documents, ids=ids)
                # Si usas persistencia, puedes activar el persist aquí:
                # if CHROMA_PERSIST_DIR:
                #     st.session_state.vectorstore.persist()

            # Registrar IDs del archivo
            st.session_state.doc_ids_by_filehash[filehash] = ids

            # Guardar en memoria
            st.session_state.pdf_chunks.extend(documents)

            # Resumen
            with st.spinner(f"Generando resumen para {pdf_file.name}..."):
                summary = create_smart_summary(
                    full_text, doc_type, pdf_file.name)

            # Pestañas
            label = unique_label(
                pdf_file.name, existing_labels, suffix=filehash[:6])
            existing_labels.add(label)

            # Registrar
            st.session_state.processed_hashes.add(filehash)
            st.session_state.summaries.append({
                "label": label,
                "filename": pdf_file.name,
                "filehash": filehash,
                "summary": summary
            })

        except Exception as e:
            st.error(f"No se pudo procesar {pdf_file.name}: {e}")

# ---------------------------
# Mostrar pestañas de resúmenes
# ---------------------------
if st.session_state.summaries:
    st.subheader("🤖 Resúmenes Inteligentes")
    labels = [item["label"] for item in st.session_state.summaries]
    tabs = st.tabs(labels)
    for tab, item in zip(tabs, st.session_state.summaries):
        with tab:
            st.markdown(f"### 📄 {item['filename']}")
            st.markdown(item["summary"])

# ---------------------------
# Interfaz de chat
# ---------------------------
st.markdown("---")
st.subheader("💬 Chat con el Copiloto")

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.pdf_chunks:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 ¡Hola! Sube algunos PDFs para poder ayudarte a responder preguntas sobre su contenido.")
    st.warning(
        "⚠️ **No puedes hacer preguntas aún** - Primero debes subir al menos un archivo PDF en la barra lateral.")
    st.info("""
    **📋 Pasos para comenzar:**
    1. Sube 1-5 archivos PDF en la barra lateral
    2. Espera a que se procesen los documentos
    3. ¡Listo! Ya podrás hacer preguntas sobre tu contenido
    """)
    st.chat_input("🚫 Sube PDFs primero para habilitar el chat", disabled=True)
else:
    if prompt := st.chat_input("¡Hola! Pregúntame cualquier cosa sobre tu PDF."):
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando..."):
                relevant_chunks = st.session_state.vectorstore.similarity_search(
                    prompt, k=5)

                final_prompt = build_chat_prompt(prompt, relevant_chunks)
                response = llm(final_prompt)
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
