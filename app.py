import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.llms import Ollama
import os

st.title("Copiloto Conversacional sobre PDFs - Día 2 (Llama3) con Resumen y Tipo de Documento")

# Inicializar variables en session_state (solo durante la sesión actual)
if 'pdf_chunks' not in st.session_state:
    st.session_state.pdf_chunks = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
# Inicializar historial del chat
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Inicializar Llama3 local
llm = Ollama(model="llama3", temperature=0.1)

# Subida de PDFs
uploaded_files = st.file_uploader(
    "Sube hasta 5 PDFs", type="pdf", accept_multiple_files=True)

# Procesar solo archivos nuevos (no procesados anteriormente)
if uploaded_files:
    new_files = [
        f for f in uploaded_files if f.name not in st.session_state.processed_files]

    for pdf_file in new_files:
        st.subheader(f"Procesando: {pdf_file.name}")
        try:
            # Extraer texto
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"

            # Chunking
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(full_text)
            st.write(f"{len(chunks)} chunks generados del PDF {pdf_file.name}")

            # Agregar chunks a la sesión
            st.session_state.pdf_chunks.extend(chunks)
            st.session_state.processed_files.append(pdf_file.name)

            # --- Resumen automático con identificación de tipo ---
            summary_prompt = f'''Eres un asistente que analiza documentos y resume su contenido.
Primero identifica qué tipo de documento es (por ejemplo, curriculum vitae, informe técnico, artículo, etc.).
Luego, genera un resumen de un párrafo claro y conciso describiendo de qué trata el documento.

Texto del PDF:
{full_text}

Instrucciones de salida:
- Comienza indicando el tipo de documento.
- Luego, un resumen de una sola frase o párrafo.
- Todo en español.

Resumen:'''
            summary = llm(summary_prompt)
            st.subheader("Resumen del PDF:")
            st.write(summary)

        except Exception as e:
            st.error(f"No se pudo procesar {pdf_file.name}: {e}")

# Crear vector store solo en memoria (sin persistencia)
if st.session_state.pdf_chunks and st.session_state.vectorstore is None:
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # Crear vector store sin persist_directory para que sea temporal
    st.session_state.vectorstore = Chroma.from_texts(
        st.session_state.pdf_chunks,
        embedding=embeddings
    )
    st.success(
        "Chunks guardados en vector store temporal (solo durante esta sesión)")

# Mostrar archivos procesados
if st.session_state.processed_files:
    st.subheader("Archivos procesados en esta sesión:")
    for file_name in st.session_state.processed_files:
        st.write(f"• {file_name}")

# ===== INTERFAZ DE CHAT MODERNA =====
st.markdown("---")
st.subheader("💬 Chat con el Copiloto")

# Mostrar mensajes del historial del chat
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mostrar mensaje de bienvenida si no hay archivos procesados
if not st.session_state.pdf_chunks:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 ¡Hola! Soy tu copiloto conversacional. Sube algunos PDFs para poder ayudarte a responder preguntas sobre su contenido.")

    # Mostrar mensaje de bloqueo más visible
    st.warning(
        "⚠️ **No puedes hacer preguntas aún** - Primero debes subir al menos un archivo PDF en la sección superior.")

    # Mostrar ejemplo de lo que se puede hacer
    st.info("""
    **📋 Pasos para comenzar:**
    1. Sube 1-5 archivos PDF en la sección de arriba
    2. Espera a que se procesen los documentos
    3. ¡Listo! Ya podrás hacer preguntas sobre tu contenido
    """)

    # Chat input deshabilitado con mensaje explicativo
    st.chat_input("🚫 Sube PDFs primero para habilitar el chat", disabled=True)
else:
    # Input del chat habilitado solo cuando hay archivos
    if prompt := st.chat_input("¡Hola! Pregúntame cualquier cosa sobre tu PDF."):
        # Verificar que haya archivos procesados (doble verificación)
        if not st.session_state.pdf_chunks:
            with st.chat_message("assistant"):
                st.error(
                    "❌ Primero necesitas subir y procesar algunos PDFs para poder hacer preguntas.")
        else:
            # Agregar mensaje del usuario al historial
            st.session_state.chat_messages.append(
                {"role": "user", "content": prompt})

            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.markdown(prompt)

            # Mostrar mensaje del asistente con spinner
            with st.chat_message("assistant"):
                with st.spinner("🤔 Pensando..."):
                    # Buscar los chunks más relevantes
                    relevant_chunks = st.session_state.vectorstore.similarity_search(
                        prompt, k=3)  # top 3 chunks

                    # Construir prompt con citas y bullets
                    chat_prompt = f'''Eres un asistente que responde preguntas sobre documentos PDF. 
Usa SOLO la información en el CONTEXTO y cita la información indicando de qué chunk proviene.

Instrucciones:
- Responde en español.
- Usa bullets para cada afirmación.
- Si la información se repite en varios chunks, haz un resumen.
- Si no hay información suficiente, responde: "No se encontró evidencia en los documentos."

Pregunta: {prompt}

Contexto (chunks relevantes):
'''
                    for i, chunk in enumerate(relevant_chunks, 1):
                        chat_prompt += f"\nChunk {i}:\n{chunk.page_content}\n"

                    chat_prompt += "\nRespuesta:"

                    # Obtener respuesta del LLM
                    response = llm(chat_prompt)

                    # Mostrar la respuesta
                    st.markdown(response)

                    # Mostrar contexto usado (colapsable)
                    with st.expander("🔍 Ver contexto usado para esta respuesta"):
                        for i, chunk in enumerate(relevant_chunks, 1):
                            st.markdown(f"**Chunk {i}:**")
                            st.text(chunk.page_content)
                            if i < len(relevant_chunks):
                                st.divider()

            # Agregar respuesta del asistente al historial
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": response})

# Botón para limpiar el chat (opcional)
if st.session_state.chat_messages:
    if st.sidebar.button("🗑️ Limpiar Chat", type="secondary"):
        st.session_state.chat_messages = []
        st.rerun()
