"""
DocumentProcessor: Procesador de PDFs e imágenes para TARS
Centraliza rutas y lógica de ingesta usando config.py

Ejemplo de uso:
    from processing.document_processor import DocumentProcessor
    processor = DocumentProcessor()
    resultados = processor.buscar_en_documentos("machine learning")
    print(resultados)
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from core.config import DATA_DIR
from core.pdf_processing import *

class DocumentProcessor:
    """
    Procesador de documentos (PDFs, imágenes) para TARS.
    Centraliza rutas y lógica de ingesta usando config.py.
    """
    def __init__(self):
        self.base_dir = DATA_DIR / "documents"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.base_dir / "document_index.json"
        self.index = self._load_index()
        self.docs_dir = self.base_dir
        self.images_dir = self.base_dir / "images"
        self.images_dir.mkdir(exist_ok=True)

    def _load_index(self) -> Dict:
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documentos": [], "total": 0}

    def _save_index(self) -> None:
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def buscar_en_documentos(self, query: str, categoria: Optional[str] = None) -> List[Dict]:
        """
        Busca texto en todos los documentos procesados.
        Args:
            query: Texto a buscar
            categoria: Filtrar por categoría (opcional)
        Returns:
            Lista de resultados con contexto
        """
        import re
        resultados = []
        for doc_file in self.docs_dir.glob("*.txt"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                if re.search(query, contenido, re.IGNORECASE):
                    matches = list(re.finditer(query, contenido, re.IGNORECASE))
                    for match in matches[:3]:
                        start = max(0, match.start() - 100)
                        end = min(len(contenido), match.end() + 100)
                        contexto = contenido[start:end]
                        resultados.append({
                            "documento": doc_file.stem.replace("_procesado", ""),
                            "contexto": f"...{contexto}...",
                            "posicion": match.start()
                        })
            except Exception:
                pass
        return resultados

    def extraer_informacion_clave(self, texto: str, tipo: str = "paper") -> Dict:
        """
        Extrae información estructurada según el tipo de documento.
        Args:
            texto: Texto del documento
            tipo: Tipo (paper, manual, reporte)
        Returns:
            Diccionario con información extraída
        """
        import re
        info = {
            "tipo": tipo,
            "secciones_detectadas": [],
            "referencias": [],
            "ecuaciones": [],
            "figuras_mencionadas": []
        }
        if tipo == "paper":
            secciones = ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"]
            for seccion in secciones:
                if re.search(rf'\\b{seccion}\\b', texto, re.IGNORECASE):
                    info["secciones_detectadas"].append(seccion)
            figuras = re.findall(r'(?:Figure|Fig\\.?)\\s+(\\d+)', texto, re.IGNORECASE)
            info["figuras_mencionadas"] = list(set(figuras))
            refs = re.findall(r'\\[(\\d+)\\]', texto)
            info["referencias"] = list(set(refs))
        elif tipo == "manual":
            pasos = re.findall(r'(?:Step|Paso)\\s+(\\d+)', texto, re.IGNORECASE)
            info["pasos_detectados"] = list(set(pasos))
        return info

    def listar_documentos(self, categoria: Optional[str] = None) -> List[Dict]:
        """Lista todos los documentos procesados."""
        docs = self.index.get("documentos", [])
        if categoria:
            docs = [d for d in docs if d.get("categoria") == categoria]
        return docs

    def procesar_imagen(self, imagen_path: str, descripcion: str = "") -> Dict:
        """
        Procesa una imagen individual (diagrama, foto, etc.).
        """
        from core.pdf_processing import procesar_imagen
        return procesar_imagen(imagen_path, descripcion)

    def procesar_pdf(self, pdf_path: str, categoria: str = "general", extraer_imagenes: bool = True, extraer_tablas: bool = True) -> Dict:
        """
        Procesa un PDF completo: texto, imágenes, tablas, metadatos.
        """
        from core.pdf_processing import procesar_pdf
        resultado = procesar_pdf(
            pdf_path,
            categoria=categoria,
            extraer_imagenes=extraer_imagenes,
            extraer_tablas=extraer_tablas,
            images_dir=self.images_dir
        )
        if "error" not in resultado:
            self._guardar_documento_procesado(resultado)
            self._actualizar_indice(resultado)
        return resultado

    # _extraer_imagenes_pdf now handled in core/pdf_processing.py

    def _guardar_documento_procesado(self, resultado: Dict) -> None:
        """Guarda el resultado del procesamiento como JSON y TXT."""
        nombre_archivo = Path(resultado["nombre_archivo"]).stem
        output_file = self.docs_dir / f"{nombre_archivo}_procesado.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        text_file = self.docs_dir / f"{nombre_archivo}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(resultado["texto_completo"])

    def _actualizar_indice(self, resultado: Dict) -> None:
        """Actualiza el índice con el nuevo documento."""
        self.index["documentos"].append({
            "nombre": resultado["nombre_archivo"],
            "categoria": resultado["categoria"],
            "fecha": resultado["fecha_procesado"],
            "palabras": resultado["estadisticas"]["total_palabras"],
            "paginas": resultado["metadatos"].get("num_paginas", 0)
        })
        self.index["total"] = len(self.index["documentos"])
        self._save_index()
        def _save_index(self) -> None:
            """Guarda el índice de documentos procesados en disco."""
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)

        def procesar_pdf(self, pdf_path: str, categoria: str = "general", extraer_imagenes: bool = True, extraer_tablas: bool = True) -> Dict:
            """
            Procesa un PDF completo: texto, imágenes, tablas, metadatos.
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
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
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
                    if extraer_imagenes and PDF2IMAGE_AVAILABLE:
                        imagenes = self._extraer_imagenes_pdf(pdf_path_obj)
                        resultado["imagenes_extraidas"] = imagenes
                    resultado["estadisticas"] = {
                        "total_palabras": len(resultado["texto_completo"].split()),
                        "total_caracteres": len(resultado["texto_completo"]),
                        "total_tablas": len(resultado["tablas"]),
                        "total_imagenes": len(resultado["imagenes_extraidas"])
                    }
                    self._guardar_documento_procesado(resultado)
                    self._actualizar_indice(resultado)
            except Exception as e:
                resultado["error"] = str(e)
            return resultado

        def _extraer_imagenes_pdf(self, pdf_path: Path) -> List[str]:
            """Extrae imágenes del PDF como archivos separados."""
            imagenes_extraidas = []
            try:
                imagenes = convert_from_path(str(pdf_path), dpi=150)
                base_name = pdf_path.stem
                for i, img in enumerate(imagenes, 1):
                    img_path = self.images_dir / f"{base_name}_pagina_{i}.png"
                    img.save(img_path, 'PNG')
                    imagenes_extraidas.append(str(img_path))
            except Exception as e:
                pass
            return imagenes_extraidas

        def _guardar_documento_procesado(self, resultado: Dict) -> None:
            """Guarda el resultado del procesamiento como JSON y TXT."""
            nombre_archivo = Path(resultado["nombre_archivo"]).stem
            output_file = self.docs_dir / f"{nombre_archivo}_procesado.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            text_file = self.docs_dir / f"{nombre_archivo}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(resultado["texto_completo"])

        def _actualizar_indice(self, resultado: Dict) -> None:
            """Actualiza el índice con el nuevo documento."""
            self.index["documentos"].append({
                "nombre": resultado["nombre_archivo"],
                "categoria": resultado["categoria"],
                "fecha": resultado["fecha_procesado"],
                "palabras": resultado["estadisticas"]["total_palabras"],
                "paginas": resultado["metadatos"].get("num_paginas", 0)
            })
            self.index["total"] = len(self.index["documentos"])
            self._save_index()
    def __init__(self):
        self.base_dir = DATA_DIR / "documents"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.base_dir / "document_index.json"
        self.index = self._load_index()
        self.docs_dir = self.base_dir
        self.images_dir = self.base_dir / "images"
        self.images_dir.mkdir(exist_ok=True)

    def _load_index(self):
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documentos": [], "total": 0}

    def _save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    # ...aquí se migran y adaptan los métodos de procesamiento de PDF, imágenes, búsqueda, etc...
