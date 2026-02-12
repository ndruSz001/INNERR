#!/usr/bin/env python3
"""
Interfaz Interactiva TARS con Gestión de Conversaciones
Permite elegir entre:
- Nueva conversación ocasional
- Continuar conversación anterior
- Buscar en conversaciones pasadas
"""

import sys
from pathlib import Path
from datetime import datetime
from conversation_manager import ConversationManager


def mostrar_menu_principal():
    """Menú principal al iniciar TARS"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*25 + "TARS - INICIO" + " "*32 + "║")
    print("╚" + "="*68 + "╝")
    print("\n¿Cómo deseas empezar?")
    print("\n1. 💬 Nueva conversación (ocasional)")
    print("2. 📂 Continuar conversación anterior")
    print("3. 🔍 Buscar en conversaciones pasadas")
    print("4. 📊 Ver estadísticas de conversaciones")
    print("5. 📋 Listar todas las conversaciones")
    print("6. ⚙️  Configuración de memoria")
    print("7. 🚪 Salir")
    
    return input("\nSelecciona opción (1-7): ").strip()


def nueva_conversacion_wizard(manager: ConversationManager) -> str:
    """Wizard para crear nueva conversación con filtros"""
    print("\n" + "="*70)
    print("💬 NUEVA CONVERSACIÓN")
    print("="*70)
    
    # Filtro 1: Tipo de conversación
    print("\n¿Qué tipo de conversación será?")
    print("1. 🔬 Investigación / Análisis de papers")
    print("2. ⚙️  Desarrollo / Diseño de proyecto")
    print("3. 🏥 Médica / Biomecánica")
    print("4. 💬 Casual / General")
    print("5. 📊 Análisis de datos / Experimentos")
    
    tipo_opcion = input("\nTipo (1-5, Enter=casual): ").strip() or "4"
    
    categorias = {
        "1": "investigacion",
        "2": "desarrollo", 
        "3": "medica",
        "4": "casual",
        "5": "analisis"
    }
    categoria = categorias.get(tipo_opcion, "casual")
    
    # Filtro 2: Relacionar con proyecto
    print(f"\n¿Esta conversación está relacionada con algún proyecto específico?")
    print("(Enter para omitir)")
    proyecto = input("Nombre del proyecto: ").strip() or None
    
    # Filtro 3: Importancia
    print(f"\n¿Qué tan importante es esta conversación?")
    print("1-3: Baja (exploratoria)")
    print("4-7: Media (trabajo regular)")
    print("8-10: Alta (crítica/importante)")
    
    importancia = input("Importancia (1-10, Enter=5): ").strip() or "5"
    try:
        importancia = int(importancia)
        importancia = max(1, min(10, importancia))
    except:
        importancia = 5
    
    # Filtro 4: Tags opcionales
    print(f"\nEtiquetas para organización (separadas por comas):")
    print("Ejemplos: exoesqueleto, motor, ACL, pruebas")
    tags_input = input("Tags (Enter para omitir): ").strip()
    tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
    
    # Crear conversación
    conv_id = manager.nueva_conversacion(
        titulo=None,  # Se generará automáticamente
        categoria=categoria,
        proyecto_relacionado=proyecto,
        tags=tags,
        auto_titulo=True
    )
    
    # Guardar importancia en contexto
    manager.guardar_contexto(conv_id, "importancia", str(importancia))
    
    # Actualizar importancia en BD
    import sqlite3
    conn = sqlite3.connect(str(manager.db_path))
    cursor = conn.cursor()
    cursor.execute("UPDATE conversaciones SET importancia = ? WHERE id = ?",
                   (importancia, conv_id))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Conversación configurada")
    print(f"   Categoría: {categoria}")
    if proyecto:
        print(f"   Proyecto: {proyecto}")
    if tags:
        print(f"   Tags: {', '.join(tags)}")
    print(f"   Importancia: {importancia}/10")
    
    return conv_id


def continuar_conversacion_wizard(manager: ConversationManager) -> str:
    """Wizard para elegir conversación a continuar"""
    print("\n" + "="*70)
    print("📂 CONTINUAR CONVERSACIÓN")
    print("="*70)
    
    # Mostrar conversaciones recientes
    print("\nConversaciones recientes:")
    
    conversaciones = manager.listar_conversaciones(
        estado="activa",
        limit=10,
        orden="reciente"
    )
    
    if not conversaciones:
        print("\n⚠️  No hay conversaciones activas")
        print("Crear nueva conversación...")
        return nueva_conversacion_wizard(manager)
    
    for i, conv in enumerate(conversaciones, 1):
        fecha = datetime.fromisoformat(conv['fecha_ultima_actividad'])
        tiempo_transcurrido = datetime.now() - fecha
        
        if tiempo_transcurrido.days == 0:
            tiempo_str = "Hoy"
        elif tiempo_transcurrido.days == 1:
            tiempo_str = "Ayer"
        else:
            tiempo_str = f"Hace {tiempo_transcurrido.days} días"
        
        print(f"\n{i}. {conv['titulo']}")
        print(f"   📁 {conv['categoria']} | 💬 {conv['num_mensajes']} mensajes | 🕐 {tiempo_str}")
        if conv['proyecto_relacionado']:
            print(f"   🔗 Proyecto: {conv['proyecto_relacionado']}")
    
    print(f"\n{len(conversaciones) + 1}. 🔍 Buscar otra conversación")
    print(f"{len(conversaciones) + 2}. 💬 Nueva conversación")
    
    opcion = input(f"\nElegir (1-{len(conversaciones) + 2}): ").strip()
    
    try:
        opcion_num = int(opcion)
        
        if 1 <= opcion_num <= len(conversaciones):
            # Continuar conversación elegida
            conv_elegida = conversaciones[opcion_num - 1]
            contexto = manager.continuar_conversacion(conv_elegida['id'])
            
            # Mostrar resumen de últimos mensajes
            print(f"\n📜 Últimos mensajes:")
            for msg in contexto['ultimos_mensajes'][-3:]:
                tipo_emoji = "👤" if msg['tipo'] == 'user' else "🤖"
                contenido_corto = msg['contenido'][:80] + "..." if len(msg['contenido']) > 80 else msg['contenido']
                print(f"   {tipo_emoji} {contenido_corto}")
            
            return conv_elegida['id']
        
        elif opcion_num == len(conversaciones) + 1:
            # Buscar
            return buscar_conversacion_wizard(manager)
        
        else:
            # Nueva conversación
            return nueva_conversacion_wizard(manager)
    
    except:
        return nueva_conversacion_wizard(manager)


def buscar_conversacion_wizard(manager: ConversationManager) -> str:
    """Búsqueda de conversaciones por contenido"""
    print("\n" + "="*70)
    print("🔍 BUSCAR CONVERSACIÓN")
    print("="*70)
    
    query = input("\n🔎 Buscar: ").strip()
    
    if not query:
        return continuar_conversacion_wizard(manager)
    
    resultados = manager.buscar_conversaciones(query, limit=10)
    
    if not resultados:
        print(f"\n❌ No se encontraron conversaciones con '{query}'")
        return continuar_conversacion_wizard(manager)
    
    print(f"\n✅ {len(resultados)} resultado(s) encontrado(s):\n")
    
    for i, res in enumerate(resultados, 1):
        print(f"{i}. {res['titulo']}")
        print(f"   📁 {res['categoria']} | 💬 {res['mensajes']} mensajes")
        if res['descripcion']:
            print(f"   📝 {res['descripcion'][:60]}...")
        print()
    
    opcion = input(f"Elegir conversación (1-{len(resultados)}, Enter=cancelar): ").strip()
    
    try:
        opcion_num = int(opcion)
        if 1 <= opcion_num <= len(resultados):
            conv_id = resultados[opcion_num - 1]['id']
            manager.continuar_conversacion(conv_id)
            return conv_id
    except:
        pass
    
    return continuar_conversacion_wizard(manager)


def ver_estadisticas(manager: ConversationManager):
    """Muestra estadísticas de conversaciones"""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DE CONVERSACIONES")
    print("="*70)
    
    stats = manager.estadisticas_generales()
    
    print(f"\n📈 General:")
    print(f"   Total conversaciones: {stats['total_conversaciones']}")
    print(f"   Total mensajes: {stats['total_mensajes']}")
    
    if stats.get('por_estado'):
        print(f"\n📋 Por Estado:")
        for estado, count in stats['por_estado'].items():
            print(f"   {estado.title()}: {count}")
    
    if stats.get('por_categoria'):
        print(f"\n📁 Por Categoría:")
        for cat, count in stats['por_categoria'].items():
            print(f"   {cat.title()}: {count}")
    
    if stats.get('conversacion_mas_larga'):
        print(f"\n🏆 Conversación más larga:")
        print(f"   {stats['conversacion_mas_larga']['titulo']}")
        print(f"   {stats['conversacion_mas_larga']['mensajes']} mensajes")
    
    input("\nPresiona Enter para continuar...")


def listar_todas_conversaciones(manager: ConversationManager):
    """Lista todas las conversaciones con filtros"""
    print("\n" + "="*70)
    print("📋 LISTAR CONVERSACIONES")
    print("="*70)
    
    print("\nFiltrar por:")
    print("1. Todas las conversaciones")
    print("2. Por categoría")
    print("3. Activas solamente")
    print("4. Archivadas")
    print("5. Por proyecto")
    
    filtro = input("\nOpción (1-5, Enter=1): ").strip() or "1"
    
    kwargs = {
        "limit": 50,
        "orden": "reciente"
    }
    
    if filtro == "2":
        print("\nCategorías: investigacion, desarrollo, medica, casual, analisis")
        cat = input("Categoría: ").strip()
        if cat:
            kwargs["categoria"] = cat
    elif filtro == "3":
        kwargs["estado"] = "activa"
    elif filtro == "4":
        kwargs["estado"] = "archivada"
    elif filtro == "5":
        proyecto = input("Nombre del proyecto: ").strip()
        if proyecto:
            kwargs["proyecto"] = proyecto
    
    conversaciones = manager.listar_conversaciones(**kwargs)
    
    if not conversaciones:
        print("\n⚠️  No se encontraron conversaciones")
        input("\nPresiona Enter para continuar...")
        return
    
    print(f"\n📚 {len(conversaciones)} conversación(es):\n")
    
    for i, conv in enumerate(conversaciones, 1):
        fecha_inicio = datetime.fromisoformat(conv['fecha_inicio'])
        fecha_actividad = datetime.fromisoformat(conv['fecha_ultima_actividad'])
        
        print(f"{i}. [{conv['id']}] {conv['titulo']}")
        print(f"   📁 {conv['categoria']} | Estado: {conv['estado']}")
        print(f"   💬 {conv['num_mensajes']} mensajes | ⭐ {conv['importancia']}/10")
        print(f"   📅 Inicio: {fecha_inicio.strftime('%Y-%m-%d')}")
        print(f"   🕐 Última: {fecha_actividad.strftime('%Y-%m-%d %H:%M')}")
        
        if conv['proyecto_relacionado']:
            print(f"   🔗 Proyecto: {conv['proyecto_relacionado']}")
        
        if conv['tags']:
            print(f"   🏷️  Tags: {', '.join(conv['tags'])}")
        
        print()
    
    input("Presiona Enter para continuar...")


def configuracion_memoria(manager: ConversationManager):
    """Configuración de memoria y conversaciones"""
    print("\n" + "="*70)
    print("⚙️  CONFIGURACIÓN DE MEMORIA")
    print("="*70)
    
    print("\n1. Ver ubicación de base de datos")
    print("2. Archivar conversaciones antiguas")
    print("3. Generar resúmenes de conversaciones")
    print("4. Exportar conversaciones")
    print("5. Volver")
    
    opcion = input("\nOpción (1-5): ").strip()
    
    if opcion == "1":
        print(f"\n📁 Base de datos: {manager.db_path}")
        print(f"   Existe: {'✅' if manager.db_path.exists() else '❌'}")
        if manager.db_path.exists():
            size_mb = manager.db_path.stat().st_size / (1024 * 1024)
            print(f"   Tamaño: {size_mb:.2f} MB")
    
    elif opcion == "2":
        print("\n¿Archivar conversaciones sin actividad por más de cuántos días?")
        dias = input("Días (Enter=30): ").strip() or "30"
        # TODO: Implementar archivado automático
        print("⚠️  Función en desarrollo")
    
    elif opcion == "3":
        print("\nGenerando resúmenes...")
        conversaciones = manager.listar_conversaciones(estado="activa", limit=100)
        for conv in conversaciones:
            if conv['num_mensajes'] > 5:  # Solo si tiene suficientes mensajes
                manager.generar_resumen_conversacion(conv['id'])
                print(f"   ✅ {conv['titulo']}")
        print(f"\n✅ {len(conversaciones)} resúmenes generados")
    
    input("\nPresiona Enter para continuar...")


def simular_chat_con_memoria(manager: ConversationManager, conv_id: str):
    """Simula un chat simple con memoria de conversación"""
    print("\n" + "="*70)
    print("💬 CHAT CON TARS")
    print("="*70)
    print("Comandos: /salir, /archivar, /contexto, /resumen")
    print("="*70)
    
    while True:
        mensaje = input("\n👤 Tú: ").strip()
        
        if not mensaje:
            continue
        
        # Comandos especiales
        if mensaje == "/salir":
            # Guardar último contexto
            manager.guardar_contexto(conv_id, "ultimo_tema", "conversación general")
            print("\n💾 Conversación guardada automáticamente")
            break
        
        elif mensaje == "/archivar":
            manager.archivar_conversacion(conv_id)
            break
        
        elif mensaje == "/contexto":
            # Mostrar contexto actual
            import sqlite3
            conn = sqlite3.connect(str(manager.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                SELECT clave, valor FROM contexto_conversacion
                WHERE conversacion_id = ?
            ''', (conv_id,))
            contexto = cursor.fetchall()
            conn.close()
            
            print("\n📋 Contexto guardado:")
            for clave, valor in contexto:
                print(f"   {clave}: {valor}")
            continue
        
        elif mensaje == "/resumen":
            resumen = manager.generar_resumen_conversacion(conv_id)
            print(f"\n📝 Resumen:")
            print(f"   {resumen['resumen_corto']}")
            print(f"\n🏷️  Palabras clave: {', '.join(resumen['palabras_clave'])}")
            continue
        
        # Guardar mensaje del usuario
        manager.agregar_mensaje(conv_id, "user", mensaje)
        
        # Simular respuesta de TARS (en producción, llamar a core_ia.py)
        respuesta_simulada = f"[TARS]: He procesado tu mensaje sobre '{mensaje[:30]}...'"
        
        # Guardar respuesta
        manager.agregar_mensaje(conv_id, "tars", respuesta_simulada)
        
        print(f"\n🤖 TARS: {respuesta_simulada}")
        print("        (Conectar a core_ia.py para respuestas reales)")


def main():
    """Función principal"""
    manager = ConversationManager()
    
    while True:
        opcion = mostrar_menu_principal()
        
        if opcion == "1":
            # Nueva conversación
            conv_id = nueva_conversacion_wizard(manager)
            simular_chat_con_memoria(manager, conv_id)
        
        elif opcion == "2":
            # Continuar conversación
            conv_id = continuar_conversacion_wizard(manager)
            if conv_id:
                simular_chat_con_memoria(manager, conv_id)
        
        elif opcion == "3":
            # Buscar
            conv_id = buscar_conversacion_wizard(manager)
            if conv_id:
                simular_chat_con_memoria(manager, conv_id)
        
        elif opcion == "4":
            # Estadísticas
            ver_estadisticas(manager)
        
        elif opcion == "5":
            # Listar todas
            listar_todas_conversaciones(manager)
        
        elif opcion == "6":
            # Configuración
            configuracion_memoria(manager)
        
        elif opcion == "7":
            print("\n👋 ¡Hasta pronto!")
            break
        
        else:
            print("\n❌ Opción inválida")


if __name__ == "__main__":
    main()
