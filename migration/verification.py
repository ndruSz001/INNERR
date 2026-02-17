"""
Database migration verification logic.
"""
import sqlite3
from pathlib import Path

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
