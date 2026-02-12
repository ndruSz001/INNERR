#!/usr/bin/env python3
"""
Demostración de Funcionalidades Avanzadas de Procesamiento de PDFs
TARS - Sistema mejorado para investigación científica
"""

import sys
from pathlib import Path
from core_ia import TarsVision


def demo_ocr(pdf_path):
    """Demo: OCR para PDFs escaneados"""
    print("\n" + "="*70)
    print("🔍 DEMO: OCR para PDFs Escaneados")
    print("="*70)
    print("\nUso: Para papers antiguos sin texto extraíble")
    print("Detecta texto en imágenes escaneadas usando Tesseract OCR\n")
    
    tars = TarsVision()
    
    # Aplicar OCR
    resultado = tars.procesar_pdf_con_ocr(pdf_path, idioma="spa+eng")
    
    if "error" not in resultado:
        print(f"\n✅ OCR completado:")
        print(f"   📄 Páginas: {len(resultado['paginas_ocr'])}")
        print(f"   📝 Palabras extraídas: {resultado['total_palabras']:,}")
        print(f"   💾 Guardado en: tars_lifelong/knowledge/ocr_results/")
        
        # Mostrar primeras líneas
        primeras_lineas = resultado['texto_completo'][:500]
        print(f"\n📖 Primeras líneas extraídas:")
        print(f"   {primeras_lineas}...")


def demo_metadatos(pdf_path):
    """Demo: Extracción de metadatos de papers"""
    print("\n" + "="*70)
    print("📋 DEMO: Extracción Automática de Metadatos")
    print("="*70)
    print("\nExtrae: Título, Autores, DOI, Año, Abstract, Keywords\n")
    
    tars = TarsVision()
    
    metadatos = tars.extraer_metadatos_paper(pdf_path)
    
    if "error" not in metadatos:
        print("\n✅ Metadatos extraídos:\n")
        
        if metadatos.get("titulo"):
            print(f"📌 Título: {metadatos['titulo']}")
        
        if metadatos.get("doi"):
            print(f"🔗 DOI: {metadatos['doi']}")
        
        if metadatos.get("año"):
            print(f"📅 Año: {metadatos['año']}")
        
        if metadatos.get("keywords"):
            print(f"\n🏷️  Keywords ({len(metadatos['keywords'])}):")
            for kw in metadatos['keywords'][:5]:
                print(f"   • {kw}")
        
        if metadatos.get("abstract"):
            print(f"\n📄 Abstract (primeras líneas):")
            print(f"   {metadatos['abstract'][:300]}...")


def demo_resumen(pdf_path):
    """Demo: Resumen automático"""
    print("\n" + "="*70)
    print("📝 DEMO: Resumen Automático Extractivo")
    print("="*70)
    print("\nGenera resumen basado en oraciones más importantes\n")
    
    tars = TarsVision()
    
    resultado = tars.generar_resumen_pdf(pdf_path, num_oraciones=5)
    
    if "error" not in resultado:
        print(f"\n✅ Resumen generado ({resultado['num_oraciones']} oraciones):\n")
        print(resultado['resumen'])


def demo_referencias(pdf_path):
    """Demo: Extracción de referencias bibliográficas"""
    print("\n" + "="*70)
    print("📚 DEMO: Extracción de Referencias Bibliográficas")
    print("="*70)
    print("\nExtrae y estructura todas las referencias citadas\n")
    
    tars = TarsVision()
    
    resultado = tars.extraer_referencias_paper(pdf_path)
    
    if "error" not in resultado:
        print(f"\n✅ Referencias extraídas: {resultado['total_referencias']}\n")
        
        # Mostrar primeras 5 referencias
        for ref in resultado['referencias'][:5]:
            print(f"[{ref['numero']}] {ref['texto'][:150]}...")
            if ref.get('doi'):
                print(f"    DOI: {ref['doi']}")
            if ref.get('año'):
                print(f"    Año: {ref['año']}")
            print()


def demo_comparacion(pdf1_path, pdf2_path):
    """Demo: Comparación entre documentos"""
    print("\n" + "="*70)
    print("🔄 DEMO: Comparación de Documentos")
    print("="*70)
    print("\nCompara dos versiones de un paper o documentos relacionados\n")
    
    tars = TarsVision()
    
    # Primero asegurar que ambos estén procesados
    print("📄 Procesando documentos si es necesario...")
    tars.procesar_pdf(pdf1_path)
    tars.procesar_pdf(pdf2_path)
    
    # Comparar
    resultado = tars.comparar_pdfs(pdf1_path, pdf2_path)
    
    if "error" not in resultado:
        print(f"\n📊 Resultados de comparación:\n")
        print(f"   Similitud: {resultado['similitud_porcentaje']}%")
        print(f"   Líneas agregadas: {resultado['lineas_agregadas']}")
        print(f"   Líneas eliminadas: {resultado['lineas_eliminadas']}")
        
        if resultado['diferencias_mayores']:
            print(f"\n   ⚠️  Diferencias significativas detectadas")
        else:
            print(f"\n   ✅ Documentos muy similares")


def demo_calidad(pdf_path):
    """Demo: Análisis de calidad de paper"""
    print("\n" + "="*70)
    print("⭐ DEMO: Análisis de Calidad de Paper Científico")
    print("="*70)
    print("\nVerifica estructura, completitud y calidad científica\n")
    
    tars = TarsVision()
    
    calidad = tars.analizar_calidad_paper(pdf_path)
    
    if "error" not in calidad:
        print(f"\n📊 Análisis completo:")
        print(f"   Completitud: {calidad['completitud']}%")
        print(f"\n   ✅ Secciones encontradas:")
        for seccion in calidad['secciones_encontradas']:
            print(f"      • {seccion.title()}")
        
        if calidad['secciones_faltantes']:
            print(f"\n   ⚠️  Secciones faltantes:")
            for seccion in calidad['secciones_faltantes']:
                print(f"      • {seccion.title()}")
        
        print(f"\n   📚 Referencias: {calidad['numero_referencias']}")
        print(f"   🖼️  Figuras mencionadas: {calidad['numero_figuras']}")


def demo_completo(pdf_path):
    """Demo completo de todas las funcionalidades"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "TARS - PROCESAMIENTO AVANZADO DE PDFs" + " "*16 + "║")
    print("║" + " "*20 + "Demo de Funcionalidades" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    tars = TarsVision()
    
    # 1. Procesamiento básico
    print("\n" + "="*70)
    print("1️⃣  PROCESAMIENTO BÁSICO")
    print("="*70)
    
    resultado = tars.procesar_pdf(pdf_path, categoria="paper", extraer_imagenes=True)
    
    if "error" in resultado:
        print(f"❌ Error: {resultado['error']}")
        return
    
    print(f"\n✅ PDF procesado: {resultado['nombre_archivo']}")
    print(f"   📊 Páginas: {resultado['metadatos']['num_paginas']}")
    print(f"   📝 Palabras: {resultado['estadisticas']['total_palabras']:,}")
    print(f"   📊 Tablas: {resultado['estadisticas']['total_tablas']}")
    print(f"   🖼️  Imágenes: {resultado['estadisticas']['total_imagenes']}")
    
    # 2. Metadatos
    print("\n" + "="*70)
    print("2️⃣  METADATOS EXTRAÍDOS")
    print("="*70)
    
    metadatos = tars.extraer_metadatos_paper(pdf_path)
    
    if metadatos.get("doi"):
        print(f"\n🔗 DOI: {metadatos['doi']}")
    if metadatos.get("año"):
        print(f"📅 Año: {metadatos['año']}")
    if metadatos.get("keywords"):
        print(f"🏷️  Keywords: {', '.join(metadatos['keywords'][:5])}")
    
    # 3. Resumen automático
    print("\n" + "="*70)
    print("3️⃣  RESUMEN AUTOMÁTICO")
    print("="*70)
    
    resumen_resultado = tars.generar_resumen_pdf(pdf_path, num_oraciones=3)
    print(f"\n{resumen_resultado['resumen']}")
    
    # 4. Referencias
    print("\n" + "="*70)
    print("4️⃣  REFERENCIAS BIBLIOGRÁFICAS")
    print("="*70)
    
    refs = tars.extraer_referencias_paper(pdf_path)
    print(f"\n📚 Total de referencias: {refs['total_referencias']}")
    
    # 5. Calidad
    print("\n" + "="*70)
    print("5️⃣  ANÁLISIS DE CALIDAD")
    print("="*70)
    
    calidad = tars.analizar_calidad_paper(pdf_path)
    print(f"\n⭐ Completitud: {calidad['completitud']}%")
    print(f"📋 Secciones: {len(calidad['secciones_encontradas'])}")
    print(f"📚 Referencias: {calidad['numero_referencias']}")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETADO")
    print("="*70)
    print("\nTodas las funcionalidades avanzadas están operativas!")


def menu():
    """Menú interactivo"""
    while True:
        print("\n" + "="*70)
        print("TARS - PROCESAMIENTO AVANZADO DE PDFs")
        print("="*70)
        print("\nFuncionalidades Avanzadas:")
        print("1. OCR para PDFs escaneados")
        print("2. Extracción de metadatos (DOI, título, autores, etc.)")
        print("3. Resumen automático")
        print("4. Extracción de referencias bibliográficas")
        print("5. Comparación de documentos")
        print("6. Análisis de calidad de paper")
        print("7. Demo completo de todas las funciones")
        print("8. Salir")
        
        opcion = input("\nSelecciona opción (1-8): ").strip()
        
        if opcion == "1":
            pdf = input("\nRuta del PDF escaneado: ").strip()
            if Path(pdf).exists():
                demo_ocr(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "2":
            pdf = input("\nRuta del PDF: ").strip()
            if Path(pdf).exists():
                demo_metadatos(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "3":
            pdf = input("\nRuta del PDF: ").strip()
            if Path(pdf).exists():
                demo_resumen(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "4":
            pdf = input("\nRuta del PDF: ").strip()
            if Path(pdf).exists():
                demo_referencias(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "5":
            pdf1 = input("\nPrimer PDF: ").strip()
            pdf2 = input("Segundo PDF: ").strip()
            if Path(pdf1).exists() and Path(pdf2).exists():
                demo_comparacion(pdf1, pdf2)
            else:
                print("❌ Uno o ambos archivos no encontrados")
        
        elif opcion == "6":
            pdf = input("\nRuta del PDF: ").strip()
            if Path(pdf).exists():
                demo_calidad(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "7":
            pdf = input("\nRuta del PDF: ").strip()
            if Path(pdf).exists():
                demo_completo(pdf)
            else:
                print(f"❌ Archivo no encontrado: {pdf}")
        
        elif opcion == "8":
            print("\n👋 ¡Hasta pronto!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        if not Path(pdf_path).exists():
            print(f"\n❌ Archivo no encontrado: {pdf_path}")
            print("\nUso:")
            print(f"  python {sys.argv[0]} <archivo.pdf>  # Demo completo")
            print(f"  python {sys.argv[0]}                # Menú interactivo")
            sys.exit(1)
        
        # Demo completo del PDF
        demo_completo(pdf_path)
    else:
        # Menú interactivo
        menu()
