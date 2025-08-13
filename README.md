# 📄 Copiloto Conversacional sobre PDFs

**Prototipo** - Una app web simple para procesar PDFs y extraer texto.

## ✨ Qué hace

- Sube hasta 5 PDFs simultáneamente
- Extrae el texto de cada página
- Divide el contenido en chunks manejables
- Guarda todo localmente en una base de datos

## 🛠️ Tecnologías

- **Frontend**: Streamlit
- **PDFs**: PyPDF2
- **Procesamiento**: LangChain
- **Base de datos**: ChromaDB
- **Embeddings**: Sentence Transformers

## 🚀 Instalación

```bash
# Clonar y entrar al directorio
git clone <tu-repositorio>
cd copiloto_pdfs

# Entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Dependencias
pip install -r requirements.txt
```

## 🎯 Uso

```bash
streamlit run app.py
```

La app se abre en `localhost:8501`

## 📁 Estructura

```
copiloto_pdfs/
├── app.py              # App principal
├── requirements.txt    # Dependencias
└── data/              # Datos locales (ignorado por Git)
```

## 🤝 Contribuciones

Fork, rama, commit, PR. Es un proyecto casual, no hay drama.
