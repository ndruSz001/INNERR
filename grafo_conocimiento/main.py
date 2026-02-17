"""
CLI y menú interactivo para el grafo de conocimiento.
"""
from .visualizer import GrafoConocimientoVisualizer

def menu_interactivo():
    viz = GrafoConocimientoVisualizer()
    while True:
        print("\n" + "="*80)
        print("🕸️  EXPLORADOR DE GRAFO DE CONOCIMIENTO")
        print("="*80)
        print("\n1. Ver grafo completo")
        print("2. Explorar conversación específica")
        print("3. Analizar convergencias")
        print("4. Crear conversación integradora")
        print("5. Vincular conversaciones")
        print("6. Exportar grafo (Graphviz)")
        print("7. Salir")
        opcion = input("\nOpción: ").strip()
        if opcion == '1':
            viz.mostrar_grafo_completo()
        elif opcion == '2':
            conv_id = input("\nID de conversación: ").strip()
            prof = input("Profundidad (1-3, Enter=1): ").strip() or "1"
            viz.explorar_conversacion(conv_id, int(prof))
        elif opcion == '3':
            print("\nIDs de conversaciones a analizar (separadas por comas):")
            ids = input("IDs: ").strip().split(',')
            ids = [i.strip() for i in ids if i.strip()]
            if ids:
                viz.sugerir_integracion(ids)
        elif opcion == '4':
            print("\n" + "="*80)
            print("📝 CREAR CONVERSACIÓN INTEGRADORA")
            print("="*80)
            titulo = input("\nTítulo de la integración: ").strip()
            objetivo = input("Objetivo (por qué integrar): ").strip()
            print("\nIDs de conversaciones base (separadas por comas):")
            ids = input("IDs: ").strip().split(',')
            ids = [i.strip() for i in ids if i.strip()]
            if titulo and objetivo and len(ids) >= 2:
                print("\n🔍 Analizando convergencias...")
                viz.sugerir_integracion(ids)
                confirmar = input("\n¿Crear conversación integradora? (s/n): ").lower()
                if confirmar == 's':
                    conv_id = viz.manager.crear_conversacion_integradora(
                        titulo=titulo,
                        objetivo=objetivo,
                        conversaciones_base=ids
                    )
                    print(f"\n✅ Conversación integradora creada: {conv_id}")
                    print(f"   Puedes usarla con: python tars_asistente.py")
            else:
                print("\n❌ Datos incompletos")
        elif opcion == '5':
            print("\n" + "="*80)
            print("🔗 VINCULAR CONVERSACIONES")
            print("="*80)
            origen = input("\nID conversación origen: ").strip()
            destino = input("ID conversación destino: ").strip()
            print("\nTipos de relación:")
            print("  1. relacionada    - Temas relacionados")
            print("  2. continua       - Una continúa la otra")
            print("  3. complementa    - Información complementaria")
            print("  4. contradice     - Información contradictoria")
            print("  5. depende        - Requiere contexto de la otra")
            print("  6. converge       - Conclusiones similares")
            print("  7. diverge        - Conclusiones diferentes")
            tipo_num = input("\nTipo (1-7): ").strip()
            tipos = {
                '1': 'relacionada',
                '2': 'continua',
                '3': 'complementa',
                '4': 'contradice',
                '5': 'depende',
                '6': 'converge',
                '7': 'diverge'
            }
            tipo = tipos.get(tipo_num, 'relacionada')
            desc = input("Descripción (opcional): ").strip()
            rel = input("Relevancia 1-10 (Enter=5): ").strip() or "5"
            if origen and destino:
                exito = viz.manager.vincular_conversaciones(
                    origen, destino, tipo, desc, int(rel)
                )
                if exito:
                    print("\n✅ Conversaciones vinculadas exitosamente")
                else:
                    print("\n❌ Error al vincular (verifica que los IDs existan)")
        elif opcion == '6':
            archivo = input("\nArchivo de salida (Enter=grafo_conocimiento.dot): ").strip()
            if not archivo:
                archivo = "grafo_conocimiento.dot"
            viz.exportar_grafo_dot(archivo)
        elif opcion == '7':
            print("\n👋 ¡Hasta pronto!")
            break
        else:
            print("\n❌ Opción inválida")
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    menu_interactivo()
