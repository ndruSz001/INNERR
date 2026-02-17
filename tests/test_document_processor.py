"""
Pruebas unitarias para DocumentProcessor.
"""

import unittest
from processing.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def test_procesar_pdf(self):
        processor = DocumentProcessor()
        resultado = processor.procesar_pdf('test.pdf')
        self.assertIn('nombre_archivo', resultado)

if __name__ == '__main__':
    unittest.main()
