"""
CLI Interactiva - Interfaz de línea de comandos para TARS

Características:
  - Input/output en tiempo real
  - Colores para mejor legibilidad
  - Historial con arrow keys
  - Comandos especiales (/memory, /projects, etc)
  - Autocompletado
"""

import sys
import argparse
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TARSCLIApp:
    """Aplicación CLI interactiva para TARS"""
    
    def __init__(self, orchestrator=None):
        """
        Args:
            orchestrator: Instancia de Orchestrator
        """
        self.orchestrator = orchestrator
        self.user_id = "cli_user"
        self.conversation_id: Optional[str] = None
        self.running = False
        
        # Colores ANSI
        self.colors = {
            'HEADER': '\033[95m',
            'BLUE': '\033[94m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'RED': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """Agregar color a texto"""
        return f"{self.colors.get(color, '')}{text}{self.colors['ENDC']}"
    
    def print_header(self) -> None:
        """Imprimir header de bienvenida"""
        print("\n" + "="*70)
        print(self._colorize("🚀 TARS Interactive CLI - Sprint 2", "BOLD"))
        print("="*70)
        print("\nComandos disponibles:")
        print(f"  {self._colorize('/help', 'YELLOW')}          - Mostrar ayuda")
        print(f"  {self._colorize('/memory', 'YELLOW')}        - Ver estado de memoria")
        print(f"  {self._colorize('/projects', 'YELLOW')}      - Listar proyectos")
        print(f"  {self._colorize('/health', 'YELLOW')}        - Health check")
        print(f"  {self._colorize('/clear', 'YELLOW')}         - Limpiar pantalla")
        print(f"  {self._colorize('/exit o quit', 'YELLOW')}   - Salir")
        print("\n")
    
    def run(self) -> None:
        """Iniciar CLI interactiva"""
        self.running = True
        self.print_header()
        
        while self.running:
            try:
                # Prompt
                prompt = self._colorize("TARS> ", "BLUE")
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Procesar input
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    self._handle_query(user_input)
            
            except KeyboardInterrupt:
                print("\n")
                self._handle_command("/exit")
            except Exception as e:
                print(f"\n{self._colorize(f'❌ Error: {e}', 'RED')}\n")
                logger.exception("Unhandled exception")
    
    def _handle_command(self, command: str) -> None:
        """Procesar comando especial"""
        cmd = command.split()[0].lower()
        
        if cmd == '/help':
            self._show_help()
        elif cmd == '/memory':
            self._show_memory_status()
        elif cmd == '/projects':
            self._show_projects()
        elif cmd == '/health':
            self._show_health()
        elif cmd == '/clear':
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd in ['/exit', '/quit']:
            self.running = False
            print(f"\n{self._colorize('👋 Hasta luego!', 'GREEN')}\n")
        else:
            print(f"{self._colorize('⚠️  Comando desconocido', 'YELLOW')}: {cmd}")
            print(f"Usa {self._colorize('/help', 'YELLOW')} para ver comandos disponibles\n")
    
    def _handle_query(self, query: str) -> None:
        """Procesar query de usuario"""
        if not self.orchestrator:
            print(f"{self._colorize('❌ Orchestrator no disponible', 'RED')}\n")
            return
        
        print(f"{self._colorize('⏳ Procesando...', 'YELLOW')}")
        
        try:
            result = self.orchestrator.process(
                query=query,
                user_id=self.user_id,
                conversation_id=self.conversation_id
            )
            
            # Guardar conversation ID
            self.conversation_id = result.get('conversation_id')
            
            # Mostrar respuesta
            response = result.get('response', '')
            routing_type = result.get('routing_type', 'unknown')
            proc_time = result.get('processing_time', 0)
            
            print(f"\n{self._colorize('TARS:', 'GREEN')} {response}\n")
            
            # Metadatos
            meta = f"[{routing_type} | {proc_time:.2f}s]"
            print(f"{self._colorize(meta, 'YELLOW')}\n")
        
        except Exception as e:
            print(f"\n{self._colorize(f'❌ Error: {e}', 'RED')}\n")
            logger.error(f"Error procesando query: {e}")
    
    def _show_help(self) -> None:
        """Mostrar ayuda detallada"""
        help_text = f"""
{self._colorize('TARS CLI - Ayuda', 'BOLD')}

{self._colorize('COMANDOS:', 'HEADER')}
  /help          Mostrar esta ayuda
  /memory        Ver estadísticas de memoria
  /projects      Listar proyectos almacenados
  /health        Ver salud del sistema
  /clear         Limpiar pantalla
  /exit, /quit   Salir de la aplicación

{self._colorize('USO:', 'HEADER')}
  - Escribe tu pregunta directamente (sin /)
  - Los comandos comienzan con /
  - Usa arrow keys para historial (si readline está disponible)

{self._colorize('EJEMPLOS:', 'HEADER')}
  TARS> Hola, ¿cómo estás?
  TARS> ¿Cuál es la capital de Francia?
  TARS> /memory
  TARS> /projects

{self._colorize('NOTAS:', 'HEADER')}
  - Las conversaciones se guardan automáticamente
  - Los proyectos se indexan para búsqueda rápida
  - Los cambios se sintetizan cada noche a las 02:00 AM
"""
        print(help_text)
    
    def _show_memory_status(self) -> None:
        """Mostrar estado de memoria"""
        if not self.orchestrator or not self.orchestrator.conversation_store:
            print(f"{self._colorize('⚠️  Memoria no disponible', 'YELLOW')}\n")
            return
        
        stats = self.orchestrator.conversation_store.get_stats()
        
        print(f"\n{self._colorize('📊 ESTADO DE MEMORIA', 'BOLD')}")
        print("-" * 50)
        print(f"  Conversaciones activas: {stats['total_conversations']}")
        print(f"  Usuarios únicos:       {stats['total_users']}")
        print(f"  Mensajes totales:      {stats['total_messages']}")
        print(f"  Msgs por conversación: {stats['avg_messages_per_conv']:.1f}")
        print()
    
    def _show_projects(self) -> None:
        """Listar proyectos"""
        if not self.orchestrator or not self.orchestrator.project_store:
            print(f"{self._colorize('⚠️  Project store no disponible', 'YELLOW')}\n")
            return
        
        projects = self.orchestrator.project_store.list_all_projects()
        
        if not projects:
            print(f"\n{self._colorize('📭 Sin proyectos almacenados', 'YELLOW')}\n")
            return
        
        print(f"\n{self._colorize('📁 PROYECTOS ALMACENADOS', 'BOLD')}")
        print("-" * 70)
        
        for i, proj in enumerate(projects[:10], 1):
            name = proj.get('name', 'Sin nombre')[:30]
            tags = ", ".join(proj.get('tags', []))[:20]
            print(f"  {i}. {self._colorize(name, 'BLUE')}")
            if tags:
                print(f"     Tags: {tags}")
        
        if len(projects) > 10:
            print(f"  ... y {len(projects) - 10} más")
        
        print()
    
    def _show_health(self) -> None:
        """Mostrar health status"""
        print(f"\n{self._colorize('🏥 HEALTH CHECK', 'BOLD')}")
        print("-" * 50)
        
        components = {
            'Orchestrator': bool(self.orchestrator),
            'Conversation Store': bool(self.orchestrator and self.orchestrator.conversation_store),
            'Project Store': bool(self.orchestrator and self.orchestrator.project_store),
            'Inference Engine': bool(self.orchestrator and self.orchestrator.inference_engine),
            'Vector Index': bool(self.orchestrator and hasattr(self.orchestrator, 'semantic_index'))
        }
        
        for component, healthy in components.items():
            status = self._colorize("✅ OK", "GREEN") if healthy else self._colorize("❌ FAIL", "RED")
            print(f"  {component:.<30} {status}")
        
        print()


# ========== Entry point CLI ==========

def main():
    """Función principal para CLI"""
    parser = argparse.ArgumentParser(
        description='TARS Interactive CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s                    # Iniciar CLI interactiva
  %(prog)s --query "Hola"     # Procesar query única
  %(prog)s --help             # Mostrar esta ayuda
        """
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Query a procesar (sin iniciar CLI interactiva)'
    )
    
    parser.add_argument(
        '--user',
        type=str,
        default='cli_user',
        help='User ID para las queries'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Nivel de logging'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    # Crear orchestrator
    try:
        from orchestrator.main import Orchestrator
        
        orch = Orchestrator(
            enable_memory=True,
            enable_inference=False,  # Sin LLM en CLI
            enable_semantic=False
        )
        
        # Crear CLI
        cli = TARSCLIApp(orchestrator=orch)
        
        if args.query:
            # Modo query única
            print(f"\nProcesando: {args.query}\n")
            cli._handle_query(args.query)
        else:
            # Modo interactivo
            cli.run()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
