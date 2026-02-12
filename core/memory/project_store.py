"""
Project Store - Gestiona resúmenes de proyectos completados

Responsabilidad: Almacenar y recuperar resúmenes de proyectos
- Solo metadatos y resúmenes (NO raw text)
- Indexable por keywords y tags
- Apuntadores a embeddings en PC2

Estructura:
{
    'id': 'proj_123',
    'name': 'Proyecto X',
    'summary': 'Resumen de 100-200 palabras',
    'created_at': '2026-02-12T...',
    'completed_at': '2026-02-12T...',
    'keywords': ['ML', 'Python', 'NLP'],
    'tags': ['completed', 'high-priority'],
    'embedding_id': 'emb_456'  # Apunta a vector en PC2
}
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json


class ProjectStore:
    """Gestiona resúmenes de proyectos (DB)"""
    
    def __init__(self):
        """Inicializar store"""
        self.projects: Dict[str, Dict[str, Any]] = {}  # {project_id: data}
        self.keyword_index: Dict[str, List[str]] = {}  # {keyword: [project_ids]}
        self.tag_index: Dict[str, List[str]] = {}  # {tag: [project_ids]}
    
    def create_project_summary(
        self,
        name: str,
        summary: str,
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crear resumen de proyecto
        
        Args:
            name: Nombre del proyecto
            summary: Resumen (200-500 palabras máximo)
            keywords: Lista de keywords para búsqueda
            tags: Lista de tags para clasificación
            metadata: Metadatos adicionales
            
        Returns:
            ID del proyecto creado
        """
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        
        self.projects[project_id] = {
            'id': project_id,
            'name': name,
            'summary': summary,
            'created_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'keywords': keywords or [],
            'tags': tags or [],
            'embedding_id': None,  # Se asignará cuando PC2 genere embedding
            'metadata': metadata or {}
        }
        
        # Indexar por keywords
        for keyword in keywords or []:
            keyword_lower = keyword.lower()
            if keyword_lower not in self.keyword_index:
                self.keyword_index[keyword_lower] = []
            self.keyword_index[keyword_lower].append(project_id)
        
        # Indexar por tags
        for tag in tags or []:
            tag_lower = tag.lower()
            if tag_lower not in self.tag_index:
                self.tag_index[tag_lower] = []
            self.tag_index[tag_lower].append(project_id)
        
        return project_id
    
    def get_project_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener resumen de proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Datos del proyecto o None
        """
        return self.projects.get(project_id)
    
    def search_projects(
        self,
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar proyectos por keywords y/o tags
        
        Args:
            keywords: Lista de keywords a buscar
            tags: Lista de tags a buscar
            limit: Máximo de resultados
            
        Returns:
            Lista de proyectos coincidentes
        """
        results = set()
        
        # Buscar por keywords
        if keywords:
            for keyword in keywords:
                keyword_lower = keyword.lower()
                results.update(self.keyword_index.get(keyword_lower, []))
        
        # Buscar por tags
        if tags:
            for tag in tags:
                tag_lower = tag.lower()
                results.update(self.tag_index.get(tag_lower, []))
        
        # Si no hay criterios, devolver todos
        if not keywords and not tags:
            results = set(self.projects.keys())
        
        # Convertir a lista de objetos y ordenar por fecha
        projects = [self.projects[pid] for pid in results if pid in self.projects]
        projects.sort(key=lambda p: p['completed_at'], reverse=True)
        
        return projects[:limit]
    
    def update_project_metadata(
        self,
        project_id: str,
        metadata: Dict[str, Any],
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Actualizar metadatos de proyecto
        
        Args:
            project_id: ID del proyecto
            metadata: Nuevos metadatos
            keywords: Actualizar keywords
            tags: Actualizar tags
            
        Returns:
            True si fue actualizado, False si no existe
        """
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        project['metadata'].update(metadata)
        
        # Actualizar keywords si se proporciona
        if keywords is not None:
            # Remover del índice anterior
            for keyword in project['keywords']:
                keyword_lower = keyword.lower()
                if keyword_lower in self.keyword_index:
                    self.keyword_index[keyword_lower].remove(project_id)
            
            # Agregar al nuevo índice
            project['keywords'] = keywords
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keyword_index:
                    self.keyword_index[keyword_lower] = []
                self.keyword_index[keyword_lower].append(project_id)
        
        # Actualizar tags si se proporciona
        if tags is not None:
            # Remover del índice anterior
            for tag in project['tags']:
                tag_lower = tag.lower()
                if tag_lower in self.tag_index:
                    self.tag_index[tag_lower].remove(project_id)
            
            # Agregar al nuevo índice
            project['tags'] = tags
            for tag in tags:
                tag_lower = tag.lower()
                if tag_lower not in self.tag_index:
                    self.tag_index[tag_lower] = []
                self.tag_index[tag_lower].append(project_id)
        
        return True
    
    def list_all_projects(self) -> List[Dict[str, Any]]:
        """
        Listar todos los proyectos ordenados por fecha
        
        Returns:
            Lista de todos los proyectos
        """
        projects = list(self.projects.values())
        projects.sort(key=lambda p: p['completed_at'], reverse=True)
        return projects
    
    def set_embedding_id(self, project_id: str, embedding_id: str) -> bool:
        """
        Asociar embedding vectorial a proyecto
        
        Args:
            project_id: ID del proyecto
            embedding_id: ID del embedding en PC2
            
        Returns:
            True si fue actualizado, False si proyecto no existe
        """
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]['embedding_id'] = embedding_id
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """
        Eliminar proyecto
        
        Args:
            project_id: ID a eliminar
            
        Returns:
            True si fue eliminado, False si no existe
        """
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        
        # Limpiar índices
        for keyword in project['keywords']:
            keyword_lower = keyword.lower()
            if keyword_lower in self.keyword_index:
                self.keyword_index[keyword_lower].remove(project_id)
        
        for tag in project['tags']:
            tag_lower = tag.lower()
            if tag_lower in self.tag_index:
                self.tag_index[tag_lower].remove(project_id)
        
        del self.projects[project_id]
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del store"""
        return {
            'total_projects': len(self.projects),
            'unique_keywords': len(self.keyword_index),
            'unique_tags': len(self.tag_index),
            'projects_with_embeddings': sum(
                1 for p in self.projects.values() if p.get('embedding_id')
            )
        }
