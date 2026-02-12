#!/usr/bin/env python3
"""
Visualizador de Grafo de Conocimiento
Sistema de memoria episódica estructurada - TARS
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from conversation_manager import ConversationManager


class GrafoConocimientoVisualizer:
    """
    Herramientas para visualizar y navegar el grafo de conocimiento
    """
    
    def __init__(self):
        self.manager = ConversationManager()
    
    def mostrar_grafo_completo(self):
        """Muestra el grafo completo de conversaciones"""
        grafo = self.manager.obtener_grafo_conocimiento()
        
        print("\n" + "="*80)
        print("🕸️  GRAFO DE CONOCIMIENTO - TARS")
        print("="*80)
        
        stats = grafo['estadisticas']
        print(f"\n📊 Estadísticas:")
        print(f"   • Nodos (conversaciones): {stats['num_nodos']}")
        print(f"   • Aristas (relaciones): {stats['num_aristas']}")
        print(f"   • Conversaciones integradoras: {stats['nodos_integradores']}")
        print(f"   • Conversaciones independientes: {stats['nodos_independientes']}")
        
        if not grafo['nodos']:
            print("\n⚠️  No hay conversaciones en el sistema")
            return
        
        # Agrupar por categoría
        por_categoria = {}
        for nid, nodo in grafo['nodos'].items():
            cat = nodo['categoria']
            if cat not in por_categoria:
                por_categoria[cat] = []
            por_categoria[cat].append((nid, nodo))
        
        print(f"\n📁 Conversaciones por categoría:")
        for cat, nodos in por_categoria.items():
            print(f"\n   {cat.upper()} ({len(nodos)}):")
            for nid, nodo in nodos:
                integrador = " [INTEGRADORA]" if nodo['es_integradora'] else ""
                print(f"      • {nid}: {nodo['titulo']}{integrador}")
        
        # Mostrar relaciones
        if grafo['aristas']:
            print(f"\n🔗 Relaciones entre conversaciones:")
            
            # Agrupar por tipo
            por_tipo = {}
            for arista in grafo['aristas']:
                tipo = arista['tipo']
                if tipo not in por_tipo:
                    por_tipo[tipo] = []
                por_tipo[tipo].append(arista)
            
            for tipo, aristas in por_tipo.items():
                print(f"\n   {tipo.upper()} ({len(aristas)}):")
                for arista in aristas[:10]:  # Mostrar max 10 por tipo
                    origen_titulo = grafo['nodos'][arista['origen']]['titulo']
                    destino_titulo = grafo['nodos'][arista['destino']]['titulo']
                    rel = arista['relevancia']
                    
                    print(f"      {arista['origen']}: {origen_titulo}")
                    print(f"         ↓ ({rel}/10)")
                    print(f"      {arista['destino']}: {destino_titulo}")
                    print()
                
                if len(aristas) > 10:
                    print(f"      ... y {len(aristas) - 10} más")
    
    def explorar_conversacion(self, conv_id: str, profundidad: int = 1):
        """
        Explora una conversación y sus relaciones
        
        Args:
            conv_id: ID de la conversación
            profundidad: Niveles de relaciones a explorar
        """
        print("\n" + "="*80)
        print(f"🔍 EXPLORANDO CONVERSACIÓN: {conv_id}")
        print("="*80)
        
        # Información básica
        import sqlite3
        conn = sqlite3.connect(str(self.manager.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT titulo, descripcion, categoria, es_integradora, objetivo,
                   conclusiones, resultados, num_mensajes, fecha_inicio,
                   fecha_ultima_actividad, tags, proyecto_relacionado
            FROM conversaciones WHERE id = ?
        ''', (conv_id,))
        
        row = cursor.fetchone()
        
        if not row:
            print(f"\n❌ Conversación {conv_id} no encontrada")
            conn.close()
            return
        
        titulo, desc, cat, es_int, obj, concl, res, num_msg, fecha_i, fecha_u, tags, proy = row
        
        print(f"\n📌 Título: {titulo}")
        print(f"📁 Categoría: {cat}")
        print(f"💬 Mensajes: {num_msg}")
        
        if es_int:
            print(f"🔗 Tipo: CONVERSACIÓN INTEGRADORA")
        
        if obj:
            print(f"\n🎯 Objetivo:")
            print(f"   {obj}")
        
        if desc:
            print(f"\n📝 Descripción:")
            print(f"   {desc}")
        
        if concl:
            print(f"\n💡 Conclusiones:")
            for linea in concl.split('\n'):
                if linea.strip():
                    print(f"   • {linea.strip()}")
        
        if res:
            print(f"\n✅ Resultados:")
            for linea in res.split('\n'):
                if linea.strip():
                    print(f"   • {linea.strip()}")
        
        if proy:
            print(f"\n🔗 Proyecto relacionado: {proy}")
        
        if tags:
            tags_list = json.loads(tags)
            if tags_list:
                print(f"\n🏷️  Tags: {', '.join(tags_list)}")
        
        fecha_inicio = datetime.fromisoformat(fecha_i)
        fecha_ultima = datetime.fromisoformat(fecha_u)
        dias = (datetime.now() - fecha_ultima).days
        
        print(f"\n🕐 Temporal:")
        print(f"   • Inicio: {fecha_inicio.strftime('%Y-%m-%d %H:%M')}")
        print(f"   • Última actividad: Hace {dias} día(s)")
        
        conn.close()
        
        # Relaciones
        relaciones = self.manager.obtener_conversaciones_relacionadas(conv_id)
        
        if relaciones['salientes']:
            print(f"\n🔗 Relaciones salientes ({len(relaciones['salientes'])}):")
            print(f"   (Esta conversación referencia otras)")
            for rel in relaciones['salientes']:
                print(f"\n   → {rel['tipo'].upper()}: {rel['titulo']}")
                print(f"      ID: {rel['id']}")
                print(f"      Relevancia: {'★' * rel['relevancia']}")
                if rel['descripcion']:
                    print(f"      {rel['descripcion']}")
        
        if relaciones['entrantes']:
            print(f"\n🔗 Relaciones entrantes ({len(relaciones['entrantes'])}):")
            print(f"   (Otras conversaciones referencian esta)")
            for rel in relaciones['entrantes']:
                print(f"\n   ← {rel['tipo'].upper()}: {rel['titulo']}")
                print(f"      ID: {rel['id']}")
                print(f"      Relevancia: {'★' * rel['relevancia']}")
                if rel['descripcion']:
                    print(f"      {rel['descripcion']}")
        
        if not relaciones['salientes'] and not relaciones['entrantes']:
            print(f"\n⚠️  Esta conversación no tiene relaciones con otras")
            print(f"   (Es una conversación independiente)")
        
        # Subgrafo si hay profundidad
        if profundidad > 0 and relaciones['total'] > 0:
            print(f"\n🕸️  Subgrafo (profundidad {profundidad}):")
            subgrafo = self.manager.obtener_grafo_conocimiento(profundidad, conv_id)
            
            print(f"   • Nodos alcanzables: {subgrafo['estadisticas']['num_nodos']}")
            print(f"   • Relaciones totales: {subgrafo['estadisticas']['num_aristas']}")
    
    def sugerir_integracion(self, conv_ids: List[str]):
        """
        Analiza un conjunto de conversaciones y sugiere si vale la pena integrarlas
        
        Args:
            conv_ids: Lista de IDs de conversaciones a analizar
        """
        print("\n" + "="*80)
        print("🧪 ANÁLISIS DE CONVERGENCIA")
        print("="*80)
        
        if len(conv_ids) < 2:
            print("\n⚠️  Se requieren al menos 2 conversaciones para análisis")
            return
        
        print(f"\n📊 Analizando {len(conv_ids)} conversaciones...")
        
        analisis = self.manager.analizar_convergencias(conv_ids)
        
        if 'error' in analisis:
            print(f"\n❌ Error: {analisis['error']}")
            return
        
        print(f"\n📚 Conversaciones analizadas:")
        for conv in analisis['conversaciones']:
            print(f"   • {conv['id']}: {conv['titulo']} [{conv['categoria']}]")
        
        # Temas comunes
        if analisis['temas_comunes']:
            print(f"\n🎯 Temas comunes encontrados:")
            for tema in analisis['temas_comunes'][:10]:
                barra = '█' * int(tema['porcentaje'] / 10)
                print(f"   • {tema['palabra']:<20} {barra} {tema['frecuencia']}/{len(conv_ids)}")
        else:
            print(f"\n⚠️  No se encontraron temas comunes evidentes")
        
        # Categorías
        print(f"\n📁 Distribución de categorías:")
        for cat, count in analisis['categorias'].items():
            print(f"   • {cat}: {count}")
        
        # Convergencias
        if analisis['convergencias']:
            print(f"\n✅ Convergencias detectadas:")
            for conv in analisis['convergencias']:
                print(f"   • {conv['tipo']}: {conv['descripcion']}")
        
        # Divergencias
        if analisis['divergencias']:
            print(f"\n⚠️  Divergencias detectadas:")
            for div in analisis['divergencias']:
                print(f"   • {div['tipo']}: {div['descripcion']}")
        
        # Recomendación
        print(f"\n💡 RECOMENDACIÓN:")
        
        temas_comunes_significativos = len([t for t in analisis['temas_comunes'] 
                                            if t['frecuencia'] >= len(conv_ids) * 0.5])
        
        if temas_comunes_significativos >= 3:
            print(f"   ✅ ALTA convergencia temática")
            print(f"   → Se recomienda crear conversación integradora")
            print(f"   → Estas conversaciones comparten contexto significativo")
        elif temas_comunes_significativos >= 1:
            print(f"   🟡 MEDIA convergencia temática")
            print(f"   → Considerar integración si hay objetivo común")
            print(f"   → Hay algunos temas compartidos")
        else:
            print(f"   🔴 BAJA convergencia temática")
            print(f"   → No se recomienda integración automática")
            print(f"   → Conversaciones parecen independientes")
    
    def exportar_grafo_dot(self, archivo: str = "grafo_conocimiento.dot"):
        """
        Exporta el grafo en formato DOT para visualización con Graphviz
        
        Args:
            archivo: Nombre del archivo de salida
        """
        grafo = self.manager.obtener_grafo_conocimiento()
        
        dot = ["digraph GrafoConocimiento {"]
        dot.append("  rankdir=LR;")
        dot.append("  node [shape=box, style=rounded];")
        dot.append("")
        
        # Nodos
        for nid, nodo in grafo['nodos'].items():
            label = nodo['titulo'].replace('"', '\\"')
            color = "lightblue" if nodo['es_integradora'] else "white"
            
            dot.append(f'  "{nid}" [label="{label}\\n[{nodo["categoria"]}]", fillcolor={color}, style=filled];')
        
        dot.append("")
        
        # Aristas
        for arista in grafo['aristas']:
            peso = arista['relevancia']
            estilo = f"label=\"{arista['tipo']}\\n{peso}/10\""
            
            dot.append(f'  "{arista["origen"]}" -> "{arista["destino"]}" [{estilo}];')
        
        dot.append("}")
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot))
        
        print(f"\n✅ Grafo exportado a: {archivo}")
        print(f"   Visualizar con: dot -Tpng {archivo} -o grafo.png")


def menu_interactivo():
    """Menú interactivo para explorar el grafo de conocimiento"""
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
                # Análisis previo
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
