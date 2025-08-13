import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
import os

st.set_page_config(page_title="Copiloto PDFs", layout="centered")

# CSS personalizado para controlar el ancho máximo
st.markdown("""
<style>
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        max-width: 100%;
    }
    .stFileUploader > div > div {
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Prototipo: Procesador de PDFs")
st.markdown(
    "Prototipo experimental para subir PDFs y procesar su contenido básico.")

# Carpeta de persistencia para Chroma
persist_dir = "./data/chroma"
os.makedirs(persist_dir, exist_ok=True)

# Subida de PDFs
uploaded_files = st.file_uploader(
    "Sube hasta 5 PDFs",
    type="pdf",
    accept_multiple_files=True
)

all_chunks = []

if uploaded_files:
    for pdf_file in uploaded_files:
        with st.expander(f"📁 Procesando: {pdf_file.name}", expanded=True):
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
                st.markdown(f"**Chunks generados:** {len(chunks)}")

                all_chunks.extend(chunks)

                # Mostrar información básica del PDF
                st.markdown("**Información del PDF:**")
                st.info(f"""
                - **Nombre del archivo**: {pdf_file.name}
                - **Páginas procesadas**: {len(reader.pages)}
                - **Texto extraído**: {len(full_text)} caracteres
                - **Chunks creados**: {len(chunks)}
                """)

            except Exception as e:
                st.error(f"No se pudo procesar {pdf_file.name}: {e}")

# Crear vector store básico
if all_chunks:
    try:
        embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_texts(
            all_chunks, embedding=embeddings, persist_directory=persist_dir)
        vectorstore.persist()
        st.success("✅ Chunks guardados en base de datos local (Chroma)")

        # Mostrar estadísticas básicas
        st.subheader("📊 Estadísticas del procesamiento")
        st.markdown(f"""
        - **Total de PDFs procesados**: {len(uploaded_files)}
        - **Total de chunks generados**: {len(all_chunks)}
        - **Base de datos**: ChromaDB local
        - **Estado**: Datos persistidos correctamente
        """)

    except Exception as e:
        st.error(f"Error al crear la base de datos: {e}")

# Información del prototipo
st.subheader("ℹ️ Información del Prototipo")
st.warning("""
**Este es un prototipo experimental con funcionalidad limitada:**

- ✅ Extrae texto de PDFs
- ✅ Divide texto en chunks
- ✅ Almacena datos localmente
- ❌ No incluye procesamiento inteligente
- ❌ No genera resúmenes automáticos
- ❌ No responde preguntas sobre el contenido

**Estado**: Prototipo básico en desarrollo
**Propósito**: Aprendizaje y experimentación
**No recomendado para uso en producción**
""")

# Footer
st.markdown("---")
st.markdown("*Prototipo experimental - Solo para desarrollo y aprendizaje*")
