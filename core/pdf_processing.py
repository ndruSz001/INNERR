# Migración de la clase DocumentProcessor y funciones desde document_processor.py
import os
import json
import logging
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


logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("core.pdf_processing")

# --- PDF Processing Utilities ---
def procesar_pdf(
	pdf_path: str,
	categoria: str = "general",
	extraer_imagenes: bool = True,
	extraer_tablas: bool = True,
	images_dir: Optional[Path] = None
) -> Dict:
	"""
	Process a PDF file extracting text, images, tables, and metadata.

	Args:
		pdf_path (str): Path to the PDF file.
		categoria (str): Document category (e.g., paper, manual, report).
		extraer_imagenes (bool): Whether to extract images from the PDF.
		extraer_tablas (bool): Whether to extract tables from the PDF.
		images_dir (Optional[Path]): Directory to save extracted images.

	Returns:
		Dict: Dictionary with extracted information, including:
			- nombre_archivo: Filename
			- ruta_original: Original path
			- categoria: Category
			- fecha_procesado: Processing date
			- paginas: List of page info
			- metadatos: Metadata
			- texto_completo: Full text
			- imagenes_extraidas: List of image paths
			- tablas: List of tables
			- estadisticas: Stats (words, chars, tables, images)
			- error: Error message (if any)
	"""
	if not PDF_AVAILABLE:
		logger.error("pdfplumber no instalado")
		return {"error": "pdfplumber no instalado"}
	pdf_path_obj = Path(pdf_path)
	if not pdf_path_obj.exists():
		logger.error(f"Archivo PDF no encontrado: {pdf_path}")
		return {"error": f"Archivo no encontrado: {pdf_path}"}
	resultado = {
		"nombre_archivo": pdf_path_obj.name,
		"ruta_original": str(pdf_path_obj),
		"categoria": categoria,
		"fecha_procesado": datetime.now().isoformat(),
		"paginas": [],
		"metadatos": {},
		"texto_completo": "",
		"imagenes_extraidas": [],
		"tablas": [],
		"estadisticas": {}
	}
	try:
		with pdfplumber.open(pdf_path_obj) as pdf:
			resultado["metadatos"] = {
				"num_paginas": len(pdf.pages),
				"info": pdf.metadata if pdf.metadata else {}
			}
			texto_total = []
			for i, page in enumerate(pdf.pages, 1):
				pagina_info = {
					"numero": i,
					"texto": "",
					"tablas": [],
					"tiene_imagenes": False
				}
				texto = page.extract_text()
				if texto:
					pagina_info["texto"] = texto
					texto_total.append(texto)
				if extraer_tablas:
					tablas = page.extract_tables()
					if tablas:
						pagina_info["tablas"] = tablas
						resultado["tablas"].extend([
							{"pagina": i, "tabla": tabla} for tabla in tablas
						])
				resultado["paginas"].append(pagina_info)
			resultado["texto_completo"] = "\n\n".join(texto_total)
			if extraer_imagenes and PDF2IMAGE_AVAILABLE and images_dir:
				imagenes = extraer_imagenes_pdf(pdf_path_obj, images_dir)
				resultado["imagenes_extraidas"] = imagenes
			resultado["estadisticas"] = {
				"total_palabras": len(resultado["texto_completo"].split()),
				"total_caracteres": len(resultado["texto_completo"]),
				"total_tablas": len(resultado["tablas"]),
				"total_imagenes": len(resultado["imagenes_extraidas"])
			}
	except Exception as e:
		logger.exception(f"Error procesando PDF: {pdf_path}")
		resultado["error"] = str(e)
	return resultado

def extraer_imagenes_pdf(pdf_path: Path, images_dir: Path) -> List[str]:
	"""
	Extract images from a PDF file and save them as PNG files.

	Args:
		pdf_path (Path): Path to the PDF file.
		images_dir (Path): Directory to save extracted images.

	Returns:
		List[str]: List of paths to saved images.
	"""
	imagenes_extraidas = []
	try:
		imagenes = convert_from_path(str(pdf_path), dpi=150)
		base_name = pdf_path.stem
		for i, img in enumerate(imagenes, 1):
			img_path = images_dir / f"{base_name}_pagina_{i}.png"
			img.save(img_path, 'PNG')
			imagenes_extraidas.append(str(img_path))
	except Exception as e:
		logger.exception(f"Error extrayendo imágenes de PDF: {pdf_path}")
	return imagenes_extraidas

def procesar_imagen(imagen_path: str, descripcion: str = "") -> Dict:
	"""
	Process a single image (diagram, photo, etc.) and extract basic info.

	Args:
		imagen_path (str): Path to the image file.
		descripcion (str): Optional description.

	Returns:
		Dict: Dictionary with image information, including:
			- nombre: Filename
			- ruta: Path
			- descripcion: Description
			- dimensiones: Size (width, height)
			- formato: Format (e.g., PNG, JPG)
			- modo: Color mode
			- fecha_procesado: Processing date
			- error: Error message (if any)
	"""
	if not IMAGE_AVAILABLE:
		logger.error("PIL no instalado")
		return {"error": "PIL no instalado"}
	imagen_path_obj = Path(imagen_path)
	if not imagen_path_obj.exists():
		logger.error(f"Imagen no encontrada: {imagen_path}")
		return {"error": f"Imagen no encontrada: {imagen_path}"}
	try:
		img = Image.open(imagen_path_obj)
		resultado = {
			"nombre": imagen_path_obj.name,
			"ruta": str(imagen_path_obj),
			"descripcion": descripcion,
			"dimensiones": img.size,
			"formato": img.format,
			"modo": img.mode,
			"fecha_procesado": datetime.now().isoformat()
		}
		return resultado
	except Exception as e:
		logger.exception(f"Error procesando imagen: {imagen_path}")
		return {"error": str(e)}
