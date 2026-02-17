"""
Advanced statistics for the knowledge graph database.
"""
import sqlite3
from pathlib import Path

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
