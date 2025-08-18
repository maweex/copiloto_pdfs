📄 Copiloto Conversacional sobre PDFs

Una aplicación de Streamlit que permite procesar PDFs y hacer preguntas sobre su contenido usando IA local (Ollama) y RAG (Retrieval-Augmented Generation).

🚀 Características

Procesamiento de PDFs: Extrae texto y crea chunks para análisis

IA Local: Usa Ollama con el modelo llama3 para procesamiento local

RAG: Sistema de búsqueda semántica para respuestas contextuales

Interfaz Web: Aplicación Streamlit fácil de usar

Persistencia opcional: Almacena embeddings en Chroma DB local (puede deshabilitarse)

Contenerización: Ejecución con Docker y Docker Compose para un entorno reproducible

📋 Requisitos Previos
Opción A: Ejecución nativa

Python 3.8+

Ollama instalado y configurado

Modelo llama3 descargado

Opción B: Ejecución con Docker

Docker Desktop (Windows/Mac) o Docker Engine (Linux)

Docker Compose plugin

🛠️ Instalación

1. Clonar el repositorio
   git clone <tu-repositorio>
   cd copiloto_pdfs

🚀 Opción A: Ejecutar localmente con Python 2. Crear y activar entorno virtual

(ver instrucciones de Windows, Linux/Mac en el archivo original)

3. Instalar dependencias
   pip install -r requirements.txt

4. Configurar Ollama

# Iniciar servicio Ollama

ollama serve

# Descargar modelo llama3

ollama pull llama3

5. Ejecutar la aplicación
   streamlit run app.py

Abrir navegador en http://localhost:8501

🐳 Opción B: Ejecutar con Docker 2. Construir la imagen
docker compose build

3. Iniciar los contenedores
   docker compose up -d

Esto levanta:

ollama (servidor LLM local en el puerto 11434)

app (la aplicación Streamlit en el puerto 8501)

4. Abrir la aplicación
   http://localhost:8501

5. Detener la aplicación
   docker compose down

📁 Estructura del Proyecto
copiloto_pdfs/
├── app.py # Aplicación principal de Streamlit
├── requirements.txt # Dependencias de Python
├── Dockerfile # Imagen para la app
├── docker-compose.yml # Orquestación con Docker
├── activate_venv.bat # Script de activación (Windows CMD)
├── activate_venv.ps1 # Script de activación (PowerShell)
├── venv/ # Entorno virtual (local, no en Docker)
├── data/ # Datos persistentes (si se habilitan)
│ └── chroma/ # Base de datos vectorial
└── README.md # Este archivo

🔧 Solución de Problemas
Docker

Reconstruir la imagen después de cambios en dependencias:

docker compose build app
docker compose up -d

Ver logs en vivo:

docker compose logs -f app

Abrir y cerrar rápido la app con un solo comando (Linux/Mac):

docker compose up -d && xdg-open http://localhost:8501

En Windows (PowerShell):

docker compose up -d; Start-Process "http://localhost:8501"

Ollama

(conservar las notas de tu README original)

📚 Dependencias Principales

Streamlit: Interfaz web

PyPDF2: Procesamiento de PDFs

LangChain: Framework para aplicaciones de IA

ChromaDB: Base de datos vectorial

Sentence Transformers: Embeddings de texto

Ollama: LLM local

Docker + Docker Compose: Orquestación y despliegue

👉 ¿Quieres que además te prepare un snippet con comandos rápidos (copiloto-start y copiloto-stop) para que lo pongas en tu README y no tengas que memorizar docker compose up y down?
