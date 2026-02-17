"""
CLI entry point for database migration, verification, and statistics.
"""
import sys
from migration.migration import migrar_base_datos
from migration.verification import verificar_migracion
from migration.statistics import estadisticas_avanzadas

if __name__ == "__main__":
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
