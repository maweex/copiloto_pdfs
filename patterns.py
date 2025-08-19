import re


def get_document_patterns():
    return {
        'guion_pelicula': [
            r'\b(int\.|ext\.|int/|ext/|noche|día|night|day|morning|evening)\b',
            r'(fade in:|fade out\.|cut to:|dissolve to:|escena|scene|acto|act)',
            r'^[A-Z][A-Z0-9\s\-\'\.]{2,}$',
            r'\([^)]+\)',
            r'(screenplay|guion|script|dialogue|diálogo|personaje|voz en off|v\.o\.|o\.s\.)'
        ],
        'articulo_academico': [
            r'\b(abstract|resumen|introduction|introducción|conclusion|conclusión)\b',
            r'\b(references|bibliography|bibliografía|citation|cita)\b',
            r'\b(methodology|metodología|results|resultados|discussion|discusión)\b'
        ],
        'informe_tecnico': [
            r'\b(executive summary|resumen ejecutivo|technical|técnico)\b',
            r'\b(specifications|especificaciones|requirements|requisitos)\b',
            r'\b(implementation|implementación|deployment|despliegue)\b'
        ],
        'curriculum_vitae': [
            r'\b(experience|experiencia|education|educación|skills|habilidades)\b',
            r'\b(work history|historial laboral|professional|profesional)\b',
            r'\b(resume|cv|curriculum|curriculum vitae)\b'
        ],
        'manual_instrucciones': [
            r'\b(step|paso|instruction|instrucción|procedure|procedimiento)\b',
            r'\b(how to|cómo|tutorial|guide|guía|manual)\b',
            r'\b(installation|instalación|setup|configuración)\b'
        ],
        'brochure_educativo': [
            r'\b(diplomado|diploma|certificado|certificación|curso|programa)\b',
            r'\b(educación|educativo|académico|universidad|instituto|escuela|facultad)\b',
            r'\b(objetivos|competencias|habilidades|conocimientos|aprendizaje|formación)\b',
            r'\b(duración|horas|créditos|módulos|asignaturas|materias|semanas)\b',
            r'\b(inversión|precio|costo|matrícula|inscripción|becas|descuentos)\b',
            r'\b(profesores|docentes|instructores|facilitadores|expertos|especialistas)\b',
            r'\b(metodología|modalidad|presencial|online|híbrido|flexible|intensivo)\b',
            r'\b(requisitos|perfil|público|dirigido|participantes|estudiantes)\b',
            r'\b(plan de estudios|malla curricular|contenidos|temario|syllabus)\b',
            r'\b(acreditación|reconocimiento|validez|certificación|título)\b',
            r'\b(infraestructura|laboratorios|recursos|biblioteca|tecnología)\b',
            r'\b(convenios|partnerships|colaboraciones|redes|alianzas)\b'
        ],
        'brochure_servicios': [
            r'\b(servicios|servicio|soluciones|solucion|productos|producto)\b',
            r'\b(empresa|compañía|corporación|organización|institución|firma)\b',
            r'\b(experiencia|trayectoria|años|historia|misión|visión|valores)\b',
            r'\b(clientes|casos de éxito|testimonios|referencias|portfolio)\b',
            r'\b(contacto|teléfono|email|dirección|ubicación|horarios|atención)\b',
            r'\b(precios|tarifas|cotizaciones|presupuestos|ofertas|promociones)\b',
            r'\b(garantía|calidad|certificaciones|estándares|normas|iso)\b',
            r'\b(equipo|profesionales|consultores|asesores|especialistas)\b',
            r'\b(tecnología|innovación|metodologías|procesos|herramientas)\b',
            r'\b(cobertura|alcance|mercados|sectores|industrias)\b'
        ]
    }


def detect_document_type(text: str, filename: str) -> str:
    patterns = get_document_patterns()
    flags = re.IGNORECASE | re.MULTILINE
    scores = {}

    for doc_type, pattern_list in patterns.items():
        score = 0
        for pattern in pattern_list:
            score += len(re.findall(pattern, text, flags=flags))
        scores[doc_type] = score

    if scores:
        best_type = max(scores, key=scores.get)
        if scores[best_type] > 0:
            return best_type

    return 'documento_generico'
