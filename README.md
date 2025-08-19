<h1>📄 Copiloto Conversacional sobre PDFs</h1>
<p>Aplicación de <strong>Streamlit</strong> que procesa PDFs y permite hacer preguntas sobre su contenido usando <strong>IA local con Ollama</strong> y <strong>RAG</strong> (Retrieval-Augmented Generation), ejecutada íntegramente con <strong>Docker</strong> y <strong>Docker Compose</strong>.</p>

<h2>🚀 Características</h2>
<ul>
  <li><strong>Procesamiento de PDFs</strong>: extracción de texto y chunking</li>
  <li><strong>IA local</strong>: modelo <code>llama3:3b</code> servido por Ollama</li>
  <li><strong>RAG</strong>: búsqueda semántica con Chroma</li>
  <li><strong>Interfaz Web</strong>: app Streamlit en el puerto 8501</li>
  <li><strong>Contenerización</strong>: entorno reproducible con Docker</li>
</ul>

<h2>📋 Requisitos</h2>
<ul>
  <li><strong>Docker</strong> (Docker Desktop en Windows/Mac o Docker Engine en Linux)</li>
  <li><strong>Docker Compose</strong></li>
</ul>

<h2>🛠️ Instalación y Ejecución (solo Docker)</h2>

<h3>1) Clonar el repositorio</h3>
<pre><code>git clone &lt;Link del repo&gt;
cd copiloto_pdfs
</code></pre>

<h3>2) Construir las imágenes</h3>
<pre><code>docker compose build
</code></pre>
<p><em>Nota:</em> La primera vez puede demorar porque se instalan todas las dependencias dentro de la imagen. Las siguientes veces será mucho más rápido gracias a la caché de Docker. Recomiendo tener la App de Docker abierta.</p>

<h3>3) Levantar servicios</h3>
<pre><code>docker compose up -d
</code></pre>
<p>Esto levanta dos contenedores:</p>
<ul>
  <li><code>ollama</code>: servidor del modelo (puerto 11434 interno)</li>
  <li><code>app</code>: aplicación Streamlit (expuesta en <code>http://localhost:8501</code>)</li>
</ul>

<h3>4) Descargar el modelo (solo primera vez)</h3>
<pre><code>docker compose exec ollama ollama pull llama3:3b
</code></pre>
<p><em>Importante:</em> La descarga del modelo puede tardar varios minutos la primera vez. Una vez descargado, quedará cacheado y los arranques posteriores serán mucho más rápidos.</p>

<h3>5) Abrir la aplicación</h3>
<pre><code>http://localhost:8501
</code></pre>

<h3>✔️ Comando único (levantar y abrir navegador)</h3>
<p><em>Linux:</em></p>
<pre><code>docker compose up -d &amp;&amp; xdg-open http://localhost:8501
</code></pre>
<p><em>macOS:</em></p>
<pre><code>docker compose up -d &amp;&amp; open http://localhost:8501
</code></pre>
<p><em>Windows (PowerShell):</em></p>
<pre><code>docker compose up -d; Start-Process "http://localhost:8501"
</code></pre>

<h2>🛑 Detener</h2>
<pre><code>docker compose down
</code></pre>
<p>Esto apaga y elimina los contenedores (no borra las imágenes). Si alguna vez quisieras limpiar volúmenes y datos cacheados, usa <code>docker compose down -v</code>.</p>

<h2>🧪 Pruebas rápidas</h2>
<ul>
  <li>Ver contenedores activos:
    <pre><code>docker compose ps
</code></pre>
  </li>
  <li>Probar el modelo desde el contenedor de Ollama:
    <pre><code>docker compose exec ollama ollama run llama3:3b "Hola, ¿cómo estás?"
</code></pre>
  </li>
</ul>

<h2>🪵 Logs</h2>
<pre><code>docker compose logs -f app
docker compose logs -f ollama
</code></pre>

<h2>📁 Estructura del proyecto</h2>
<pre><code>copiloto_pdfs/
├── app.py                 # Aplicación principal de Streamlit
├── requirements.txt       # Dependencias de Python (para la imagen)
├── Dockerfile             # Imagen de la app
├── docker-compose.yml     # Orquestación (app + ollama)
└── README.md              # Este archivo
</code></pre>

<h2>🏗️ Arquitectura del Sistema</h2>

<h3>Diagrama de Arquitectura</h3>
<pre><code>┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NAVEGADOR WEB                                │
│                    (localhost:8501)                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTAINER: APP                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 STREAMLIT APP                           │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │   INTERFAZ      │  │      PROCESAMIENTO          │  │   │
│  │  │   DE USUARIO    │  │         DE PDFs             │  │   │
│  │  │                 │  │                             │  │   │
│  │  │ • Upload PDF    │  │ • Extracción de texto       │  │   │
│  │  │ • Chat UI       │  │ • Chunking inteligente      │  │   │
│  │  │ • Historial     │  │ • Generación embeddings     │  │   │
│  │  └─────────────────┘  └─────────────────────────────┘  │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │              LANGCHAIN ORCHESTRATOR                 │  │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  │   RAG       │  │   CHAIN     │  │   OUTPUT    │  │   │
│  │  │  │  ENGINE     │  │  MANAGER    │  │  PROCESSOR  │  │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTAINER: OLLAMA                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 LLM SERVICE                             │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │              LLAMA3:3B MODEL                        │  │   │
│  │  │  • Procesamiento de consultas                       │  │   │
│  │  │  • Generación de respuestas                         │  │   │
│  │  │  • Contexto de conversación                         │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR STORE                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CHROMADB                             │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │   EMBEDDINGS    │  │      METADATA               │  │   │
│  │  │   STORAGE       │  │      STORAGE                 │  │   │
│  │  │                 │  │                             │  │   │
│  │  │ • Vector chunks │  │ • Información del PDF        │  │   │
│  │  │ • Similarity    │  │ • Timestamps                 │  │   │
│  │  │   search        │  │ • Chunk indices              │  │   │
│  │  └─────────────────┘  └─────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FLUJO DE DATOS │
│ │
│ 1. Usuario sube PDF → Streamlit │
│ 2. Streamlit → Procesamiento → Chunks + Embeddings │
│ 3. Embeddings → ChromaDB (Vector Store) │
│ 4. Usuario hace pregunta → Streamlit │
│ 5. Streamlit → RAG Engine → ChromaDB (búsqueda semántica) │
│ 6. RAG Engine → Ollama (LLM) con contexto │
│ 7. Ollama → Respuesta → Streamlit → Usuario │
└─────────────────────────────────────────────────────────────────┘
</code></pre>

<h3>Componentes Principales</h3>
<ul>
  <li><strong>Frontend (Streamlit)</strong>: Interfaz de usuario para upload y chat</li>
  <li><strong>Backend (Python)</strong>: Lógica de procesamiento y orquestación</li>
  <li><strong>LLM Service (Ollama)</strong>: Modelo de lenguaje local para generación de respuestas</li>
  <li><strong>Vector Database (ChromaDB)</strong>: Almacenamiento de embeddings para búsqueda semántica</li>
  <li><strong>RAG Engine (LangChain)</strong>: Orquestación del flujo de Retrieval-Augmented Generation</li>
</ul>

<h2>❓Preguntas frecuentes</h2>
<ul>
  <li><strong>¿Por qué tarda tanto la primera vez?</strong><br>
    Porque Docker construye la imagen (instala dependencias) y Ollama descarga el modelo <code>llama3:3b</code>. Después de esa primera preparación, los arranques siguientes usan la caché y son mucho más rápidos.</li>
  <li><strong>¿Necesito Python/venv en mi máquina?</strong><br>
    No. Todo corre dentro de los contenedores.</li>
  <li><strong>¿Cómo actualizo el código?</strong><br>
    Cambia tus archivos y luego:
    <pre><code>docker compose build app
docker compose up -d
</code></pre>
  </li>
  <li><strong>¿Por qué la app se demora tanto en enviar mensajes? </strong> <br> Es un problema común que noté al momento de dockerizar la aplicación. Puede ser que el modelo de lenguaje es muy lento o se demora haciendo la solicitud al llm.</li>
</ul>

<h2>📚 Tecnologías</h2>
<ul>
  <li><strong>Streamlit</strong> — interfaz web</li>
  <li><strong>LangChain</strong> — orquestación de LLM + RAG</li>
  <li><strong>ChromaDB</strong> — vector store</li>
  <li><strong>Sentence Transformers</strong> — embeddings</li>
  <li><strong>Ollama</strong> — LLM local (modelo <code>llama3:3b</code>)</li>
  <li><strong>Docker &amp; Docker Compose</strong> — despliegue y orquestación</li>
</ul>

<h3>🎯 Justificación de la Stack Tecnológica</h3>
<ul>
  <li><strong>Streamlit</strong> — Front-end ideal para prototipos de IA, desarrollo "rápido" y recomendado para proyectos con IA.</li>
  <li><strong>LangChain</strong> — Framework estándar para RAG con integración con Ollama</li>
  <li><strong>ChromaDB</strong> — Vector store ligero y eficiente para aplicaciones locales</li>
  <li><strong>Sentence Transformers</strong> — Embeddings de alta calidad en español/inglés, optimizados para RAG</li>
  <li><strong>Ollama</strong> — LLM local sin dependencias externas, escogí el modelo llama3:3b por el balance calidad/velocidad</li>
  <li><strong>Docker</strong> — Para reproducir el entorno en otras máquinas.</li>
</ul>

<h2>⚠️ Limitaciones Actuales</h2>
<ul>
  <li><strong>Interfaz Visual</strong>: La interfaz actual es funcional pero básica, necesita mejoras en diseño y UX para verse más profesional e intuitivo de usar.</li>
  <li><strong>Rendimiento</strong>: El procesamiento de PDFs y las respuestas del LLM pueden ser lentas, especialmente con archivos grandes.</li>
  <li><strong>Persistencia</strong>: No hay sistema de usuarios ni memoria de archivos procesados anteriormente</li>
  <li><strong>Seguridad</strong>: Falta implementar autenticación, autorización y validación de archivos</li>
  <li><strong>Escalabilidad</strong>: Limitado a un solo usuario por sesión.</li>
  <li><strong>Modelo LLM</strong>: El modelo llama3:3b es rápido (lo probé con el modelo estandar) pero puede tener limitaciones en calidad de respuestas complejas</li>
</ul>

<h2>🚀 Roadmap de Mejoras Futuras</h2>

<h3>🎨 Fase 1: Mejoras de Interfaz y UX</h3>
<ul>
  <li>Rediseño completo de la interfaz con componentes modernos y responsive</li>
  <li>Implementación de temas claro/oscuro</li>
  <li>Mejoras en la visualización de PDFs (zoom, navegación por páginas)</li>
  <li>Indicadores de progreso y feedback visual mejorado</li>
  <li>Historial de conversaciones en la misma sesión</li>
</ul>

<h3>⚡ Fase 2: Optimización de Rendimiento</h3>
<ul>
  <li>Probar otros modelos para evaluar rendimiento</li>
  <li>Implementación de procesamiento asíncrono de PDFs</li>
  <li>Optimización del chunking y embeddings para mayor velocidad</li>
  <li>Cache de embeddings para archivos procesados previamente</li>
  <li>Procesamiento en lotes para múltiples archivos</li>
  <li>Evaluación de modelos LLM más rápidos manteniendo calidad</li>
  <li>Implementación de framework de testing robusto (pytest, unittest) con tests unitarios, de integración y de rendimiento</li>
</ul>

<h3>👥 Fase 3: Sistema de Usuarios y Persistencia</h3>
<ul>
  <li>Sistema de autenticación y registro de usuarios</li>
  <li>Base de datos para almacenar historial de archivos y conversaciones</li>
  <li>Dashboard personalizado con estadísticas de uso</li>
  <li>Compartir archivos y conversaciones entre usuarios</li>
  <li>Sistema de favoritos y etiquetas para organizar contenido</li>
</ul>

<h3>🔒 Fase 4: Seguridad y Robustez</h3>
<ul>
  <li>Validación y sanitización de archivos PDF</li>
  <li>Rate limiting para prevenir abuso</li>
  <li>Encriptación de datos sensibles</li>
  <li>Auditoría de acceso y logs de seguridad</li>
</ul>

<h3>🌐 Fase 5: Funcionalidades Avanzadas</h3>
<ul>
  <li>Separación de backend y frontend para mejor escalabilidad y mantenimiento. Quizás usar FastAPI ya que se integra bien con proyectos de python.</li>
  <li>API REST para integración con otros sistemas</li>
  <li>Webhooks para notificaciones</li>
  <li>Integración con sistemas de almacenamiento en la nube</li>
  <li>Análisis avanzado de documentos (extracción de tablas, imágenes)</li>
  <li>Sistema de plugins para funcionalidades personalizables</li>
</ul>

<h3>📊 Fase 6: Monitoreo y Analytics</h3>
<ul>
  <li>Dashboard de métricas de rendimiento</li>
  <li>Análisis de uso y patrones de consulta</li>
  <li>Sistema de alertas para problemas de rendimiento</li>
  <li>Reportes automáticos de calidad de respuestas</li>
  <li>Integración con herramientas de observabilidad</li>
</ul>

<h2>🤝 Contribuciones</h2>
<p>¡Las contribuciones son bienvenidas! Puedes hacer Fork y aportar, Este es un prototipo por lo que puede que continúe este proyecto para un portafolio más robusto. Gracias por revisar mi proyecto :)</p>
