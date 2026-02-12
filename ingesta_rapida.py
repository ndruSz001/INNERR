#!/usr/bin/env python3
"""
Script de Ingesta Rápida de Información para TARS
Procesa PDFs, imágenes y otros documentos para investigación
"""

import sys
import os
from pathlib import Path
from core_ia import TarsVision


def procesar_paper_cientifico(pdf_path):
    """Procesa un paper científico completo"""
    print("\n" + "="*70)
    print("📄 PROCESANDO PAPER CIENTÍFICO")
    print("="*70)
    
    tars = TarsVision()
    
    # Procesar PDF
    resultado = tars.procesar_pdf(
        pdf_path,
        categoria="paper",
        extraer_imagenes=True
    )
    
    if "error" in resultado:
        print(f"❌ Error: {resultado['error']}")
        return
    
    print(f"\n✅ Paper procesado: {resultado['nombre_archivo']}")
    print(f"   📊 {resultado['metadatos']['num_paginas']} páginas")
    print(f"   📝 {resultado['estadisticas']['total_palabras']:,} palabras")
    print(f"   📊 {resultado['estadisticas']['total_tablas']} tablas")
    print(f"   🖼️  {resultado['estadisticas']['total_imagenes']} imágenes")
    
    # Extraer información clave
    if tars.docs:
        info_clave = tars.docs.extraer_informacion_clave(
            resultado["texto_completo"],
            tipo="paper"
        )
        
        if info_clave.get("secciones_detectadas"):
            print(f"\n📑 Secciones detectadas:")
            for seccion in info_clave["secciones_detectadas"]:
                print(f"   ✓ {seccion.title()}")
        
        if info_clave.get("figuras_mencionadas"):
            print(f"\n🖼️  Figuras mencionadas: {len(info_clave['figuras_mencionadas'])}")
            for fig in info_clave["figuras_mencionadas"][:5]:
                print(f"   - Figura {fig}")
    
    return resultado


def procesar_manual_tecnico(pdf_path):
    """Procesa un manual técnico"""
    print("\n" + "="*70)
    print("📘 PROCESANDO MANUAL TÉCNICO")
    print("="*70)
    
    tars = TarsVision()
    
    resultado = tars.procesar_pdf(
        pdf_path,
        categoria="manual",
        extraer_imagenes=True
    )
    
    if "error" not in resultado:
        print(f"\n✅ Manual procesado: {resultado['nombre_archivo']}")
        
        # Extraer pasos/procedimientos
        if tars.docs:
            info_clave = tars.docs.extraer_informacion_clave(
                resultado["texto_completo"],
                tipo="manual"
            )
            
            if info_clave.get("pasos_detectados"):
                print(f"\n📋 Pasos detectados: {len(info_clave['pasos_detectados'])}")
    
    return resultado


def analisis_completo_documento(pdf_path):
    """Análisis completo con cerebros expertos"""
    print("\n" + "="*70)
    print("🧠 ANÁLISIS COMPLETO CON CEREBROS EXPERTOS")
    print("="*70)
    
    tars = TarsVision()
    
    # Procesar y analizar
    analisis = tars.analizar_documento_con_expertos(
        pdf_path,
        tipo_analisis="completo"
    )
    
    if "error" in analisis:
        print(f"❌ Error: {analisis['error']}")
        return
    
    print(f"\n📄 Documento: {analisis['documento']}")
    print(f"📊 Páginas procesadas: {analisis['total_paginas']}")
    
    if analisis.get("analisis_expertos"):
        print(f"\n🔬 Análisis de expertos realizados: {len(analisis['analisis_expertos'])}")
        for i, analisis_exp in enumerate(analisis["analisis_expertos"], 1):
            print(f"\n   Análisis {i} ({analisis_exp['tipo']}):")
            print(f"   Imagen: {Path(analisis_exp['imagen']).name}")
    
    return analisis


def buscar_informacion(query):
    """Busca información en todos los documentos procesados"""
    print("\n" + "="*70)
    print(f"🔍 BUSCANDO: '{query}'")
    print("="*70)
    
    tars = TarsVision()
    
    resultados = tars.buscar_en_documentos(query)
    
    if not resultados:
        print("\n❌ No se encontraron resultados")
        return
    
    print(f"\n✅ {len(resultados)} resultado(s) encontrado(s):\n")
    
    for i, res in enumerate(resultados, 1):
        print(f"{i}. 📄 {res['documento']}")
        print(f"   {res['contexto']}")
        print()


def listar_documentos_procesados():
    """Lista todos los documentos en la base de conocimiento"""
    print("\n" + "="*70)
    print("📚 DOCUMENTOS PROCESADOS")
    print("="*70)
    
    tars = TarsVision()
    
    if not tars.docs:
        print("❌ Procesador de documentos no disponible")
        return
    
    resumen = tars.docs.generar_resumen_coleccion()
    
    print(f"\n📊 Total documentos: {resumen['total_documentos']}")
    print(f"📄 Total páginas: {resumen['total_paginas']}")
    print(f"📝 Total palabras: {resumen['total_palabras']:,}")
    
    if resumen['categorias']:
        print(f"\n📁 Por categoría:")
        for cat, count in resumen['categorias'].items():
            print(f"   - {cat}: {count} documento(s)")
    
    # Listar documentos
    docs = tars.docs.listar_documentos()
    if docs:
        print(f"\n📋 Documentos:")
        for i, doc in enumerate(docs, 1):
            print(f"\n{i}. {doc['nombre']}")
            print(f"   Categoría: {doc['categoria']}")
            print(f"   Páginas: {doc['paginas']}")
            print(f"   Palabras: {doc['palabras']:,}")
            print(f"   Fecha: {doc['fecha'][:10]}")


def menu_interactivo():
    """Menú interactivo para ingesta de información"""
    tars = TarsVision()
    
    while True:
        print("\n" + "="*70)
        print("TARS - INGESTA RÁPIDA DE INFORMACIÓN")
        print("="*70)
        print("\nOpciones:")
        print("1. Procesar paper científico")
        print("2. Procesar manual técnico")
        print("3. Análisis completo (con cerebros expertos)")
        print("4. Buscar en documentos")
        print("5. Listar documentos procesados")
        print("6. Salir")
        
        opcion = input("\nSelecciona opción (1-6): ").strip()
        
        if opcion == "1":
            pdf_path = input("\nRuta del PDF: ").strip()
            if os.path.exists(pdf_path):
                procesar_paper_cientifico(pdf_path)
            else:
                print(f"❌ Archivo no encontrado: {pdf_path}")
        
        elif opcion == "2":
            pdf_path = input("\nRuta del PDF: ").strip()
            if os.path.exists(pdf_path):
                procesar_manual_tecnico(pdf_path)
            else:
                print(f"❌ Archivo no encontrado: {pdf_path}")
        
        elif opcion == "3":
            pdf_path = input("\nRuta del PDF: ").strip()
            if os.path.exists(pdf_path):
                analisis_completo_documento(pdf_path)
            else:
                print(f"❌ Archivo no encontrado: {pdf_path}")
        
        elif opcion == "4":
            query = input("\n🔍 ¿Qué buscas?: ").strip()
            if query:
                buscar_informacion(query)
        
        elif opcion == "5":
            listar_documentos_procesados()
        
        elif opcion == "6":
            print("\n👋 ¡Hasta pronto!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "TARS - INGESTA DE INFORMACIÓN" + " "*24 + "║")
    print("║" + " "*10 + "Procesa PDFs, papers, manuales técnicos" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    # Si se pasa un archivo como argumento
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        if not os.path.exists(pdf_path):
            print(f"\n❌ Archivo no encontrado: {pdf_path}")
            print("\nUso:")
            print(f"  python {sys.argv[0]} <archivo.pdf>")
            print(f"  python {sys.argv[0]}  # Modo interactivo")
            sys.exit(1)
        
        # Determinar tipo por nombre o extensión
        nombre = Path(pdf_path).stem.lower()
        
        if "manual" in nombre:
            procesar_manual_tecnico(pdf_path)
        elif "paper" in nombre or "article" in nombre:
            procesar_paper_cientifico(pdf_path)
        else:
            # Por defecto, análisis completo
            analisis_completo_documento(pdf_path)
    
    else:
        # Modo interactivo
        menu_interactivo()
