"""
Procesador de Documentos para TARS
Extrae información de PDFs, imágenes, texto para análisis rápido
Diferenciador: Ingesta local de papers científicos, manuales técnicos, resultados
"""

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
    
    def __init__(self, storage_dir="tars_lifelong/knowledge"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Directorio para documentos procesados
        self.docs_dir = self.storage_dir / "documents"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Directorio para imágenes extraídas
        self.images_dir = self.storage_dir / "extracted_images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Directorio para OCR de PDFs escaneados
        self.ocr_dir = self.storage_dir / "ocr_results"
        self.ocr_dir.mkdir(exist_ok=True)
        
        # Índice de documentos procesados
        self.index_file = self.storage_dir / "documents_index.json"
        self.index = self._load_index()
        
        # Cache de stopwords para NLP
        self.stopwords_es = set(stopwords.words('spanish')) if NLP_AVAILABLE else set()
        self.stopwords_en = set(stopwords.words('english')) if NLP_AVAILABLE else set()
    
    def _load_index(self) -> Dict:
        """Carga índice de documentos procesados"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documentos": [], "total": 0}
    
    def _save_index(self):
        """Guarda índice de documentos"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def procesar_pdf(self, pdf_path: str, categoria: str = "general",
                     extraer_imagenes: bool = True,
                     extraer_tablas: bool = True) -> Dict:
        """
        Procesa un PDF completo: texto, imágenes, tablas, metadatos
        
        Args:
            pdf_path: Ruta al archivo PDF
            categoria: Tipo de documento (paper, manual, reporte, etc.)
            extraer_imagenes: Si debe extraer imágenes del PDF
            extraer_tablas: Si debe extraer tablas
        
        Returns:
            Dict con toda la información extraída
        """
        if not PDF_AVAILABLE:
            return {"error": "pdfplumber no instalado"}
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"error": f"Archivo no encontrado: {pdf_path}"}
        
        print(f"\n📄 Procesando PDF: {pdf_path.name}")
        print("="*70)
        
        resultado = {
            "nombre_archivo": pdf_path.name,
            "ruta_original": str(pdf_path),
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
            with pdfplumber.open(pdf_path) as pdf:
                # Metadatos del PDF
                resultado["metadatos"] = {
                    "num_paginas": len(pdf.pages),
                    "info": pdf.metadata if pdf.metadata else {}
                }
                
                print(f"📊 Páginas: {len(pdf.pages)}")
                
                # Procesar cada página
                texto_total = []
                for i, page in enumerate(pdf.pages, 1):
                    print(f"   Procesando página {i}/{len(pdf.pages)}...", end='\r')
                    
                    pagina_info = {
                        "numero": i,
                        "texto": "",
                        "tablas": [],
                        "tiene_imagenes": False
                    }
                    
                    # Extraer texto
                    texto = page.extract_text()
                    if texto:
                        pagina_info["texto"] = texto
                        texto_total.append(texto)
                    
                    # Extraer tablas
                    if extraer_tablas:
                        tablas = page.extract_tables()
                        if tablas:
                            pagina_info["tablas"] = tablas
                            resultado["tablas"].extend([
                                {"pagina": i, "tabla": tabla}
                                for tabla in tablas
                            ])
                    
                    resultado["paginas"].append(pagina_info)
                
                resultado["texto_completo"] = "\n\n".join(texto_total)
                
                # Extraer imágenes si se solicita
                if extraer_imagenes and PDF2IMAGE_AVAILABLE:
                    print(f"\n🖼️  Extrayendo imágenes...")
                    imagenes = self._extraer_imagenes_pdf(pdf_path)
                    resultado["imagenes_extraidas"] = imagenes
                
                # Estadísticas
                resultado["estadisticas"] = {
                    "total_palabras": len(resultado["texto_completo"].split()),
                    "total_caracteres": len(resultado["texto_completo"]),
                    "total_tablas": len(resultado["tablas"]),
                    "total_imagenes": len(resultado["imagenes_extraidas"])
                }
                
                print(f"\n✅ Procesado completo:")
                print(f"   - {resultado['estadisticas']['total_palabras']} palabras")
                print(f"   - {resultado['estadisticas']['total_tablas']} tablas")
                print(f"   - {resultado['estadisticas']['total_imagenes']} imágenes")
                
                # Guardar documento procesado
                self._guardar_documento_procesado(resultado)
                
                # Actualizar índice
                self._actualizar_indice(resultado)
                
        except Exception as e:
            resultado["error"] = str(e)
            print(f"\n❌ Error procesando PDF: {e}")
        
        return resultado
    
    def _extraer_imagenes_pdf(self, pdf_path: Path) -> List[str]:
        """Extrae imágenes del PDF como archivos separados"""
        imagenes_extraidas = []
        
        try:
            # Convertir páginas a imágenes
            imagenes = convert_from_path(str(pdf_path), dpi=150)
            
            base_name = pdf_path.stem
            for i, img in enumerate(imagenes, 1):
                img_path = self.images_dir / f"{base_name}_pagina_{i}.png"
                img.save(img_path, 'PNG')
                imagenes_extraidas.append(str(img_path))
        
        except Exception as e:
            print(f"   ⚠️  Error extrayendo imágenes: {e}")
        
        return imagenes_extraidas
    
    def _guardar_documento_procesado(self, resultado: Dict):
        """Guarda el resultado del procesamiento como JSON"""
        nombre_archivo = Path(resultado["nombre_archivo"]).stem
        output_file = self.docs_dir / f"{nombre_archivo}_procesado.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        # También guardar texto plano para búsqueda rápida
        text_file = self.docs_dir / f"{nombre_archivo}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(resultado["texto_completo"])
    
    def _actualizar_indice(self, resultado: Dict):
        """Actualiza el índice con el nuevo documento"""
        self.index["documentos"].append({
            "nombre": resultado["nombre_archivo"],
            "categoria": resultado["categoria"],
            "fecha": resultado["fecha_procesado"],
            "palabras": resultado["estadisticas"]["total_palabras"],
            "paginas": resultado["metadatos"].get("num_paginas", 0)
        })
        self.index["total"] = len(self.index["documentos"])
        self._save_index()
    
    def buscar_en_documentos(self, query: str, categoria: Optional[str] = None) -> List[Dict]:
        """
        Busca texto en todos los documentos procesados
        
        Args:
            query: Texto a buscar
            categoria: Filtrar por categoría (opcional)
        
        Returns:
            Lista de resultados con contexto
        """
        resultados = []
        
        # Buscar en archivos de texto
        for doc_file in self.docs_dir.glob("*.txt"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Buscar query (case-insensitive)
                if re.search(query, contenido, re.IGNORECASE):
                    # Encontrar contexto (100 caracteres antes y después)
                    matches = list(re.finditer(query, contenido, re.IGNORECASE))
                    
                    for match in matches[:3]:  # Máximo 3 coincidencias por documento
                        start = max(0, match.start() - 100)
                        end = min(len(contenido), match.end() + 100)
                        contexto = contenido[start:end]
                        
                        resultados.append({
                            "documento": doc_file.stem.replace("_procesado", ""),
                            "contexto": f"...{contexto}...",
                            "posicion": match.start()
                        })
            
            except Exception as e:
                print(f"Error buscando en {doc_file}: {e}")
        
        return resultados
    
    def extraer_informacion_clave(self, texto: str, tipo: str = "paper") -> Dict:
        """
        Extrae información estructurada según el tipo de documento
        
        Args:
            texto: Texto del documento
            tipo: Tipo (paper, manual, reporte)
        
        Returns:
            Diccionario con información extraída
        """
        info = {
            "tipo": tipo,
            "secciones_detectadas": [],
            "referencias": [],
            "ecuaciones": [],
            "figuras_mencionadas": []
        }
        
        if tipo == "paper":
            # Detectar secciones típicas de papers
            secciones = ["abstract", "introduction", "methods", "results", 
                        "discussion", "conclusion", "references"]
            
            for seccion in secciones:
                if re.search(rf'\b{seccion}\b', texto, re.IGNORECASE):
                    info["secciones_detectadas"].append(seccion)
            
            # Buscar referencias a figuras
            figuras = re.findall(r'(?:Figure|Fig\.?)\s+(\d+)', texto, re.IGNORECASE)
            info["figuras_mencionadas"] = list(set(figuras))
            
            # Buscar referencias bibliográficas
            refs = re.findall(r'\[(\d+)\]', texto)
            info["referencias"] = list(set(refs))
        
        elif tipo == "manual":
            # Detectar pasos numerados
            pasos = re.findall(r'(?:Step|Paso)\s+(\d+)', texto, re.IGNORECASE)
            info["pasos_detectados"] = list(set(pasos))
        
        return info
    
    def listar_documentos(self, categoria: Optional[str] = None) -> List[Dict]:
        """Lista todos los documentos procesados"""
        docs = self.index.get("documentos", [])
        
        if categoria:
            docs = [d for d in docs if d.get("categoria") == categoria]
        
        return docs
    
    def procesar_imagen(self, imagen_path: str, descripcion: str = "") -> Dict:
        """
        Procesa una imagen individual (diagrama, foto, etc.)
        
        Args:
            imagen_path: Ruta a la imagen
            descripcion: Descripción opcional
        
        Returns:
            Información de la imagen
        """
        if not IMAGE_AVAILABLE:
            return {"error": "PIL no disponible"}
        
        imagen_path = Path(imagen_path)
        if not imagen_path.exists():
            return {"error": f"Imagen no encontrada: {imagen_path}"}
        
        try:
            img = Image.open(imagen_path)
            
            resultado = {
                "nombre": imagen_path.name,
                "ruta": str(imagen_path),
                "descripcion": descripcion,
                "dimensiones": img.size,
                "formato": img.format,
                "modo": img.mode,
                "fecha_procesado": datetime.now().isoformat()
            }
            
            print(f"🖼️  Imagen: {imagen_path.name}")
            print(f"   Dimensiones: {img.size[0]}x{img.size[1]} px")
            print(f"   Formato: {img.format}")
            
            return resultado
        
        except Exception as e:
            return {"error": str(e)}
    
    def generar_resumen_coleccion(self) -> Dict:
        """Genera resumen de todos los documentos procesados"""
        total_palabras = sum(d.get("palabras", 0) for d in self.index["documentos"])
        total_paginas = sum(d.get("paginas", 0) for d in self.index["documentos"])
        
        categorias = {}
        for doc in self.index["documentos"]:
            cat = doc.get("categoria", "general")
            categorias[cat] = categorias.get(cat, 0) + 1
        
        return {
            "total_documentos": self.index["total"],
            "total_palabras": total_palabras,
            "total_paginas": total_paginas,
            "categorias": categorias,
            "ultimo_procesado": self.index["documentos"][-1] if self.index["documentos"] else None
        }
    
    # ============================================================
    # FUNCIONALIDADES AVANZADAS
    # ============================================================
    
    def aplicar_ocr_a_pdf(self, pdf_path: str, idioma: str = "spa+eng") -> Dict:
        """
        Aplica OCR a un PDF escaneado (sin texto extraíble)
        Útil para papers antiguos, documentos escaneados, etc.
        
        Args:
            pdf_path: Ruta al PDF
            idioma: Idiomas para OCR ("spa", "eng", "spa+eng")
        
        Returns:
            Dict con texto extraído por OCR
        """
        if not OCR_AVAILABLE:
            return {"error": "OCR no disponible. Instalar pytesseract y opencv-python"}
        
        if not PDF2IMAGE_AVAILABLE:
            return {"error": "pdf2image no disponible"}
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"error": f"PDF no encontrado: {pdf_path}"}
        
        print(f"\n🔍 Aplicando OCR a: {pdf_path.name}")
        print(f"   Idioma(s): {idioma}")
        print("="*70)
        
        resultado = {
            "archivo": pdf_path.name,
            "idioma": idioma,
            "paginas_ocr": [],
            "texto_completo": "",
            "fecha": datetime.now().isoformat()
        }
        
        try:
            # Convertir PDF a imágenes
            imagenes = convert_from_path(str(pdf_path), dpi=300)  # Alta resolución para OCR
            
            texto_total = []
            
            for i, img in enumerate(imagenes, 1):
                print(f"   Procesando página {i}/{len(imagenes)} con OCR...", end='\r')
                
                # Convertir PIL Image a numpy array para OpenCV
                img_array = np.array(img)
                
                # Preprocesamiento para mejorar OCR
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Aplicar threshold para mejorar contraste
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Aplicar OCR
                texto = pytesseract.image_to_string(thresh, lang=idioma)
                
                resultado["paginas_ocr"].append({
                    "pagina": i,
                    "texto": texto,
                    "confianza": "alta"  # pytesseract puede dar confianza con image_to_data
                })
                
                texto_total.append(texto)
            
            resultado["texto_completo"] = "\n\n".join(texto_total)
            resultado["total_caracteres"] = len(resultado["texto_completo"])
            resultado["total_palabras"] = len(resultado["texto_completo"].split())
            
            print(f"\n✅ OCR completado:")
            print(f"   {len(imagenes)} páginas procesadas")
            print(f"   {resultado['total_palabras']:,} palabras extraídas")
            
            # Guardar resultado OCR
            ocr_file = self.ocr_dir / f"{pdf_path.stem}_ocr.json"
            with open(ocr_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            # También texto plano
            ocr_txt = self.ocr_dir / f"{pdf_path.stem}_ocr.txt"
            with open(ocr_txt, 'w', encoding='utf-8') as f:
                f.write(resultado["texto_completo"])
        
        except Exception as e:
            resultado["error"] = str(e)
            print(f"\n❌ Error en OCR: {e}")
        
        return resultado
    
    def extraer_metadatos_paper(self, texto: str) -> Dict:
        """
        Extrae metadatos estructurados de un paper científico
        - Título
        - Autores
        - Afiliaciones
        - DOI
        - Año
        - Abstract
        - Keywords
        """
        metadatos = {
            "titulo": None,
            "autores": [],
            "afiliaciones": [],
            "doi": None,
            "año": None,
            "abstract": None,
            "keywords": [],
            "journal": None
        }
        
        # Extraer DOI
        doi_match = re.search(r'\b(10\.\d{4,}/[^\s]+)', texto)
        if doi_match:
            metadatos["doi"] = doi_match.group(1)
        
        # Extraer año (buscar 4 dígitos que parezcan año)
        año_matches = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', texto[:2000])  # Primeras líneas
        if año_matches:
            metadatos["año"] = año_matches[0]
        
        # Extraer abstract (entre "Abstract" y siguiente sección)
        abstract_match = re.search(
            r'(?:abstract|resumen)\s*[:.]?\s*(.*?)(?:\n\s*(?:keywords|introduction|1\.|i\.))',
            texto[:5000],
            re.IGNORECASE | re.DOTALL
        )
        if abstract_match:
            metadatos["abstract"] = abstract_match.group(1).strip()[:1000]  # Máx 1000 chars
        
        # Extraer keywords
        keywords_match = re.search(
            r'(?:keywords|palabras clave)\s*[:.]?\s*(.*?)(?:\n\n|\n\s*\d)',
            texto[:5000],
            re.IGNORECASE
        )
        if keywords_match:
            keywords_text = keywords_match.group(1)
            # Separar por comas, puntos y coma, o saltos de línea
            keywords = re.split(r'[,;•\n]', keywords_text)
            metadatos["keywords"] = [k.strip() for k in keywords if k.strip()][:10]
        
        # Intentar extraer título (generalmente primeras líneas, en mayúsculas o negrita)
        lineas = texto.split('\n')
        for i, linea in enumerate(lineas[:20]):
            if len(linea.strip()) > 20 and len(linea.strip()) < 200:
                # Heurística: si tiene muchas mayúsculas, probablemente es título
                if linea.isupper() or (i < 5 and len(linea) > 30):
                    metadatos["titulo"] = linea.strip()
                    break
        
        return metadatos
    
    def generar_resumen_automatico(self, texto: str, num_oraciones: int = 5) -> str:
        """
        Genera resumen automático usando algoritmo extractivo simple
        Basado en frecuencia de palabras clave
        """
        if not NLP_AVAILABLE:
            # Fallback: primeras N oraciones
            oraciones = texto.split('.')[:num_oraciones]
            return '. '.join(oraciones) + '.'
        
        try:
            # Tokenizar en oraciones
            oraciones = sent_tokenize(texto[:10000])  # Primeros 10k caracteres
            
            if len(oraciones) <= num_oraciones:
                return texto
            
            # Tokenizar en palabras
            palabras = word_tokenize(texto.lower())
            
            # Filtrar stopwords
            palabras_filtradas = [
                p for p in palabras 
                if p.isalnum() and p not in self.stopwords_en and p not in self.stopwords_es
            ]
            
            # Calcular frecuencias
            frecuencias = Counter(palabras_filtradas)
            
            # Puntuar oraciones basadas en palabras importantes
            puntuacion_oraciones = {}
            for i, oracion in enumerate(oraciones):
                palabras_oracion = word_tokenize(oracion.lower())
                puntuacion = sum(frecuencias.get(p, 0) for p in palabras_oracion)
                puntuacion_oraciones[i] = puntuacion
            
            # Seleccionar top N oraciones (manteniendo orden original)
            top_indices = sorted(
                puntuacion_oraciones,
                key=puntuacion_oraciones.get,
                reverse=True
            )[:num_oraciones]
            
            top_indices_ordenados = sorted(top_indices)
            
            resumen = ' '.join(oraciones[i] for i in top_indices_ordenados)
            
            return resumen
        
        except Exception as e:
            print(f"⚠️ Error generando resumen: {e}")
            # Fallback
            oraciones = texto.split('.')[:num_oraciones]
            return '. '.join(oraciones) + '.'
    
    def extraer_referencias_bibliograficas(self, texto: str) -> List[Dict]:
        """
        Extrae referencias bibliográficas de un paper
        Detecta sección de referencias y parsea cada entrada
        """
        referencias = []
        
        # Buscar sección de referencias
        ref_match = re.search(
            r'(?:references|bibliograf[ií]a|bibliography)\s*\n(.*?)(?:\n\s*(?:appendix|ap[ée]ndice|$))',
            texto,
            re.IGNORECASE | re.DOTALL
        )
        
        if not ref_match:
            return referencias
        
        seccion_refs = ref_match.group(1)
        
        # Detectar referencias numeradas [1], [2], etc.
        refs_numeradas = re.findall(r'\[(\d+)\]\s*([^\[]+)', seccion_refs)
        
        for num, contenido in refs_numeradas[:50]:  # Máximo 50 referencias
            # Intentar extraer DOI de la referencia
            doi_match = re.search(r'10\.\d{4,}/[^\s]+', contenido)
            doi = doi_match.group(0) if doi_match else None
            
            # Intentar extraer año
            año_match = re.search(r'\((\d{4})\)', contenido)
            año = año_match.group(1) if año_match else None
            
            referencias.append({
                "numero": num,
                "texto": contenido.strip()[:300],  # Primeros 300 chars
                "doi": doi,
                "año": año
            })
        
        return referencias
    
    def comparar_documentos(self, doc1_path: str, doc2_path: str) -> Dict:
        """
        Compara dos documentos y encuentra similitudes/diferencias
        Útil para comparar versiones de papers, revisar cambios
        """
        doc1 = Path(doc1_path)
        doc2 = Path(doc2_path)
        
        # Leer textos procesados
        texto1 = ""
        texto2 = ""
        
        # Buscar archivos .txt procesados
        txt1 = self.docs_dir / f"{doc1.stem}.txt"
        txt2 = self.docs_dir / f"{doc2.stem}.txt"
        
        if txt1.exists():
            with open(txt1, 'r', encoding='utf-8') as f:
                texto1 = f.read()
        
        if txt2.exists():
            with open(txt2, 'r', encoding='utf-8') as f:
                texto2 = f.read()
        
        if not texto1 or not texto2:
            return {"error": "Uno o ambos documentos no han sido procesados"}
        
        # Calcular similitud
        similitud = difflib.SequenceMatcher(None, texto1, texto2).ratio()
        
        # Encontrar diferencias
        differ = difflib.Differ()
        diff = list(differ.compare(texto1.split('\n'), texto2.split('\n')))
        
        # Contar cambios
        lineas_agregadas = sum(1 for d in diff if d.startswith('+ '))
        lineas_eliminadas = sum(1 for d in diff if d.startswith('- '))
        
        resultado = {
            "documento_1": doc1.name,
            "documento_2": doc2.name,
            "similitud_porcentaje": round(similitud * 100, 2),
            "lineas_agregadas": lineas_agregadas,
            "lineas_eliminadas": lineas_eliminadas,
            "diferencias_mayores": lineas_agregadas + lineas_eliminadas > 50
        }
        
        print(f"\n📊 Comparación de documentos:")
        print(f"   Doc 1: {doc1.name}")
        print(f"   Doc 2: {doc2.name}")
        print(f"   Similitud: {resultado['similitud_porcentaje']}%")
        print(f"   Líneas agregadas: {lineas_agregadas}")
        print(f"   Líneas eliminadas: {lineas_eliminadas}")
        
        return resultado
    
    def analizar_calidad_paper(self, texto: str) -> Dict:
        """
        Analiza la calidad/completitud de un paper científico
        Verifica presencia de secciones clave, metodología, etc.
        """
        calidad = {
            "completitud": 0,
            "secciones_encontradas": [],
            "secciones_faltantes": [],
            "tiene_abstract": False,
            "tiene_metodologia": False,
            "tiene_resultados": False,
            "tiene_referencias": False,
            "numero_referencias": 0,
            "numero_figuras": 0,
            "recomendaciones": []
        }
        
        texto_lower = texto.lower()
        
        # Secciones esperadas en un paper
        secciones_esperadas = {
            "abstract": r'\babstract\b',
            "introduction": r'\bintroduction\b',
            "methods": r'\b(?:methods|methodology|materials and methods)\b',
            "results": r'\bresults\b',
            "discussion": r'\bdiscussion\b',
            "conclusion": r'\bconclusion\b',
            "references": r'\b(?:references|bibliography)\b'
        }
        
        # Verificar cada sección
        for seccion, patron in secciones_esperadas.items():
            if re.search(patron, texto_lower):
                calidad["secciones_encontradas"].append(seccion)
            else:
                calidad["secciones_faltantes"].append(seccion)
        
        # Marcar secciones importantes
        calidad["tiene_abstract"] = "abstract" in calidad["secciones_encontradas"]
        calidad["tiene_metodologia"] = "methods" in calidad["secciones_encontradas"]
        calidad["tiene_resultados"] = "results" in calidad["secciones_encontradas"]
        calidad["tiene_referencias"] = "references" in calidad["secciones_encontradas"]
        
        # Contar referencias
        refs = re.findall(r'\[(\d+)\]', texto)
        calidad["numero_referencias"] = len(set(refs))
        
        # Contar figuras
        figs = re.findall(r'(?:Figure|Fig\.?)\s+(\d+)', texto, re.IGNORECASE)
        calidad["numero_figuras"] = len(set(figs))
        
        # Calcular completitud (porcentaje de secciones encontradas)
        calidad["completitud"] = round(
            len(calidad["secciones_encontradas"]) / len(secciones_esperadas) * 100,
            1
        )
        
        # Generar recomendaciones
        if not calidad["tiene_abstract"]:
            calidad["recomendaciones"].append("⚠️ Falta abstract o resumen")
        if not calidad["tiene_metodologia"]:
            calidad["recomendaciones"].append("⚠️ No se detectó sección de metodología")
        if calidad["numero_referencias"] < 10:
            calidad["recomendaciones"].append(f"⚠️ Pocas referencias ({calidad['numero_referencias']}), considerar agregar más")
        if calidad["numero_figuras"] == 0:
            calidad["recomendaciones"].append("ℹ️ No se detectaron figuras referenciadas")
        
        return calidad


if __name__ == "__main__":
    # Ejemplo de uso
    print("\n" + "="*70)
    print("TARS Document Processor - Ingesta Rápida de Información")
    print("="*70)
    
    processor = DocumentProcessor()
    
    # Mostrar resumen
    resumen = processor.generar_resumen_coleccion()
    print(f"\n📚 Documentos procesados: {resumen['total_documentos']}")
    
    if resumen['total_documentos'] > 0:
        print(f"📄 Total páginas: {resumen['total_paginas']}")
        print(f"📝 Total palabras: {resumen['total_palabras']:,}")
        print(f"\nCategorías:")
        for cat, count in resumen['categorias'].items():
            print(f"   - {cat}: {count}")
