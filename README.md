# 📄 Copiloto Conversacional sobre PDFs

Una aplicación de Streamlit que permite procesar PDFs y hacer preguntas sobre su contenido usando IA local (Ollama) y RAG (Retrieval-Augmented Generation).

## 🚀 Características

- **Procesamiento de PDFs**: Extrae texto y crea chunks para análisis
- **IA Local**: Usa Ollama con el modelo llama3 para procesamiento local
- **RAG**: Sistema de búsqueda semántica para respuestas contextuales
- **Interfaz Web**: Aplicación Streamlit fácil de usar
- **Persistencia**: Almacena embeddings en Chroma DB local

## 📋 Requisitos Previos

- Python 3.8+
- Ollama instalado y configurado
- Modelo llama3 descargado

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd copiloto_pdfs
```

### 2. Crear y activar entorno virtual

#### Windows (PowerShell):

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# O usar el script automático
.\activate_venv.ps1
```

#### Windows (Command Prompt):

```cmd
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate.bat

# O usar el script automático
activate_venv.bat
```

#### Linux/Mac:

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Ollama

```bash
# Iniciar servicio Ollama
ollama serve

# Descargar modelo llama3
ollama pull llama3
```

## 🚀 Uso

### 1. Activar entorno virtual

```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Ejecutar la aplicación

```bash
streamlit run app.py
```

### 3. Usar la aplicación

1. Abre tu navegador en `http://localhost:8501`
2. Sube uno o más archivos PDF
3. Espera a que se procesen y generen resúmenes
4. Haz preguntas sobre el contenido de los PDFs

## 📁 Estructura del Proyecto

```
copiloto_pdfs/
├── app.py                 # Aplicación principal de Streamlit
├── requirements.txt       # Dependencias de Python
├── activate_venv.bat     # Script de activación para Windows CMD
├── activate_venv.ps1     # Script de activación para PowerShell
├── venv/                 # Entorno virtual (se crea automáticamente)
├── data/                 # Datos persistentes (se crea automáticamente)
│   └── chroma/          # Base de datos vectorial
└── README.md            # Este archivo
```

## 🔧 Solución de Problemas

### Error de conexión a Ollama

Si ves el error "HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded":

1. **Verifica que Ollama esté ejecutándose:**

   ```bash
   ollama serve
   ```

2. **Verifica que el modelo esté disponible:**

   ```bash
   ollama list
   ```

3. **Si no hay modelos, descarga uno:**
   ```bash
   ollama pull llama3
   ```

### Problemas con el entorno virtual

1. **Asegúrate de activar el entorno virtual antes de instalar dependencias:**

   ```bash
   .\venv\Scripts\Activate.ps1  # PowerShell
   # o
   venv\Scripts\activate.bat    # CMD
   ```

2. **Verifica que estés en el entorno virtual:**

   - Deberías ver `(venv)` al inicio de tu prompt

3. **Si hay problemas, recrea el entorno:**
   ```bash
   deactivate
   rmdir /s venv
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## 📚 Dependencias Principales

- **Streamlit**: Interfaz web
- **PyPDF2**: Procesamiento de PDFs
- **LangChain**: Framework para aplicaciones de IA
- **ChromaDB**: Base de datos vectorial
- **Sentence Transformers**: Embeddings de texto
- **Ollama**: LLM local

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas:

1. Verifica que Ollama esté ejecutándose
2. Asegúrate de estar en el entorno virtual
3. Revisa que todas las dependencias estén instaladas
4. Consulta los logs de error en la consola

---

**Nota**: Siempre activa el entorno virtual antes de trabajar en el proyecto:

```bash
.\venv\Scripts\Activate.ps1  # PowerShell
# o
venv\Scripts\activate.bat    # CMD
```
