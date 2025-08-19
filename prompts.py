# prompts.py
from textwrap import dedent
from typing import List


def build_summary_prompt(text: str, doc_type: str) -> str:
    """
    Devuelve el prompt de resumen optimizado para todos los tipos de documento.
    Recorta el texto a ~3000 chars para mantenerlo ágil.
    """
    text_head = (text or "")[:3000]

    # Prompt unificado y optimizado para todos los tipos
    head = """
    Eres un experto en análisis de documentos. Analiza este documento y proporciona SOLO:

    1. Tipo de Documento: [Especifica el tipo exacto]
    2. Descripción General: [Máximo 400 caracteres - explica brevemente de qué trata el documento]
    3. Palabras Clave: [5 palabras clave separadas por comas]

    IMPORTANTE:
    - La descripción debe ser clara y concisa
    - Máximo 400 caracteres en la descripción
    - Solo 5 palabras clave relevantes
    - Formato simple y directo
    """

    tail = f"""
    Texto del documento:
    {text_head}...

    Resumen optimizado:
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
    - Si no hay información suficiente, responde: "No se encontró evidencia en los documentos." a menos de que puedes inferir la información a partir de los chunks.
    - Mantén el contexto y la coherencia en tu respuesta.
    - Sé breve, y no seas redundante.

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
