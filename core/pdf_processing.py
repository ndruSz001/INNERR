# Migración de la clase DocumentProcessor y funciones desde document_processor.py
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union
import re
from collections import Counter
import difflib

try:
	import pdfplumber
	PDF_AVAILABLE = True
except ImportError:
	PDF_AVAILABLE = False
	print("⚠️  pdfplumber no disponible. Instalar con: pip install pdfplumber")

try:
	from PIL import Image
	IMAGE_AVAILABLE = True
except ImportError:
	IMAGE_AVAILABLE = False

try:
	from pdf2image import convert_from_path
	PDF2IMAGE_AVAILABLE = True
except ImportError:
	PDF2IMAGE_AVAILABLE = False

try:
	import pytesseract
	import cv2
	import numpy as np
	OCR_AVAILABLE = True
except ImportError:
	OCR_AVAILABLE = False
	print("⚠️  OCR no disponible. Instalar: pip install pytesseract opencv-python")

try:
	import nltk
	from nltk.tokenize import sent_tokenize, word_tokenize
	from nltk.corpus import stopwords
	NLP_AVAILABLE = True
	# Descargar recursos necesarios (silenciosamente)
	try:
		nltk.data.find('tokenizers/punkt')
	except LookupError:
		print("📥 Descargando recursos de NLTK...")
		nltk.download('punkt', quiet=True)
		nltk.download('stopwords', quiet=True)
		nltk.download('averaged_perceptron_tagger', quiet=True)
except ImportError:
	NLP_AVAILABLE = False


class DocumentProcessor:
	"""
	Procesa documentos técnicos/científicos para alimentar a TARS
	- PDFs: Papers, manuales, reportes
	- Imágenes: Diagramas, gráficas, fotos
	- Texto: Notas, observaciones
	"""
	...existing code...

# Punto de entrada para ejecutar el procesador modular
def main():
	processor = DocumentProcessor()
	resumen = processor.generar_resumen_coleccion()
	print(f"\n📚 Documentos procesados: {resumen['total_documentos']}")
	if resumen['total_documentos'] > 0:
		print(f"📄 Total páginas: {resumen['total_paginas']}")
		print(f"📝 Total palabras: {resumen['total_palabras']:,}")
		print(f"\nCategorías:")
		for cat, count in resumen['categorias'].items():
			print(f"   - {cat}: {count}")
"""
Módulo: pdf_processing.py
Funciones y clases para extracción, búsqueda y resumen de PDFs.
Extraído de document_processor.py
"""

# Aquí irá DocumentProcessor y utilidades relacionadas a PDFs
