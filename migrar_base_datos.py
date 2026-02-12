#!/usr/bin/env python3
"""
Migración de Base de Datos
Actualiza schema existente para soportar grafo de conocimiento
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def migrar_base_datos(db_path="tars_lifelong/conversations.db"):
    """
    Migra base de datos existente al nuevo schema con grafo de conocimiento
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"⚠️  Base de datos no existe: {db_path}")
        print("   Se creará automáticamente al usar ConversationManager")
        return
    
    print(f"\n🔄 Migrando base de datos: {db_path}")
    
    # Backup
    backup_path = db_file.with_suffix('.db.backup')
    import shutil
    shutil.copy2(db_file, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    # Verificar columnas existentes
    cursor.execute("PRAGMA table_info(conversaciones)")
    columnas_existentes = {row[1] for row in cursor.fetchall()}
    
    print(f"\n📊 Columnas existentes: {len(columnas_existentes)}")
    
    # Agregar nuevas columnas si no existen
    nuevas_columnas = {
        'es_integradora': 'INTEGER DEFAULT 0',
        'objetivo': 'TEXT',
        'conclusiones': 'TEXT',
        'resultados': 'TEXT'
    }
    
    for columna, tipo in nuevas_columnas.items():
        if columna not in columnas_existentes:
            try:
                cursor.execute(f'''
                    ALTER TABLE conversaciones
                    ADD COLUMN {columna} {tipo}
                ''')
                print(f"✅ Columna agregada: {columna}")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Error al agregar {columna}: {e}")
    
    # Crear tabla de relaciones si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relaciones_conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversacion_origen TEXT,
            conversacion_destino TEXT,
            tipo_relacion TEXT,
            descripcion TEXT,
            relevancia INTEGER DEFAULT 5,
            fecha_vinculacion TEXT,
            metadata TEXT,
            FOREIGN KEY (conversacion_origen) REFERENCES conversaciones(id),
            FOREIGN KEY (conversacion_destino) REFERENCES conversaciones(id)
        )
    ''')
    print("✅ Tabla relaciones_conversaciones verificada")
    
    # Crear índices si no existen
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relaciones_origen 
            ON relaciones_conversaciones(conversacion_origen)
        ''')
        print("✅ Índice idx_relaciones_origen creado")
    except:
        pass
    
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relaciones_destino 
            ON relaciones_conversaciones(conversacion_destino)
        ''')
        print("✅ Índice idx_relaciones_destino creado")
    except:
        pass
    
    conn.commit()
    
    # Estadísticas post-migración
    cursor.execute('SELECT COUNT(*) FROM conversaciones')
    num_conversaciones = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM relaciones_conversaciones')
    num_relaciones = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Migración completada")
    print(f"\n📊 Estadísticas:")
    print(f"   • Conversaciones: {num_conversaciones}")
    print(f"   • Relaciones: {num_relaciones}")
    print(f"\n💡 La base de datos ahora soporta:")
    print(f"   • Conversaciones integradoras")
    print(f"   • Conclusiones y resultados")
    print(f"   • Relaciones entre conversaciones")
    print(f"   • Grafo de conocimiento completo")


def verificar_migracion(db_path="tars_lifelong/conversations.db"):
    """
    Verifica que la migración fue exitosa
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    print(f"\n🔍 Verificando migración...")
    
    # Verificar columnas
    cursor.execute("PRAGMA table_info(conversaciones)")
    columnas = {row[1] for row in cursor.fetchall()}
    
    columnas_requeridas = {'es_integradora', 'objetivo', 'conclusiones', 'resultados'}
    
    print(f"\n✅ Columnas en conversaciones:")
    for col in sorted(columnas):
        marcador = "🆕" if col in columnas_requeridas else "  "
        print(f"   {marcador} {col}")
    
    # Verificar tablas
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    ''')
    
    tablas = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Tablas en base de datos:")
    for tabla in tablas:
        marcador = "🆕" if tabla == 'relaciones_conversaciones' else "  "
        print(f"   {marcador} {tabla}")
    
    # Verificar índices
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='index' 
        ORDER BY name
    ''')
    
    indices = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Índices:")
    for idx in indices:
        if not idx.startswith('sqlite_'):
            marcador = "🆕" if 'relaciones' in idx else "  "
            print(f"   {marcador} {idx}")
    
    conn.close()
    
    # Verificación final
    faltantes = columnas_requeridas - columnas
    
    if faltantes:
        print(f"\n❌ Faltan columnas: {faltantes}")
        return False
    
    if 'relaciones_conversaciones' not in tablas:
        print(f"\n❌ Falta tabla: relaciones_conversaciones")
        return False
    
    print(f"\n✅ Migración verificada correctamente")
    return True


def estadisticas_avanzadas(db_path="tars_lifelong/conversations.db"):
    """
    Muestra estadísticas avanzadas del grafo
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    print(f"\n📊 ESTADÍSTICAS DEL GRAFO DE CONOCIMIENTO")
    print("=" * 60)
    
    # Conversaciones por tipo
    cursor.execute('''
        SELECT 
            CASE WHEN es_integradora = 1 THEN 'Integradora' ELSE 'Normal' END as tipo,
            COUNT(*) as cantidad
        FROM conversaciones
        WHERE estado = 'activa'
        GROUP BY es_integradora
    ''')
    
    print("\n📁 Por tipo:")
    for tipo, cantidad in cursor.fetchall():
        print(f"   • {tipo}: {cantidad}")
    
    # Conversaciones con conclusiones
    cursor.execute('''
        SELECT COUNT(*) 
        FROM conversaciones 
        WHERE conclusiones IS NOT NULL AND conclusiones != ''
    ''')
    
    con_conclusiones = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM conversaciones')
    total = cursor.fetchone()[0]
    
    if total > 0:
        porcentaje = (con_conclusiones / total) * 100
        print(f"\n💡 Con conclusiones: {con_conclusiones}/{total} ({porcentaje:.1f}%)")
    
    # Relaciones por tipo
    cursor.execute('''
        SELECT tipo_relacion, COUNT(*) as cantidad
        FROM relaciones_conversaciones
        GROUP BY tipo_relacion
        ORDER BY cantidad DESC
    ''')
    
    relaciones = cursor.fetchall()
    
    if relaciones:
        print(f"\n🔗 Relaciones por tipo:")
        for tipo, cantidad in relaciones:
            print(f"   • {tipo}: {cantidad}")
    else:
        print(f"\n⚠️  Sin relaciones aún")
    
    # Nodos más conectados
    cursor.execute('''
        SELECT 
            c.id, c.titulo,
            (SELECT COUNT(*) FROM relaciones_conversaciones WHERE conversacion_origen = c.id) as salientes,
            (SELECT COUNT(*) FROM relaciones_conversaciones WHERE conversacion_destino = c.id) as entrantes
        FROM conversaciones c
        WHERE c.estado = 'activa'
        ORDER BY (salientes + entrantes) DESC
        LIMIT 5
    ''')
    
    top_conectados = cursor.fetchall()
    
    if top_conectados and top_conectados[0][2] + top_conectados[0][3] > 0:
        print(f"\n⭐ Top conversaciones conectadas:")
        for conv_id, titulo, sal, ent in top_conectados:
            if sal + ent > 0:
                print(f"   • {conv_id}: {titulo}")
                print(f"     {sal} salientes, {ent} entrantes = {sal + ent} total")
    
    # Conversaciones independientes
    cursor.execute('''
        SELECT COUNT(*)
        FROM conversaciones c
        WHERE c.estado = 'activa'
        AND NOT EXISTS (
            SELECT 1 FROM relaciones_conversaciones 
            WHERE conversacion_origen = c.id OR conversacion_destino = c.id
        )
    ''')
    
    independientes = cursor.fetchone()[0]
    
    print(f"\n🔵 Conversaciones independientes: {independientes}")
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("MIGRACIÓN DE BASE DE DATOS - TARS")
    print("Grafo de Conocimiento v2.0")
    print("="*60)
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "tars_lifelong/conversations.db"
    
    # Migrar
    migrar_base_datos(db_path)
    
    # Verificar
    if verificar_migracion(db_path):
        # Estadísticas
        estadisticas_avanzadas(db_path)
    
    print("\n✅ Proceso completado")
    print("\n💡 Ahora puedes usar:")
    print("   python tars_asistente.py       - Asistente con grafo")
    print("   python grafo_conocimiento.py   - Explorador de grafo")
