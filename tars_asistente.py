import re
try:
    from document_processor import DocumentProcessor
except ImportError:
    DocumentProcessor = None
try:
    import requests
except ImportError:
    requests = None
#!/usr/bin/env python3
"""
TARS Terminal Chat con Detección Automática de Memoria
- Inicia como asistente normal
- Detecta automáticamente cuando quieres retomar conversación
- Palabras clave: volvamos, regresemos, continuemos, etc.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Importar módulos de TARS
try:
    from core.assistant import main

    if __name__ == "__main__":
        main()
    def detectar_intencion_nueva_conversacion(self, mensaje: str) -> bool:
        """
        Detecta si el usuario quiere iniciar una conversación nueva o cambiar de tema
        """
        mensaje_lower = mensaje.lower()
        
        palabras_clave = [
            'conversación nueva', 'conversacion nueva',
            'nueva conversación', 'nueva conversacion',
            'cambiar de tema', 'cambiemos de tema',
            'cambiar tema', 'cambiemos tema',
            'hablemos de otra cosa', 'hablemos de otro tema',
            'tema nuevo', 'nuevo tema',
            'empezar de nuevo', 'empezar algo nuevo',
            'iniciar conversación', 'iniciar conversacion',
            'empecemos con', 'empecemos algo',
            'quiero hablar de algo diferente',
            'algo completamente diferente'
        ]
        
        for palabra in palabras_clave:
            if palabra in mensaje_lower:
                return True
        
        return False
    
    def detectar_y_procesar_intencion(self, mensaje: str) -> bool:
        """
        Detecta si el usuario quiere retomar una conversación
        Returns True si se procesó la intención, False si es mensaje normal
        """
        if not self.manager:
            return False
        
        # Detectar intención
        intencion = self.manager.detectar_intencion_retomar(mensaje)
        
        if intencion['quiere_retomar']:
            print(f"\n🔍 Detectado: Quieres retomar conversación sobre '{intencion['texto_original']}'")
            print(f"   Buscando con palabras: {', '.join(intencion['palabras_busqueda'])}")
            
            # Buscar conversaciones
            resultados = self.manager.buscar_conversacion_inteligente(
                intencion['palabras_busqueda']
            )
            
            if not resultados:
                print(f"\n❌ No encontré conversaciones sobre '{intencion['texto_original']}'")
                print("   ¿Quieres iniciar una nueva conversación sobre este tema?")
                
                respuesta = input("   (s/n): ").strip().lower()
                if respuesta == 's':
                    # Crear nueva conversación con ese tema
                    self.conversacion_actual = self.manager.nueva_conversacion(
                        titulo=intencion['texto_original'],
                        categoria="investigacion",
                        tags=intencion['palabras_busqueda'],
                        auto_titulo=False
                    )
                    print(f"\n✅ Nueva conversación iniciada: {intencion['texto_original']}")
                
                return True
            
            # Mostrar resultados
            print(f"\n✅ Encontré {len(resultados)} conversación(es) relacionada(s):\n")
            
            for i, res in enumerate(resultados, 1):
                fecha = datetime.fromisoformat(res['fecha'])
                tiempo = (datetime.now() - fecha).days
                tiempo_str = "Hoy" if tiempo == 0 else f"Hace {tiempo} día(s)"
                
                print(f"{i}. {res['titulo']}")
                print(f"   📁 {res['categoria']} | 💬 {res['mensajes']} mensajes | 🕐 {tiempo_str}")
                print(f"   🎯 Relevancia: {'★' * min(5, res['score'])}")
                
                if res['proyecto']:
                    print(f"   🔗 Proyecto: {res['proyecto']}")
                if res['tags']:
                    print(f"   🏷️  {', '.join(res['tags'])}")
                print()
            
            # Preguntar cuál quiere
            if len(resultados) == 1:
                print("¿Retomar esta conversación? (s/n): ", end='')
                respuesta = input().strip().lower()
                
                if respuesta == 's':
                    self._cambiar_a_conversacion(resultados[0]['id'])
                    return True
            else:
                print(f"¿Cuál conversación quieres retomar? (1-{len(resultados)}, 0=ninguna): ", end='')
                try:
                    opcion = int(input().strip())
                    
                    if 1 <= opcion <= len(resultados):
                        self._cambiar_a_conversacion(resultados[opcion - 1]['id'])
                        return True
                except:
                    pass
            
            print("\n💬 Continuando conversación actual...")
            return True
        
        return False
    
    def _mostrar_opciones_nueva_conversacion(self):
        """Muestra opciones cuando el usuario quiere cambiar de tema"""
        print("¿Qué quieres hacer?\n")
        print("1. 💬 Crear nueva conversación")
        print("2. 📚 Ver conversaciones guardadas")
        print("3. 🔍 Buscar conversación específica")
        print("4. ↩️  Continuar con conversación actual")
        print()
        
        try:
            opcion = input("Selecciona (1-4): ").strip()
            
            if opcion == '1':
                self._crear_nueva_conversacion()
            elif opcion == '2':
                self._mostrar_conversaciones()
                print("\n¿Quieres cambiar a alguna? (ingresa el número o Enter para cancelar): ", end='')
                num = input().strip()
                if num.isdigit():
                    conversaciones = self.manager.listar_conversaciones(
                        estado="activa",
                        limit=10,
                        orden="reciente"
                    )
                    idx = int(num) - 1
                    if 0 <= idx < len(conversaciones):
                        self._cambiar_a_conversacion(conversaciones[idx]['id'])
            elif opcion == '3':
                termino = input("\n🔍 ¿Qué tema buscas? ").strip()
                if termino:
                    resultados = self.manager.buscar_conversacion_inteligente([termino])
                    if resultados:
                        print(f"\n✅ Encontré {len(resultados)} conversación(es):\n")
                        for i, res in enumerate(resultados, 1):
                            fecha = datetime.fromisoformat(res['fecha'])
                            dias = (datetime.now() - fecha).days
                            tiempo = "Hoy" if dias == 0 else f"Hace {dias} día(s)"
                            print(f"{i}. {res['titulo']} - {tiempo}")
                            print(f"   💬 {res['mensajes']} mensajes | 🎯 {'★' * min(5, res['score'])}")
                        
                        num = input(f"\n¿Retomar cuál? (1-{len(resultados)} o Enter para cancelar): ").strip()
                        if num.isdigit():
                            idx = int(num) - 1
                            if 0 <= idx < len(resultados):
                                self._cambiar_a_conversacion(resultados[idx]['id'])
                    else:
                        print("\n❌ No encontré conversaciones sobre ese tema")
            elif opcion == '4':
                print("\n✅ Continuando conversación actual...")
            else:
                print("\n⚠️  Opción inválida, continuando conversación actual")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Continuando conversación actual...")
        
        print()
    
    def _cambiar_a_conversacion(self, conv_id: str):
        """Cambia a una conversación específica"""
        contexto = self.manager.continuar_conversacion(conv_id)
        self.conversacion_actual = conv_id
        
        # Mostrar últimos mensajes
        if contexto.get('ultimos_mensajes'):
            print(f"\n📜 Últimos mensajes:")
            for msg in contexto['ultimos_mensajes'][-3:]:
                tipo = "Usuario" if msg['tipo'] == 'user' else "TARS"
                contenido = msg['contenido'][:100] + "..." if len(msg['contenido']) > 100 else msg['contenido']
                print(f"   [{tipo}] {contenido}")
        
        print(f"\n✅ Conversación '{contexto['titulo']}' recuperada")
        print("="*70 + "\n")
    
    def procesar_comando(self, mensaje: str) -> bool:
        """
        Procesa comandos especiales
        Returns True si es comando, False si es mensaje normal
        """
        if not mensaje.startswith('/'):
            return False
        
        comando = mensaje.lower().strip()
        
        if comando == '/salir':
            print("\n💾 Guardando conversación...")
            if self.manager and self.conversacion_actual:
                # Guardar contexto final
                self.manager.guardar_contexto(
                    self.conversacion_actual,
                    "ultima_sesion",
                    datetime.now().isoformat()
                )
            print("👋 ¡Hasta pronto!")
            return True
        
        elif comando == '/memoria':
            self._mostrar_conversaciones()
            return False
        
        elif comando == '/nueva':
            self._crear_nueva_conversacion()
            return False
        
        elif comando == '/contexto':
            self._mostrar_contexto()
            return False
        
        elif comando == '/ayuda':
            self._mostrar_ayuda()
            return False
        
        elif comando == '/stats' or comando == '/estadisticas':
            self._mostrar_estadisticas()
            return False
        
        elif comando == '/conclusiones':
            self._guardar_conclusiones()
            return False
        
        elif comando == '/vincular':
            self._vincular_conversacion()
            return False
        
        elif comando == '/integrar':
            self._crear_integradora()
            return False
        
        elif comando == '/grafo':
            self._mostrar_grafo()
            return False
        
        elif comando == '/voz':
            if self.voz:
                self.voz.alternar()
                self.voz_activa = self.voz.activo
            else:
                print("❌ Sistema de voz no disponible")
            return False
        
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("   Usa /ayuda para ver comandos disponibles")
            return False
    
    def _mostrar_conversaciones(self):
        """Muestra lista de conversaciones recientes"""
        if not self.manager:
            print("❌ Sistema de memoria no disponible")
            return
        
        print("\n" + "="*70)
        print("📚 CONVERSACIONES GUARDADAS")
        print("="*70)
        
        conversaciones = self.manager.listar_conversaciones(
            estado="activa",
            limit=10,
            orden="reciente"
        )
        
        if not conversaciones:
            print("\n⚠️  No hay conversaciones guardadas")
            return
        
        print()
        for i, conv in enumerate(conversaciones, 1):
            fecha = datetime.fromisoformat(conv['fecha_ultima_actividad'])
            dias = (datetime.now() - fecha).days
            tiempo = "Hoy" if dias == 0 else f"Hace {dias} día(s)"
            
            activa = " [ACTUAL]" if conv['id'] == self.conversacion_actual else ""
            
            print(f"{i}. {conv['titulo']}{activa}")
            print(f"   📁 {conv['categoria']} | 💬 {conv['num_mensajes']} mensajes | 🕐 {tiempo}")
            if conv['proyecto_relacionado']:
                print(f"   🔗 {conv['proyecto_relacionado']}")
            print()
        
        # Opción para cambiar
        print("¿Cambiar a alguna conversación? (número o Enter=cancelar): ", end='')
        opcion = input().strip()
        
        if opcion.isdigit():
            idx = int(opcion) - 1
            if 0 <= idx < len(conversaciones):
                self._cambiar_a_conversacion(conversaciones[idx]['id'])
    
    def _crear_nueva_conversacion(self):
        """Crea nueva conversación con configuración rápida"""
        if not self.manager:
            print("❌ Sistema de memoria no disponible")
            return
        
        print("\n" + "="*70)
        print("💬 NUEVA CONVERSACIÓN")
        print("="*70)
        
        print("\nTipo:")
        print("1. Casual (general)")
        print("2. Investigación")
        print("3. Desarrollo")
        print("4. Médica")
        
        tipo = input("\nTipo (1-4, Enter=1): ").strip() or "1"
        
        categorias = {
            "1": "casual",
            "2": "investigacion",
            "3": "desarrollo",
            "4": "medica"
        }
        
        categoria = categorias.get(tipo, "casual")
        
        proyecto = input("Proyecto relacionado (Enter=ninguno): ").strip() or None
        
        # Crear conversación
        self.conversacion_actual = self.manager.nueva_conversacion(
            categoria=categoria,
            proyecto_relacionado=proyecto,
            auto_titulo=True
        )
        
        print(f"\n✅ Nueva conversación iniciada")
        print("="*70 + "\n")
    
    def _mostrar_contexto(self):
        """Muestra contexto de conversación actual"""
        if not self.manager or not self.conversacion_actual:
            print("❌ No hay conversación activa")
            return
        
        import sqlite3
        conn = sqlite3.connect(str(self.manager.db_path))
        cursor = conn.cursor()
        
        # Obtener info de conversación
        cursor.execute('''
            SELECT titulo, categoria, num_mensajes, proyecto_relacionado
            FROM conversaciones WHERE id = ?
        ''', (self.conversacion_actual,))
        
        info = cursor.fetchone()
        
        if info:
            print("\n" + "="*70)
            print("📋 CONTEXTO ACTUAL")
            print("="*70)
            print(f"\nConversación: {info[0]}")
            print(f"Categoría: {info[1]}")
            print(f"Mensajes: {info[2]}")
            if info[3]:
                print(f"Proyecto: {info[3]}")
        
        # Obtener contexto guardado
        cursor.execute('''
            SELECT clave, valor FROM contexto_conversacion
            WHERE conversacion_id = ?
        ''', (self.conversacion_actual,))
        
        contexto = cursor.fetchall()
        
        if contexto:
            print("\nDatos guardados:")
            for clave, valor in contexto:
                print(f"  • {clave}: {valor}")
        
        conn.close()
        print()
    
    def _mostrar_ayuda(self):
        """Muestra ayuda completa"""
        print("\n" + "="*70)
        print("📖 AYUDA - TARS ASISTENTE INTELIGENTE")
        print("="*70)
        print("\n🎯 COMANDOS BÁSICOS:")
        print("  /memoria       - Ver y cambiar entre conversaciones")
        print("  /nueva         - Iniciar nueva conversación")
        print("  /contexto      - Ver información de conversación actual")
        print("  /stats         - Estadísticas generales")
        print("  /ayuda         - Mostrar esta ayuda")
        print("  /salir         - Guardar y salir")
        
        print("\n🕸️  COMANDOS DE GRAFO DE CONOCIMIENTO:")
        print("  /conclusiones  - Guardar conclusiones de esta conversación")
        print("  /vincular      - Vincular con otra conversación")
        print("  /integrar      - Crear conversación integradora")
        print("  /grafo         - Ver grafo de conocimiento")
        
        print("\n💬 RETOMAR CONVERSACIONES:")
        print("  Solo di frases como:")
        print("    • 'Volvamos a la conversación sobre motores'")
        print("    • 'Regresemos al tema del exoesqueleto'")
        print("    • 'Continuemos con el análisis de papers'")
        print("    • 'Retomemos donde hablábamos de torque'")
        print("    • 'Sigamos con el diseño mecánico'")
        
        print("\n🔍 PALABRAS CLAVE DETECTADAS:")
        print("  • volvamos, regresemos, retomemos")
        print("  • vamos a seguir, sigamos, continuemos")
        print("  • recupera, abre, carga (+ 'conversación')")
        print("  • donde estábamos, aquella conversación")
        
        print("\n🧠 SISTEMA DE MEMORIA EPISÓDICA:")
        print("  • Cada conversación es una unidad semántica independiente")
        print("  • Puedes vincular conversaciones explícitamente")
        print("  • Las conversaciones integradoras combinan conocimiento")
        print("  • El grafo preserva trazabilidad y evita contaminación")
        print("  • TÚ supervisas qué conocimiento se integra (no automático)")
        
        print("\n💡 TIPS:")
        print("  • TARS guarda TODO automáticamente")
        print("  • Cada mensaje se guarda al instante")
        print("  • Puedes retomar conversaciones de hace días/semanas")
        print("  • Busca por palabras clave del tema")
        print("  • Guarda conclusiones para reutilizar conocimiento")
        print("\n" + "="*70 + "\n")
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas de uso"""
        if not self.manager:
            print("❌ Sistema de memoria no disponible")
            return
        
        stats = self.manager.estadisticas_generales()
        
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS DE USO")
        print("="*70)
        
        print(f"\n📈 General:")
        print(f"  Total conversaciones: {stats['total_conversaciones']}")
        print(f"  Total mensajes: {stats['total_mensajes']}")
        
        if stats.get('por_categoria'):
            print(f"\n📁 Por Categoría:")
            for cat, count in stats['por_categoria'].items():
                print(f"  • {cat.title()}: {count}")
        
        if stats.get('conversacion_mas_larga'):
            print(f"\n🏆 Conversación más larga:")
            print(f"  {stats['conversacion_mas_larga']['titulo']}")
            print(f"  {stats['conversacion_mas_larga']['mensajes']} mensajes")
        
        print()
    
    def _guardar_conclusiones(self):
        """Guarda conclusiones de la conversación actual"""
        if not self.manager or not self.conversacion_actual:
            print("❌ No hay conversación activa")
            return
        
        print("\n" + "="*70)
        print("💡 GUARDAR CONCLUSIONES")
        print("="*70)
        print("\nEstas conclusiones permitirán reutilizar el conocimiento")
        print("de esta conversación en futuras integraciones.")
        
        print("\nConclusiones principales (una por línea, Enter vacío para terminar):")
        conclusiones = []
        
        while True:
            linea = input("  • ").strip()
            if not linea:
                break
            conclusiones.append(linea)
        
        if not conclusiones:
            print("\n⚠️  No se guardaron conclusiones")
            return
        
        print("\nResultados obtenidos (opcional, Enter vacío para omitir):")
        resultados = []
        
        while True:
            linea = input("  ✓ ").strip()
            if not linea:
                break
            resultados.append(linea)
        
        conclusiones_texto = '\n'.join(conclusiones)
        resultados_texto = '\n'.join(resultados) if resultados else None
        
        self.manager.actualizar_conclusiones(
            self.conversacion_actual,
            conclusiones_texto,
            resultados_texto
        )
        
        print("\n✅ Conclusiones guardadas exitosamente")
        print("   Ahora esta conversación puede ser referenciada en integraciones")
    
    def _vincular_conversacion(self):
        """Vincula conversación actual con otra"""
        if not self.manager or not self.conversacion_actual:
            print("❌ No hay conversación activa")
            return
        
        print("\n" + "="*70)
        print("🔗 VINCULAR CONVERSACIONES")
        print("="*70)
        
        # Mostrar conversaciones recientes
        print("\nConversaciones disponibles:")
        conversaciones = self.manager.listar_conversaciones(estado="activa", limit=10)
        
        for i, conv in enumerate(conversaciones, 1):
            if conv['id'] != self.conversacion_actual:
                print(f"{i}. {conv['id']}: {conv['titulo']}")
        
        destino = input("\nID de conversación a vincular (o Enter para cancelar): ").strip()
        
        if not destino:
            return
        
        print("\nTipo de relación:")
        print("  1. relacionada    - Temas relacionados")
        print("  2. continua       - Una continúa la otra")
        print("  3. complementa    - Información complementaria")
        print("  4. contradice     - Información contradictoria")
        print("  5. depende        - Requiere contexto de la otra")
        print("  6. converge       - Conclusiones similares")
        print("  7. diverge        - Conclusiones diferentes")
        
        tipo_num = input("\nTipo (1-7, Enter=1): ").strip() or "1"
        
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
        
        exito = self.manager.vincular_conversaciones(
            self.conversacion_actual,
            destino,
            tipo,
            desc,
            int(rel)
        )
        
        if exito:
            print("\n✅ Conversaciones vinculadas exitosamente")
        else:
            print("\n❌ Error al vincular")
    
    def _crear_integradora(self):
        """Crea conversación integradora"""
        if not self.manager:
            print("❌ Sistema de memoria no disponible")
            return
        
        print("\n" + "="*70)
        print("🔗 CREAR CONVERSACIÓN INTEGRADORA")
        print("="*70)
        print("\nUna conversación integradora combina conocimiento de")
        print("múltiples conversaciones independientes, manteniendo trazabilidad.")
        
        # Mostrar conversaciones
        print("\nConversaciones disponibles:")
        conversaciones = self.manager.listar_conversaciones(estado="activa", limit=15)
        
        for i, conv in enumerate(conversaciones, 1):
            print(f"{i}. {conv['id']}: {conv['titulo']} [{conv['categoria']}]")
        
        print("\nIDs de conversaciones a integrar (separados por comas):")
        ids = input("IDs: ").strip().split(',')
        ids = [i.strip() for i in ids if i.strip()]
        
        if len(ids) < 2:
            print("\n❌ Se requieren al menos 2 conversaciones")
            return
        
        # Análisis de convergencia
        print("\n🔍 Analizando convergencias...")
        analisis = self.manager.analizar_convergencias(ids)
        
        if 'error' not in analisis:
            print(f"\n📊 Temas comunes: {len(analisis['temas_comunes'])}")
            if analisis['temas_comunes']:
                print("   Principales:")
                for tema in analisis['temas_comunes'][:5]:
                    print(f"      • {tema['palabra']} ({tema['frecuencia']} veces)")
        
        titulo = input("\nTítulo de la integración: ").strip()
        objetivo = input("Objetivo (por qué integrar estas conversaciones): ").strip()
        
        if not titulo or not objetivo:
            print("\n❌ Título y objetivo son requeridos")
            return
        
        confirmar = input("\n¿Crear conversación integradora? (s/n): ").lower()
        
        if confirmar == 's':
            conv_id = self.manager.crear_conversacion_integradora(
                titulo=titulo,
                objetivo=objetivo,
                conversaciones_base=ids,
                categoria="sintesis"
            )
            
            print(f"\n✅ Conversación integradora creada: {conv_id}")
            print("   Puedes cambiar a ella con /memoria")
    
    def _mostrar_grafo(self):
        """Muestra información del grafo de conocimiento"""
        if not self.manager:
            print("❌ Sistema de memoria no disponible")
            return
        
        grafo = self.manager.obtener_grafo_conocimiento()
        
        print("\n" + "="*70)
        print("🕸️  GRAFO DE CONOCIMIENTO")
        print("="*70)
        
        stats = grafo['estadisticas']
        print(f"\n📊 Estadísticas:")
        print(f"   • Conversaciones: {stats['num_nodos']}")
        print(f"   • Relaciones: {stats['num_aristas']}")
        print(f"   • Integradoras: {stats['nodos_integradores']}")
        print(f"   • Independientes: {stats['nodos_independientes']}")
        
        if self.conversacion_actual:
            print(f"\n🔍 Conversación actual: {self.conversacion_actual}")
            
            relaciones = self.manager.obtener_conversaciones_relacionadas(
                self.conversacion_actual
            )
            
            if relaciones['total'] > 0:
                print(f"   • Relacionadas: {relaciones['total']}")
                print(f"     - Salientes: {len(relaciones['salientes'])}")
                print(f"     - Entrantes: {len(relaciones['entrantes'])}")
            else:
                print(f"   • Sin relaciones (independiente)")
        
        print("\n💡 Usa 'python grafo_conocimiento.py' para exploración completa")
    
    def generar_respuesta(self, mensaje: str) -> str:
        """Genera respuesta usando TARS o simulada"""
        if self.tars:
            # Usar TARS real
            respuesta = self.tars.generar_respuesta(mensaje)
            return respuesta
        else:
            # Respuesta simulada
            return f"[TARS simulado]: Procesando '{mensaje[:50]}...'"
    
    def chat_loop(self):
        """Loop principal de chat"""
        self.mostrar_banner()
        
        while True:
            try:
                # Prompt
                mensaje = input("> ").strip()
                
                if not mensaje:
                    continue
                
                # Verificar comando especial
                if self.procesar_comando(mensaje):
                    break  # /salir
                
                if mensaje.startswith('/'):
                    continue  # Otros comandos
                
                # Guardar mensaje del usuario
                if self.manager and self.conversacion_actual:
                    self.manager.agregar_mensaje(
                        self.conversacion_actual,
                        "user",
                        mensaje
                    )
                
                # Detectar si quiere nueva conversación o cambiar tema
                if self.detectar_intencion_nueva_conversacion(mensaje):
                    print("\n🔄 Detectado: Quieres cambiar de tema o iniciar conversación nueva\n")
                    self._mostrar_opciones_nueva_conversacion()
                    continue
                
                # Detectar intención de retomar conversación
                if self.detectar_y_procesar_intencion(mensaje):
                    # Si se procesó intención de retomar, pedir siguiente mensaje
                    continue
                
                # Generar respuesta
                print("\nTARS: ", end='', flush=True)
                respuesta = self.generar_respuesta(mensaje)
                print(respuesta)
                
                # Hablar respuesta si voz está activa
                if self.voz_activa and self.voz:
                    self.voz.hablar(respuesta)
                
                print()
                
                # Guardar respuesta
                if self.manager and self.conversacion_actual:
                    self.manager.agregar_mensaje(
                        self.conversacion_actual,
                        "tars",
                        respuesta
                    )
            
            except KeyboardInterrupt:
                print("\n\n💾 Guardando...")
                if self.manager and self.conversacion_actual:
                    self.manager.guardar_contexto(
                        self.conversacion_actual,
                        "ultima_sesion",
                        datetime.now().isoformat()
                    )
                print("👋 ¡Hasta pronto!")
                break
            
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    asistente = TarsAsistenteInteligente()
    asistente.chat_loop()


if __name__ == "__main__":
    main()
