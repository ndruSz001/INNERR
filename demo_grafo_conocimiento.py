#!/usr/bin/env python3
"""
demo_grafo_conocimiento.py
-------------------------
Demostración del Sistema de Grafo de Conocimiento de TARS.
Crea conversaciones de ejemplo, simula escenarios de investigación y muestra las capacidades del grafo.

Uso:
    python3 demo_grafo_conocimiento.py

Salida:
    Muestra en consola el flujo de conversaciones, conclusiones y relaciones en el grafo de conocimiento.

Autoría: Proyecto TARS (ver AUTORÍA_Y_LICENCIA.md)
"""

from conversation_manager import ConversationManager
from conversation_manager.graph import (
    crear_conversacion_integradora,
    vincular_conversaciones,
    obtener_conversaciones_relacionadas,
    actualizar_conclusiones,
    analizar_convergencias,
    obtener_grafo_conocimiento
)
from datetime import datetime, timedelta
import json


def crear_ejemplo_completo():
    """
    Crea un ejemplo completo de investigación sobre exoesqueleto
    """
    manager = ConversationManager()
    
    print("\n" + "="*70)
    print("DEMO: Sistema de Grafo de Conocimiento - TARS")
    print("="*70)
    print("\n🎯 Escenario: Desarrollo de exoesqueleto de rodilla")
    print("   Simula 3 meses de investigación fragmentada")
    
    # ====================================================================
    # MES 1: Investigaciones independientes
    # ====================================================================
    
    print("\n" + "="*70)
    print("📅 MES 1: Investigaciones independientes")
    print("="*70)
    
    # Conversación 1: Análisis de torque
    print("\n1️⃣  Análisis de torque requerido...")
    conv_torque = manager.nueva_conversacion(
        titulo="Análisis torque para rodilla",
        categoria="investigacion",
        descripcion="Cálculo de torque necesario basado en biomecánica",
        proyecto_relacionado="exoesqueleto_rodilla_v1",
        tags=["biomecánica", "torque", "cálculos"],
        auto_titulo=False
    )
    
    # Simular conversación
    manager.agregar_mensaje(conv_torque, "user", 
        "¿Qué torque necesito para asistir flexión/extensión de rodilla?")
    manager.agregar_mensaje(conv_torque, "tars",
        "Según literatura biomecánica, torque pico en rodilla durante marcha normal: ~60-80 Nm. "
        "Para asistencia parcial (50%), necesitas ~30-40 Nm de torque efectivo.")
    
    manager.agregar_mensaje(conv_torque, "user",
        "¿Qué motor recomiendas?")
    manager.agregar_mensaje(conv_torque, "tars",
        "Motor Maxon EC90 (90W) con reductor planetario 1:50. "
        "Torque salida: 12 Nm continuo, 36 Nm pico. "
        "Peso: 450g. Eficiencia: 85%.")
    
    # Guardar conclusiones
    actualizar_conclusiones(
        manager.db_path,
        conv_torque,
        "Motor Maxon EC90 con reductor 1:50 es óptimo para asistencia parcial. "
        "Torque efectivo: 12 Nm continuo (suficiente para 30% asistencia). "
        "Relación peso/potencia: excelente.",
        "Motor seleccionado: Maxon EC90 flat\n"
        "Reductor: 1:50 planetario\n"
        "Torque: 12 Nm continuo\n"
        "Peso: 450g\n"
        "Costo estimado: $800"
    )
    
    print(f"   ✅ Conversación creada: {conv_torque}")
    print(f"   💡 Conclusiones guardadas")
    
    # Conversación 2: Selección de sensores
    print("\n2️⃣  Selección de sensores...")
    conv_sensores = manager.nueva_conversacion(
        titulo="Sensores para control exoesqueleto",
        categoria="desarrollo",
        descripcion="IMUs, encoders, sensores de fuerza",
        proyecto_relacionado="exoesqueleto_rodilla_v1",
        tags=["sensores", "imu", "encoders"],
        auto_titulo=False
    )
    
    manager.agregar_mensaje(conv_sensores, "user",
        "¿Qué sensores necesito para control en tiempo real?")
    manager.agregar_mensaje(conv_sensores, "tars",
        "Sistema sensorial mínimo:\n"
        "1. IMU (MPU9250): Orientación muslo/pierna (2 unidades)\n"
        "2. Encoder absoluto: Ángulo articulación rodilla\n"
        "3. Células de carga: Fuerza interacción usuario (opcional pero recomendado)")
    
    actualizar_conclusiones(
        manager.db_path,
        conv_sensores,
        "IMUs MPU9250 para cinemática, encoder magnético AS5048 para posición absoluta. "
        "Frecuencia muestreo: 200 Hz mínimo.",
        "IMU: MPU9250 (2x) - $15 c/u\n"
        "Encoder: AS5048A magnético - $25\n"
        "Total sensores: ~$55"
    )
    
    print(f"   ✅ Conversación creada: {conv_sensores}")
    
    # Conversación 3: Diseño mecánico
    print("\n3️⃣  Diseño mecánico de estructura...")
    conv_mecanico = manager.nueva_conversacion(
        titulo="Diseño mecánico estructura rodilla",
        categoria="desarrollo",
        descripcion="Diseño de estructura que integra motor y sensores",
        proyecto_relacionado="exoesqueleto_rodilla_v1",
        tags=["CAD", "estructural", "diseño"],
        auto_titulo=False
    )
    
    manager.agregar_mensaje(conv_mecanico, "user",
        "Necesito diseñar la estructura que monte el motor")
    manager.agregar_mensaje(conv_mecanico, "tars",
        "Recomendaciones:\n"
        "- Aluminio 7075 para componentes estructurales (alta resistencia/peso)\n"
        "- Rodamientos de bolas en eje articulación\n"
        "- Transmisión por correa dentada (menor backlash que engranajes)")
    
    actualizar_conclusiones(
        manager.db_path,
        conv_mecanico,
        "Estructura modular en aluminio 7075. "
        "Transmisión por correa HTD5M. "
        "Peso estimado estructura: 600g.",
        "Material: Aluminio 7075-T6\n"
        "Rodamientos: 2x 6204 sellados\n"
        "Correa: HTD5M 15mm ancho\n"
        "Poleas: 20T motor, 100T salida (1:5 adicional)"
    )
    
    print(f"   ✅ Conversación creada: {conv_mecanico}")
    
    # ====================================================================
    # MES 2: Más investigaciones independientes
    # ====================================================================
    
    print("\n" + "="*70)
    print("📅 MES 2: Investigaciones adicionales")
    print("="*70)
    
    # Conversación 4: Control
    print("\n4️⃣  Estrategia de control...")
    conv_control = manager.nueva_conversacion(
        titulo="Control asistivo impedancia variable",
        categoria="investigacion",
        descripcion="Algoritmo de control para asistencia adaptativa",
        proyecto_relacionado="exoesqueleto_rodilla_v1",
        tags=["control", "impedancia", "algoritmos"],
        auto_titulo=False
    )
    
    manager.agregar_mensaje(conv_control, "user",
        "¿Qué estrategia de control usar?")
    manager.agregar_mensaje(conv_control, "tars",
        "Control de impedancia variable:\n"
        "- Detectar fase de marcha (stance/swing)\n"
        "- Ajustar rigidez según fase\n"
        "- Usar IMUs para estimar fase en tiempo real")
    
    actualizar_conclusiones(
        manager.db_path,
        conv_control,
        "Control de impedancia con detección de fase vía IMU. "
        "Rigidez alta en stance (soporte), baja en swing (movimiento libre).",
        "Algoritmo: Impedancia variable\n"
        "Frecuencia control: 200 Hz\n"
        "Microcontrolador: Teensy 4.1 (600 MHz)"
    )
    
    print(f"   ✅ Conversación creada: {conv_control}")
    
    # Conversación 5: Baterías
    print("\n5️⃣  Sistema de alimentación...")
    conv_baterias = manager.nueva_conversacion(
        titulo="Sistema de baterías LiPo",
        categoria="desarrollo",
        descripcion="Dimensionamiento de baterías para 2h autonomía",
        proyecto_relacionado="exoesqueleto_rodilla_v1",
        tags=["baterías", "potencia", "autonomía"],
        auto_titulo=False
    )
    
    manager.agregar_mensaje(conv_baterias, "user",
        "¿Qué batería necesito?")
    manager.agregar_mensaje(conv_baterias, "tars",
        "Motor: 90W pico, ~30W promedio marcha normal\n"
        "Para 2h autonomía: 60 Wh\n"
        "Batería LiPo 4S (14.8V) 4000 mAh → 59 Wh (suficiente)")
    
    actualizar_conclusiones(
        manager.db_path,
        conv_baterias,
        "Batería LiPo 4S 4000 mAh (59 Wh) da 2h autonomía con margen.",
        "Batería: Turnigy 4S 4000 mAh 30C\n"
        "Peso: 380g\n"
        "Costo: $60\n"
        "Autonomía estimada: 2-2.5h"
    )
    
    print(f"   ✅ Conversación creada: {conv_baterias}")
    
    # ====================================================================
    # MES 3: Usuario detecta convergencias y crea integradora
    # ====================================================================
    
    print("\n" + "="*70)
    print("📅 MES 3: Integración de conocimiento")
    print("="*70)
    
    # Primero, vincular conversaciones relacionadas
    print("\n🔗 Vinculando conversaciones relacionadas...")
    
    # Torque → Mecánico (el diseño mecánico depende del motor seleccionado)
    vincular_conversaciones(
        manager.db_path,
        conv_torque, conv_mecanico,
        "depende",
        "El diseño mecánico debe acomodar motor Maxon EC90",
        9
    )
    
    # Sensores → Control (control usa sensores)
    vincular_conversaciones(
        manager.db_path,
        conv_sensores, conv_control,
        "depende",
        "Algoritmo de control usa IMUs para detección de fase",
        10
    )
    
    # Torque → Baterías (potencia motor determina batería)
    vincular_conversaciones(
        manager.db_path,
        conv_torque, conv_baterias,
        "complementa",
        "Potencia motor determina capacidad batería necesaria",
        8
    )
    
    print("   ✅ 3 relaciones creadas")
    
    # Analizar convergencias
    print("\n🔍 Analizando convergencias...")
    
    todas_conversaciones = [conv_torque, conv_sensores, conv_mecanico, 
                           conv_control, conv_baterias]
    
    analisis = analizar_convergencias(manager.db_path, todas_conversaciones)
    
    print(f"\n   📊 Resultado del análisis:")
    print(f"      • Conversaciones analizadas: {analisis['num_conversaciones']}")
    print(f"      • Temas comunes: {len(analisis['temas_comunes'])}")
    
    if analisis['temas_comunes']:
        print(f"      • Top 3 temas:")
        for tema in analisis['temas_comunes'][:3]:
            print(f"         - {tema['palabra']} ({tema['frecuencia']} veces)")
    
    # Crear conversación integradora
    print("\n🔗 Creando conversación integradora...")
    
    conv_integradora = crear_conversacion_integradora(
        manager.db_path,
        "Especificación técnica completa - Exoesqueleto Rodilla v1",
        "Integrar todos los análisis de actuación, sensado, mecánica, "
        "control y potencia en una especificación técnica unificada "
        "que sirva como base para fabricación de prototipo.",
        todas_conversaciones,
        "sintesis",
        "Documento maestro que combina conclusiones de 5 "
        "investigaciones independientes realizadas durante 3 meses."
    )
    
    print(f"   ✅ Conversación integradora creada: {conv_integradora}")
    
    # Agregar mensaje en integradora que resume todo
    manager.agregar_mensaje(
        conv_integradora,
        "user",
        "Dame la especificación técnica completa del prototipo"
    )
    
    manager.agregar_mensaje(
        conv_integradora,
        "tars",
        "ESPECIFICACIÓN TÉCNICA - EXOESQUELETO RODILLA V1\n\n"
        "ACTUACIÓN (referencia: " + conv_torque + "):\n"
        "• Motor: Maxon EC90 flat, 90W\n"
        "• Reductor: Planetario 1:50\n"
        "• Transmisión adicional: Correa HTD5M 1:5\n"
        "• Torque efectivo: 12 Nm continuo\n"
        "• Peso actuación: 450g\n\n"
        "SENSADO (referencia: " + conv_sensores + "):\n"
        "• IMUs: 2x MPU9250 (muslo/pierna)\n"
        "• Encoder: AS5048A magnético absoluto\n"
        "• Frecuencia: 200 Hz\n"
        "• Peso sensores: ~50g\n\n"
        "ESTRUCTURA (referencia: " + conv_mecanico + "):\n"
        "• Material: Aluminio 7075-T6\n"
        "• Rodamientos: 2x 6204 sellados\n"
        "• Peso estructura: 600g\n\n"
        "CONTROL (referencia: " + conv_control + "):\n"
        "• Algoritmo: Impedancia variable\n"
        "• Detección de fase: IMU-based\n"
        "• Microcontrolador: Teensy 4.1\n"
        "• Frecuencia control: 200 Hz\n\n"
        "POTENCIA (referencia: " + conv_baterias + "):\n"
        "• Batería: LiPo 4S 4000 mAh (59 Wh)\n"
        "• Autonomía: 2-2.5h\n"
        "• Peso batería: 380g\n\n"
        "RESUMEN:\n"
        "• Peso total: ~1.5 kg\n"
        "• Costo componentes: ~$1000\n"
        "• Torque asistivo: 12 Nm continuo\n"
        "• Autonomía: 2+ horas\n"
        "• Listo para fabricación de prototipo"
    )
    
    # Guardar conclusiones de integradora
    actualizar_conclusiones(
        manager.db_path,
        conv_integradora,
        "Especificación técnica completa lista para prototipado. "
        "Sistema viable con componentes COTS. "
        "Peso y costo dentro de objetivos.",
        "Documento de especificación técnica completo\n"
        "BOM (Bill of Materials) definido\n"
        "Peso objetivo: 1.5 kg ✓\n"
        "Costo objetivo: <$1500 ✓\n"
        "Listo para fase de fabricación"
    )
    
    print(f"   💡 Especificación técnica guardada")
    
    # ====================================================================
    # Mostrar estadísticas finales
    # ====================================================================
    
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DEL GRAFO DE CONOCIMIENTO")
    print("="*70)
    
    grafo = obtener_grafo_conocimiento(manager.db_path)
    
    stats = grafo['estadisticas']
    print(f"\n✅ Grafo completo:")
    print(f"   • Nodos (conversaciones): {stats['num_nodos']}")
    print(f"   • Aristas (relaciones): {stats['num_aristas']}")
    print(f"   • Conversaciones integradoras: {stats['nodos_integradores']}")
    print(f"   • Conversaciones independientes: {stats['nodos_independientes']}")
    
    # Explorar integradora
    print(f"\n🔍 Conversación integradora '{conv_integradora}':")
    
    relaciones = obtener_conversaciones_relacionadas(manager.db_path, conv_integradora)
    
    print(f"   📖 Referencias (salientes): {len(relaciones['salientes'])}")
    for rel in relaciones['salientes']:
        print(f"      • {rel['tipo_relacion']}: {rel['titulo']}")
    
    print(f"\n💡 BENEFICIOS LOGRADOS:")
    print(f"   ✅ Conocimiento fragmentado → Especificación unificada")
    print(f"   ✅ 5 conversaciones independientes → 1 documento maestro")
    print(f"   ✅ Trazabilidad total: Cada dato sabe su origen")
    print(f"   ✅ Conversaciones originales preservadas sin modificar")
    print(f"   ✅ Reutilizable: Otras integraciones pueden usar mismas bases")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETADA")
    print("="*70)
    
    print(f"\n🎯 Siguiente paso:")
    print(f"   python grafo_conocimiento.py")
    print(f"   → Opción 2: Explorar '{conv_integradora}'")
    print(f"   → Opción 6: Exportar grafo a Graphviz")
    
    return {
        'conversaciones': todas_conversaciones,
        'integradora': conv_integradora,
        'grafo': grafo
    }


if __name__ == "__main__":
    resultado = crear_ejemplo_completo()
