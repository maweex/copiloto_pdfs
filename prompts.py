# prompts.py
from textwrap import dedent
from typing import List


def build_summary_prompt(text: str, doc_type: str) -> str:
    """
    Devuelve el prompt de resumen según el tipo de documento.
    Recorta el texto a ~3000 chars para mantenerlo ágil.
    """
    text_head = (text or "")[:3000]

    if doc_type == 'guion_pelicula':
        head = """
        Eres un experto en análisis de guiones cinematográficos. 
        Analiza este guion y proporciona:

        1. Tipo de documento: Guion cinematográfico
        2. Título/Historia
        3. Género
        4. Resumen de trama (2–3 oraciones)
        5. Personajes principales (3–4)
        6. Estructura (escenas/actos)
        """
    elif doc_type == 'articulo_academico':
        head = """
        Eres un experto en análisis de artículos académicos.
        Analiza este artículo y proporciona:

        1. Tipo de documento: Artículo académico
        2. Título
        3. Área de estudio
        4. Objetivo
        5. Metodología
        6. Hallazgos clave (2–3)
        """
    elif doc_type == 'curriculum_vitae':
        head = """
        Eres un experto en análisis de currículos.
        Analiza este CV y proporciona:

        1. Tipo de documento: Curriculum Vitae
        2. Profesión principal
        3. Años de experiencia
        4. Educación (nivel más alto)
        5. Habilidades clave (3–4)
        6. Perfil profesional (1–2 oraciones)
        """
    else:
        head = """
        Eres un asistente que analiza documentos.
        Analiza este documento y proporciona:

        1. Tipo de documento
        2. Propósito
        3. Contenido principal
        4. Estructura
        5. Audiencia objetivo
        """

    tail = f"""
    Texto del documento:
    {text_head}...

    Resumen estructurado:
    """

    return dedent(head).strip() + "\n\n" + dedent(tail).strip()


def build_chat_prompt(user_query: str, relevant_chunks: List) -> str:
    """
    Construye el prompt del chat a partir de la consulta del usuario
    y una lista de 'relevant_chunks' (Document de LangChain).
    """
    head = f"""
    Eres un asistente experto que responde preguntas sobre documentos PDF. 
    Usa SOLO la información en el CONTEXTO proporcionado.

    Instrucciones específicas:
    - Responde en español de manera clara y estructurada. Si en el documento hay palabras en inglés, debes responder todo en español y traducir las palabras.
    - Usa bullets para organizar la información.
    - Si la información se repite en varios chunks, haz un resumen coherente y humano.
    - Si no hay información suficiente, responde: "No se encontró evidencia en los documentos."
    - Mantén el contexto y la coherencia en tu respuesta.

    Pregunta del usuario: {user_query}

    Contexto (chunks relevantes encontrados):
    """.strip()

    blocks = []
    for i, chunk in enumerate(relevant_chunks, 1):
        md = getattr(chunk, "metadata", {}) or {}
        source = md.get("source", "N/A")
        cid = md.get("chunk_id", i)
        content = getattr(chunk, "page_content", "")
        blocks.append(
            f"--- CHUNK {i} [Fuente: {source} - Chunk {cid}] ---\n{content}")

    tail = """
    --- INSTRUCCIONES FINALES ---
    Basándote en el contexto anterior, responde la pregunta del usuario de manera clara, estructurada y simple.

    Respuesta:
    """.strip()

    return head + "\n\n" + "\n\n".join(blocks) + "\n\n" + tail
