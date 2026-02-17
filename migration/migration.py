"""
Database migration logic for knowledge graph schema.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

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
