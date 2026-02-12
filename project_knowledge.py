"""
Project Knowledge Base - Base de conocimiento acumulativa de proyectos
Memoria a largo plazo de experimentos, soluciones y evolución de diseños.
Diferenciador clave vs Copilot/ChatGPT: Contexto acumulativo persistente.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np


class ProjectKnowledge:
    """Base de conocimiento de proyectos con búsqueda semántica."""
    
    def __init__(self, projects_dir="./data/projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Índice de proyectos
        self.index_file = self.projects_dir / "projects_index.json"
        self.index = self._load_index()
        
        # Modelo para embeddings semánticos (búsqueda inteligente)
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_enabled = True
        from core.soren_project_knowledge import *

        if __name__ == "__main__":
            main()
            descripcion: Descripción del proyecto
            categoria: Categoría (exoesqueleto, medico, robotica, etc)
        """
        proyecto_id = nombre.lower().replace(" ", "_")
        
        if proyecto_id in self.index["proyectos"]:
            print(f"⚠️ Proyecto '{nombre}' ya existe")
            return proyecto_id
        
        proyecto = {
            "id": proyecto_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "categoria": categoria,
            "creado": datetime.now().isoformat(),
            "ultima_actualizacion": datetime.now().isoformat(),
            "versiones": [],
            "experimentos": [],
            "problemas_resueltos": [],
            "archivos": []
        }
        
        # Crear directorio del proyecto
        proyecto_dir = self.projects_dir / proyecto_id
        proyecto_dir.mkdir(exist_ok=True)
        
        # Guardar metadata del proyecto
        with open(proyecto_dir / "proyecto.json", 'w') as f:
            json.dump(proyecto, f, indent=2)
        
        self.index["proyectos"][proyecto_id] = proyecto
        self._save_index()
        
        print(f"✅ Proyecto creado: {nombre} ({proyecto_id})")
        return proyecto_id
    
    def registrar_experimento(self, proyecto_id, experimento_data):
        """
        Registra un experimento en un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            experimento_data: Dict con datos del experimento
            {
                "titulo": "Prueba de torque con motor 200W",
                "objetivo": "Medir torque máximo sostenido",
                "setup": "Motor 200W, ratio 1:50, carga 5kg",
                "procedimiento": "...",
                "resultados": {...},
                "observaciones": "Vibración excesiva a >30 rpm",
                "conclusion": "Necesita mejor aislamiento"
            }
        """
        if proyecto_id not in self.index["proyectos"]:
            print(f"❌ Proyecto '{proyecto_id}' no existe")
            return None
        
        # Añadir metadata
        experimento_data["fecha"] = datetime.now().isoformat()
        experimento_data["proyecto_id"] = proyecto_id
        experimento_data["id"] = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Guardar experimento
        proyecto_dir = self.projects_dir / proyecto_id
        experimentos_file = proyecto_dir / "experimentos.json"
        
        experimentos = []
        if experimentos_file.exists():
            with open(experimentos_file, 'r') as f:
                experimentos = json.load(f)
        
        experimentos.append(experimento_data)
        
        with open(experimentos_file, 'w') as f:
            json.dump(experimentos, f, indent=2)
        
        # Actualizar índice
        self.index["proyectos"][proyecto_id]["experimentos"].append(experimento_data["id"])
        self.index["proyectos"][proyecto_id]["ultima_actualizacion"] = datetime.now().isoformat()
        self.index["experimentos"].append({
            "id": experimento_data["id"],
            "proyecto": proyecto_id,
            "titulo": experimento_data["titulo"],
            "fecha": experimento_data["fecha"]
        })
        self._save_index()
        
        print(f"📝 Experimento registrado: {experimento_data['titulo']}")
        return experimento_data["id"]
    
    def registrar_solucion(self, proyecto_id, problema, solucion, efectividad="alta"):
        """
        Registra una solución a un problema específico.
        
        Args:
            proyecto_id: ID del proyecto
            problema: Descripción del problema
            solucion: Solución aplicada
            efectividad: "alta", "media", "baja"
        """
        solucion_data = {
            "id": f"sol_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "proyecto_id": proyecto_id,
            "problema": problema,
            "solucion": solucion,
            "efectividad": efectividad,
            "fecha": datetime.now().isoformat()
        }
        
        # Guardar en archivo de soluciones
        proyecto_dir = self.projects_dir / proyecto_id
        soluciones_file = proyecto_dir / "soluciones.json"
        
        soluciones = []
        if soluciones_file.exists():
            with open(soluciones_file, 'r') as f:
                soluciones = json.load(f)
        
        soluciones.append(solucion_data)
        
        with open(soluciones_file, 'w') as f:
            json.dump(soluciones, f, indent=2)
        
        # Actualizar índice
        self.index["proyectos"][proyecto_id]["problemas_resueltos"].append(solucion_data["id"])
        self.index["soluciones"].append(solucion_data)
        self._save_index()
        
        print(f"💡 Solución registrada para: {problema[:50]}...")
        return solucion_data["id"]
    
    def buscar_soluciones_previas(self, problema_query, top_k=5):
        """
        Busca soluciones previas a problemas similares.
        
        Args:
            problema_query: Descripción del problema actual
            top_k: Número de soluciones a retornar
        """
        if not self.index["soluciones"]:
            print("📭 No hay soluciones registradas aún")
            return []
        
        if self.embeddings_enabled:
            # Búsqueda semántica con embeddings
            query_embedding = self.embedding_model.encode(problema_query)
            
            resultados = []
            for sol in self.index["soluciones"]:
                sol_embedding = self.embedding_model.encode(sol["problema"])
                similitud = np.dot(query_embedding, sol_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(sol_embedding)
                )
                
                resultados.append({
                    "solucion": sol,
                    "similitud": float(similitud)
                })
            
            # Ordenar por similitud
            resultados.sort(key=lambda x: x["similitud"], reverse=True)
            
            print(f"\n🔍 Soluciones similares encontradas (top {top_k}):")
            for i, res in enumerate(resultados[:top_k], 1):
                print(f"\n{i}. Similitud: {res['similitud']:.2%}")
                print(f"   Problema: {res['solucion']['problema']}")
                print(f"   Solución: {res['solucion']['solucion']}")
                print(f"   Efectividad: {res['solucion']['efectividad']}")
                print(f"   Proyecto: {res['solucion']['proyecto_id']}")
                print(f"   Fecha: {res['solucion']['fecha']}")
            
            return [r["solucion"] for r in resultados[:top_k]]
        else:
            # Búsqueda básica por palabras clave
            palabras_clave = problema_query.lower().split()
            
            resultados = []
            for sol in self.index["soluciones"]:
                matches = sum(1 for palabra in palabras_clave if palabra in sol["problema"].lower())
                if matches > 0:
                    resultados.append({
                        "solucion": sol,
                        "matches": matches
                    })
            
            resultados.sort(key=lambda x: x["matches"], reverse=True)
            return [r["solucion"] for r in resultados[:top_k]]
    
    def evolucionar_version(self, proyecto_id, version_anterior, cambios, razon):
        """
        Registra una nueva versión de diseño documentando la evolución.
        
        Args:
            proyecto_id: ID del proyecto
            version_anterior: Versión previa (ej: "v2")
            cambios: Lista de cambios realizados
            razon: Razón de los cambios
        """
        proyecto = self.index["proyectos"][proyecto_id]
        
        num_versiones = len(proyecto["versiones"])
        nueva_version = f"v{num_versiones + 1}"
        
        version_data = {
            "version": nueva_version,
            "version_anterior": version_anterior,
            "fecha": datetime.now().isoformat(),
            "cambios": cambios,
            "razon": razon
        }
        
        # Guardar en historial de versiones
        proyecto_dir = self.projects_dir / proyecto_id
        versiones_file = proyecto_dir / "versiones.json"
        
        versiones = []
        if versiones_file.exists():
            with open(versiones_file, 'r') as f:
                versiones = json.load(f)
        
        versiones.append(version_data)
        
        with open(versiones_file, 'w') as f:
            json.dump(versiones, f, indent=2)
        
        # Actualizar índice
        self.index["proyectos"][proyecto_id]["versiones"].append(nueva_version)
        self._save_index()
        
        print(f"🔄 Nueva versión creada: {nueva_version}")
        print(f"   Razón: {razon}")
        print(f"   Cambios: {len(cambios)}")
        
        return nueva_version
    
    def generar_reporte_proyecto(self, proyecto_id):
        """
        Genera un reporte completo del progreso del proyecto.
        """
        if proyecto_id not in self.index["proyectos"]:
            print(f"❌ Proyecto '{proyecto_id}' no existe")
            return None
        
        proyecto = self.index["proyectos"][proyecto_id]
        proyecto_dir = self.projects_dir / proyecto_id
        
        reporte = {
            "proyecto": proyecto["nombre"],
            "descripcion": proyecto["descripcion"],
            "categoria": proyecto["categoria"],
            "creado": proyecto["creado"],
            "ultima_actualizacion": proyecto["ultima_actualizacion"],
            "estadisticas": {
                "experimentos_realizados": len(proyecto["experimentos"]),
                "problemas_resueltos": len(proyecto["problemas_resueltos"]),
                "versiones_desarrolladas": len(proyecto["versiones"])
            }
        }
        
        # Cargar experimentos
        experimentos_file = proyecto_dir / "experimentos.json"
        if experimentos_file.exists():
            with open(experimentos_file, 'r') as f:
                reporte["experimentos"] = json.load(f)
        
        # Cargar soluciones
        soluciones_file = proyecto_dir / "soluciones.json"
        if soluciones_file.exists():
            with open(soluciones_file, 'r') as f:
                reporte["soluciones"] = json.load(f)
        
        # Cargar versiones
        versiones_file = proyecto_dir / "versiones.json"
        if versiones_file.exists():
            with open(versiones_file, 'r') as f:
                reporte["evolución"] = json.load(f)
        
        # Guardar reporte
        reporte_file = proyecto_dir / f"reporte_{datetime.now().strftime('%Y%m%d')}.json"
        with open(reporte_file, 'w') as f:
            json.dump(reporte, f, indent=2)
        
        print(f"\n📊 REPORTE DE PROYECTO: {proyecto['nombre']}")
        print(f"="*60)
        print(f"Categoría: {proyecto['categoria']}")
        print(f"Creado: {proyecto['creado'][:10]}")
        print(f"Última actualización: {proyecto['ultima_actualizacion'][:10]}")
        print(f"\nEstadísticas:")
        print(f"  - Experimentos: {reporte['estadisticas']['experimentos_realizados']}")
        print(f"  - Problemas resueltos: {reporte['estadisticas']['problemas_resueltos']}")
        print(f"  - Versiones: {reporte['estadisticas']['versiones_desarrolladas']}")
        print(f"\nReporte guardado en: {reporte_file}")
        
        return reporte


# Ejemplo de uso
if __name__ == "__main__":
    kb = ProjectKnowledge()
    
    # Crear proyecto
    proyecto = kb.crear_proyecto(
        "Exoesqueleto_Rodilla_Rehabilitacion",
        "Exoesqueleto activo para rehabilitación de rodilla post-operación ACL",
        categoria="exoesqueleto"
    )
    
    # Registrar experimento
    kb.registrar_experimento(proyecto, {
        "titulo": "Prueba de torque con motor 200W",
        "objetivo": "Medir torque máximo sostenido",
        "setup": "Motor 200W, ratio 1:50, carga simulada 5kg",
        "resultados": {"torque_max": "45 Nm", "temperatura_max": "42°C"},
        "observaciones": "Vibración excesiva a velocidades >30 rpm",
        "conclusion": "Necesita mejor aislamiento y posiblemente motor de mayor torque"
    })
    
    # Registrar solución
    kb.registrar_solucion(
        proyecto,
        "Motor MG996R se calienta excesivamente (>50°C) después de 5 minutos",
        "Añadir disipador de aluminio y reducir carga al 80% usando control PID más suave",
        efectividad="alta"
    )
