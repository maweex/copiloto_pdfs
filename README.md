<h1>📄 Copiloto Conversacional sobre PDFs</h1>
<p>Aplicación de <strong>Streamlit</strong> que procesa PDFs y permite hacer preguntas sobre su contenido usando <strong>IA local con Ollama</strong> y <strong>RAG</strong> (Retrieval-Augmented Generation), ejecutada íntegramente con <strong>Docker</strong> y <strong>Docker Compose</strong>.</p>

<h2>🚀 Características</h2>
<ul>
  <li><strong>Procesamiento de PDFs</strong>: extracción de texto y chunking</li>
  <li><strong>IA local</strong>: modelo <code>llama3:8b</code> servido por Ollama</li>
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
<pre><code>git clone &lt;tu-repositorio&gt;
cd copiloto_pdfs
</code></pre>

<h3>2) Construir las imágenes</h3>
<pre><code>docker compose build
</code></pre>
<p><em>Nota:</em> La primera vez puede demorar porque se instalan todas las dependencias dentro de la imagen. Las siguientes veces será mucho más rápido gracias a la caché de Docker.</p>

<h3>3) Levantar servicios</h3>
<pre><code>docker compose up -d
</code></pre>
<p>Esto levanta dos contenedores:</p>
<ul>
  <li><code>ollama</code>: servidor del modelo (puerto 11434 interno)</li>
  <li><code>app</code>: aplicación Streamlit (expuesta en <code>http://localhost:8501</code>)</li>
</ul>

<h3>4) Descargar el modelo (solo primera vez)</h3>
<pre><code>docker compose exec ollama ollama pull llama3:8b
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
    <pre><code>docker compose exec ollama ollama run llama3:8b "Hola, ¿cómo estás?"
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

<h2>❓Preguntas frecuentes</h2>
<ul>
  <li><strong>¿Por qué tarda tanto la primera vez?</strong><br>
    Porque Docker construye la imagen (instala dependencias) y Ollama descarga el modelo <code>llama3:8b</code>. Después de esa primera preparación, los arranques siguientes usan la caché y son mucho más rápidos.</li>
  <li><strong>¿Necesito Python/venv en mi máquina?</strong><br>
    No. Todo corre dentro de los contenedores.</li>
  <li><strong>¿Cómo actualizo el código?</strong><br>
    Cambia tus archivos y luego:
    <pre><code>docker compose build app
docker compose up -d
</code></pre>
  </li>
</ul>

<h2>📚 Tecnologías</h2>
<ul>
  <li><strong>Streamlit</strong> — interfaz web</li>
  <li><strong>LangChain</strong> — orquestación de LLM + RAG</li>
  <li><strong>ChromaDB</strong> — vector store</li>
  <li><strong>Sentence Transformers</strong> — embeddings</li>
  <li><strong>Ollama</strong> — LLM local (modelo <code>llama3:8b</code>)</li>
  <li><strong>Docker &amp; Docker Compose</strong> — despliegue y orquestación</li>
</ul>

<h3>🎯 Justificación de la Stack Tecnológica</h3>
<ul>
  <li><strong>Streamlit</strong> — Front-end ideal para prototipos de IA, desarrollo "rápido" y recomendado para proyectos con IA.</li>
  <li><strong>LangChain</strong> — Framework estándar para RAG con integración con Ollama</li>
  <li><strong>ChromaDB</strong> — Vector store ligero y eficiente para aplicaciones locales</li>
  <li><strong>Sentence Transformers</strong> — Embeddings de alta calidad en español/inglés, optimizados para RAG</li>
  <li><strong>Ollama</strong> — LLM local sin dependencias externas, escogí el modelo llama3:8b por el balance calidad/velocidad</li>
  <li><strong>Docker</strong> — Para reproducir el entorno en otras máquinas.</li>
</ul>
