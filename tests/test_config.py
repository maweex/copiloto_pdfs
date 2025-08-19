import os
import sys


def setup_test_environment():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    os.environ['OLLAMA_MODEL'] = 'llama3:8b'
    os.environ['CHROMA_PERSIST_DIR'] = ''


SAMPLE_TEXTS = {
    'guion_pelicula': """
    INT. OFICINA - DÍA
    
    FADE IN:
    
    JUAN (V.O.)
    La historia comienza aquí...
    
    CUT TO:
    
    INT. CASA - NOCHE
    
    MARÍA
    ¿Qué pasó?
    """,

    'curriculum_vitae': """
    MAURICIO ARRIETA
    
    EXPERIENCIA LABORAL
    - Desarrollador Python (2020-2023)
    - Analista de Datos (2018-2020)
    
    EDUCACIÓN
    - Ingeniería en Sistemas
    
    HABILIDADES
    - Python, JavaScript, SQL
    - Machine Learning, Data Analysis
    """,

    'brochure_educativo': """
    DIPLOMADO EN INTELIGENCIA ARTIFICIAL
    
    OBJETIVOS:
    - Aprender fundamentos de IA
    - Desarrollar proyectos prácticos
    
    REQUISITOS:
    - Conocimientos básicos de programación
    - Inglés intermedio
    
    DURACIÓN: 6 meses
    CRÉDITOS: 120
    INVERSIÓN: $2,500
    """
}

setup_test_environment()
