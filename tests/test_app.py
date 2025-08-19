from patterns import detect_document_type, get_document_patterns
from prompts import build_summary_prompt, build_chat_prompt
import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPatterns(unittest.TestCase):

    def test_get_document_patterns(self):
        patterns = get_document_patterns()
        expected_types = [
            'guion_pelicula', 'articulo_academico', 'informe_tecnico',
            'curriculum_vitae', 'manual_instrucciones', 'brochure_educativo',
            'brochure_servicios'
        ]
        for doc_type in expected_types:
            self.assertIn(doc_type, patterns)
            self.assertIsInstance(patterns[doc_type], list)
            self.assertGreater(len(patterns[doc_type]), 0)

    def test_detect_document_type_guion(self):
        text = """
        INT. CASA - NOCHE
        
        FADE IN:
        
        JUAN (V.O.)
        Esta es mi historia...
        
        CUT TO:
        """
        doc_type = detect_document_type(text, "script.pdf")
        self.assertEqual(doc_type, 'guion_pelicula')

    def test_detect_document_type_cv(self):
        text = """
        EXPERIENCIA LABORAL
        - Desarrollador Python (2020-2023)
        
        EDUCACIÓN
        - Ingeniería en Sistemas
        
        HABILIDADES
        - Python, JavaScript, SQL
        """
        doc_type = detect_document_type(text, "cv.pdf")
        self.assertEqual(doc_type, 'curriculum_vitae')

    def test_detect_document_type_brochure_educativo(self):
        text = """
        DIPLOMADO EN INTELIGENCIA ARTIFICIAL
        
        OBJETIVOS:
        - Aprender fundamentos de IA
        
        REQUISITOS:
        - Conocimientos básicos de programación
        
        DURACIÓN: 6 meses
        """
        doc_type = detect_document_type(text, "diplomado.pdf")
        self.assertEqual(doc_type, 'brochure_educativo')

    def test_detect_document_type_generico(self):
        text = "Este es un texto genérico sin patrones específicos."
        doc_type = detect_document_type(text, "generico.txt")
        self.assertEqual(doc_type, 'documento_generico')


class TestPrompts(unittest.TestCase):

    def test_build_summary_prompt(self):
        text = "Este es un texto de prueba para el resumen."
        doc_type = "articulo_academico"
        prompt = build_summary_prompt(text, doc_type)
        self.assertIn("Eres un experto en análisis de documentos", prompt)
        self.assertIn("Tipo de Documento", prompt)
        self.assertIn("Descripción General", prompt)
        self.assertIn("Palabras Clave", prompt)
        self.assertIn(text, prompt)

    def test_build_chat_prompt(self):
        user_query = "¿Cuáles son los requisitos?"
        relevant_chunks = [
            Mock(page_content="Contenido del chunk 1",
                 metadata={"source": "test.pdf"}),
            Mock(page_content="Contenido del chunk 2",
                 metadata={"source": "test.pdf"})
        ]
        prompt = build_chat_prompt(user_query, relevant_chunks)
        self.assertIn(user_query, prompt)
        self.assertIn("Eres un asistente experto", prompt)
        self.assertIn("Contenido del chunk 1", prompt)
        self.assertIn("Contenido del chunk 2", prompt)


class TestIntegration(unittest.TestCase):

    def test_patterns_and_prompts_integration(self):
        text = """
        DIPLOMADO EN PYTHON Y DATA SCIENCE
        
        OBJETIVOS:
        - Aprender Python avanzado
        - Dominar análisis de datos
        
        REQUISITOS:
        - Conocimientos básicos de programación
        
        DURACIÓN: 8 meses
        CRÉDITOS: 120
        """
        doc_type = detect_document_type(text, "diplomado.pdf")
        self.assertEqual(doc_type, 'brochure_educativo')
        prompt = build_summary_prompt(text, doc_type)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)


if __name__ == '__main__':
    unittest.main(verbosity=2)
