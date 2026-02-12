#!/usr/bin/env python3
"""
🧪 VALIDACION COMPLETA SPRINT 2

Este script valida que todos los componentes de Sprint 2 funcionen correctamente.
Incluye: Procesamiento, Infrastructure, API, CLI y tests de integración.

Ejecutar con:
    python3 validate_sprint2.py
"""

import sys
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Colores ANSI
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Imprime encabezado"""
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{title:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

def check_imports():
    """Valida que todos los imports funcionen"""
    print_header("1️⃣  VALIDANDO IMPORTS")
    
    modules = [
        # Sprint 1
        ("core.inference.inference_engine", "Inference Engine"),
        ("core.memory.conversation_store", "Conversation Store"),
        ("core.memory.project_store", "Project Store"),
        ("core.memory.semantic_index", "Semantic Index"),
        ("orchestrator.main", "Orchestrator"),
        
        # Sprint 2 - FASE 4
        ("processing.ingestion.document_ingester", "Document Ingester"),
        ("processing.embeddings.embedding_engine", "Embedding Engine"),
        ("processing.indexing.vector_index", "Vector Index"),
        
        # Sprint 2 - FASE 5
        ("infrastructure.logging.logger_config", "Logger Config"),
        ("infrastructure.monitoring.health_checker", "Health Checker"),
        ("infrastructure.jobs.scheduler", "Job Scheduler"),
        
        # Sprint 2 - FASE 6
        ("api.main", "FastAPI Main"),
        ("cli.main", "CLI Main"),
    ]
    
    success = 0
    failed = 0
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"  {GREEN}✅{RESET} {display_name:40} OK")
            success += 1
        except ImportError as e:
            print(f"  {RED}❌{RESET} {display_name:40} ERROR: {str(e)[:30]}")
            failed += 1
    
    print(f"\n{BLUE}Resultado:{RESET} {GREEN}{success} OK{RESET}, {RED}{failed} FALLOS{RESET}")
    return failed == 0

def check_dependencies():
    """Valida que las dependencias estén instaladas"""
    print_header("2️⃣  VALIDANDO DEPENDENCIAS")
    
    packages = [
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("apscheduler", "APScheduler"),
        ("requests", "Requests"),
    ]
    
    success = 0
    failed = 0
    
    for pkg_import, pkg_display in packages:
        try:
            __import__(pkg_import)
            print(f"  {GREEN}✅{RESET} {pkg_display:40} OK")
            success += 1
        except ImportError:
            print(f"  {RED}❌{RESET} {pkg_display:40} NO INSTALADO")
            failed += 1
    
    print(f"\n{BLUE}Resultado:{RESET} {GREEN}{success} OK{RESET}, {RED}{failed} FALLOS{RESET}")
    return failed == 0

def check_file_structure():
    """Valida estructura de directorios"""
    print_header("3️⃣  VALIDANDO ESTRUCTURA DE DIRECTORIOS")
    
    directories = [
        "core/inference",
        "core/memory",
        "core/apis",
        "orchestrator/routes",
        "orchestrator/planning",
        "orchestrator/synthesis",
        "processing/ingestion",
        "processing/embeddings",
        "processing/indexing",
        "infrastructure/logging",
        "infrastructure/monitoring",
        "infrastructure/jobs",
        "infrastructure/systemd",
        "api/routes",
        "cli",
        "tests",
    ]
    
    success = 0
    failed = 0
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            print(f"  {GREEN}✅{RESET} {directory:50} OK")
            success += 1
        else:
            print(f"  {RED}❌{RESET} {directory:50} NO EXISTE")
            failed += 1
    
    print(f"\n{BLUE}Resultado:{RESET} {GREEN}{success} OK{RESET}, {RED}{failed} FALLOS{RESET}")
    return failed == 0

def run_tests():
    """Ejecuta tests de integración"""
    print_header("4️⃣  EJECUTANDO TESTS DE INTEGRACION")
    
    env = {**dict(os.environ), "PYTHONPATH": "/home/ndrz02/keys_1"}
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                "tests/test_sprint2_integration.py"
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd="/home/ndrz02/keys_1"
        )
        
        # Buscar resultado en stdout
        if "TODOS LOS TESTS PASARON" in result.stderr or "TODOS LOS TESTS PASARON" in result.stdout:
            print(f"  {GREEN}✅{RESET} Tests de integración: PASARON")
            return True
        else:
            print(f"  {RED}❌{RESET} Tests de integración: FALLARON")
            if result.stderr:
                print(f"\n{YELLOW}Error output:{RESET}")
                print(result.stderr[-500:])
            return False
    except subprocess.TimeoutExpired:
        print(f"  {RED}❌{RESET} Tests timeout (>60s)")
        return False
    except Exception as e:
        print(f"  {RED}❌{RESET} Error ejecutando tests: {str(e)}")
        return False

def check_api_instantiation():
    """Valida que la API pueda instanciarse"""
    print_header("5️⃣  VALIDANDO API INSTANTIATION")
    
    try:
        from api.main import create_app
        from orchestrator.main import Orchestrator
        
        orch = Orchestrator(enable_memory=True, enable_inference=False)
        app = create_app(orchestrator=orch)
        
        print(f"  {GREEN}✅{RESET} FastAPI app created: {str(type(app))}")
        print(f"  {GREEN}✅{RESET} Orchestrator initialized successfully")
        print(f"  {GREEN}✅{RESET} Memory enabled: True")
        return True
    except Exception as e:
        print(f"  {RED}❌{RESET} Error: {str(e)}")
        return False

def check_cli_instantiation():
    """Valida que la CLI pueda instanciarse"""
    print_header("6️⃣  VALIDANDO CLI INSTANTIATION")
    
    try:
        from cli.main import TARSCLIApp
        from orchestrator.main import Orchestrator
        
        orch = Orchestrator(enable_memory=True, enable_inference=False)
        cli = TARSCLIApp(orchestrator=orch)
        
        print(f"  {GREEN}✅{RESET} CLI app created: {str(type(cli))}")
        print(f"  {GREEN}✅{RESET} Interactive CLI ready")
        return True
    except Exception as e:
        print(f"  {RED}❌{RESET} Error: {str(e)}")
        return False

def main():
    """Ejecuta todas las validaciones"""
    print(f"\n{BOLD}{BLUE}🧪 VALIDACION COMPLETA SPRINT 2{RESET}")
    print(f"{BLUE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
    
    import os
    
    # Cambiar a directorio correcto
    os.chdir("/home/ndrz02/keys_1")
    sys.path.insert(0, "/home/ndrz02/keys_1")
    
    results = {
        "Estructura de directorios": check_file_structure(),
        "Dependencias": check_dependencies(),
        "Imports": check_imports(),
        "API Instantiation": check_api_instantiation(),
        "CLI Instantiation": check_cli_instantiation(),
        "Tests de Integración": run_tests(),
    }
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {name:40} {status}")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Total: {passed}/{total} validaciones pasaron{RESET}")
    
    if failed == 0:
        print(f"\n{GREEN}{BOLD}🎉 ¡SPRINT 2 FUNCIONANDO PERFECTAMENTE!{RESET}")
        print(f"{GREEN}✅ Todos los componentes están operacionales{RESET}")
        print(f"{GREEN}✅ API lista para producción{RESET}")
        print(f"{GREEN}✅ CLI lista para usar{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}⚠️ VALIDACION INCOMPLETA - {failed} fallos detectados{RESET}")
        return 1

if __name__ == "__main__":
    exit(main())
