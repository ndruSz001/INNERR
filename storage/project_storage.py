"""
Project Storage - Persistencia de proyectos
Sprint 3 - FASE 8

Responsabilidad: Gestionar proyectos y documentos
- Persistencia de proyectos
- Metadata indexado
- Relaciones documento-proyecto
- Historial de cambios
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from storage.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ProjectStorage:
    """Almacenamiento persistente de proyectos"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Args:
            db_manager: Instancia de DatabaseManager
        """
        self.db = db_manager
        logger.info("✅ Project Storage inicializado")
    
    def create_project(
        self,
        user_id: str,
        name: str,
        description: str = ""
    ) -> str:
        """
        Crear nuevo proyecto
        
        Args:
            user_id: ID del usuario propietario
            name: Nombre del proyecto
            description: Descripción del proyecto
            
        Returns:
            ID del proyecto creado
        """
        project_id = str(uuid.uuid4())
        
        try:
            self.db.create_project(project_id, user_id, name, description)
            logger.info(f"✅ Proyecto creado: {project_id}")
            return project_id
        
        except Exception as e:
            logger.error(f"❌ Error creando proyecto: {e}")
            return ""
    
    def add_document(
        self,
        project_id: str,
        title: str,
        content: str,
        file_path: str = ""
    ) -> str:
        """
        Agregar documento a un proyecto
        
        Args:
            project_id: ID del proyecto
            title: Título del documento
            content: Contenido del documento
            file_path: Ruta original del archivo (opcional)
            
        Returns:
            ID del documento agregado
        """
        doc_id = str(uuid.uuid4())
        
        try:
            self.db.add_document(doc_id, project_id, title, content, file_path)
            logger.info(f"✅ Documento agregado: {doc_id}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Error agregando documento: {e}")
            return ""
    
    def get_project_details(self, project_id: str) -> Optional[Dict]:
        """
        Obtener detalles completos de un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con info del proyecto y documentos
        """
        try:
            project = self.db.get_project(project_id)
            
            if not project:
                return None
            
            documents = self.db.get_documents(project_id)
            
            return {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'document_count': len(documents),
                'documents': [
                    {
                        'id': doc.id,
                        'title': doc.title,
                        'created_at': doc.created_at.isoformat(),
                        'size': len(doc.content)
                    }
                    for doc in documents
                ]
            }
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo proyecto: {e}")
            return None
    
    def list_user_projects(self, user_id: str) -> List[Dict]:
        """
        Listar proyectos de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de proyectos
        """
        try:
            projects = self.db.list_projects(user_id)
            
            result = []
            for proj in projects:
                documents = self.db.get_documents(proj.id)
                result.append({
                    'id': proj.id,
                    'name': proj.name,
                    'description': proj.description,
                    'created_at': proj.created_at.isoformat(),
                    'updated_at': proj.updated_at.isoformat(),
                    'document_count': len(documents)
                })
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error listando proyectos: {e}")
            return []
    
    def search_projects(
        self,
        user_id: str,
        query: str
    ) -> List[Dict]:
        """
        Buscar proyectos por nombre
        
        Args:
            user_id: ID del usuario
            query: Texto a buscar
            
        Returns:
            Proyectos coincidentes
        """
        try:
            projects = self.db.list_projects(user_id)
            
            matching = [
                p for p in projects
                if query.lower() in p.name.lower() or query.lower() in (p.description or "").lower()
            ]
            
            return [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'created_at': p.created_at.isoformat()
                }
                for p in matching
            ]
        
        except Exception as e:
            logger.error(f"❌ Error buscando proyectos: {e}")
            return []
    
    def get_project_documents(self, project_id: str) -> List[Dict]:
        """
        Obtener todos los documentos de un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de documentos
        """
        try:
            documents = self.db.get_documents(project_id)
            
            return [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'file_path': doc.file_path,
                    'created_at': doc.created_at.isoformat(),
                    'updated_at': doc.updated_at.isoformat(),
                    'size': len(doc.content)
                }
                for doc in documents
            ]
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo documentos: {e}")
            return []
    
    def search_documents_in_project(
        self,
        project_id: str,
        query: str
    ) -> List[Dict]:
        """
        Buscar documentos en un proyecto por contenido
        
        Args:
            project_id: ID del proyecto
            query: Texto a buscar
            
        Returns:
            Documentos coincidentes
        """
        try:
            documents = self.db.get_documents(project_id)
            
            matching = [
                d for d in documents
                if query.lower() in d.title.lower() or query.lower() in d.content.lower()
            ]
            
            return [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'created_at': doc.created_at.isoformat(),
                    'relevance': doc.content.lower().count(query.lower())
                }
                for doc in matching
            ]
        
        except Exception as e:
            logger.error(f"❌ Error buscando documentos: {e}")
            return []
    
    def export_project(self, project_id: str, format: str = "json") -> str:
        """
        Exportar proyecto con todos sus documentos
        
        Args:
            project_id: ID del proyecto
            format: 'json' o 'txt'
            
        Returns:
            Proyecto formateado
        """
        try:
            project = self.db.get_project(project_id)
            documents = self.db.get_documents(project_id)
            
            if format == "json":
                import json
                data = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'created_at': project.created_at.isoformat(),
                    'documents': [
                        {
                            'id': doc.id,
                            'title': doc.title,
                            'content': doc.content[:1000]  # Limitar contenido
                        }
                        for doc in documents
                    ]
                }
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            elif format == "txt":
                lines = [
                    f"# Proyecto: {project.name}",
                    f"Descripción: {project.description}",
                    f"Documentos: {len(documents)}",
                    ""
                ]
                
                for doc in documents:
                    lines.append(f"## {doc.title}")
                    lines.append(doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)
                    lines.append("")
                
                return "\n".join(lines)
            
            else:
                return ""
        
        except Exception as e:
            logger.error(f"❌ Error exportando proyecto: {e}")
            return ""


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    db = DatabaseManager()
    storage = ProjectStorage(db)
    
    # Crear proyecto
    proj_id = storage.create_project("user1", "Mi Proyecto", "Desc")
    
    # Agregar documentos
    doc1 = storage.add_document(proj_id, "Doc 1", "Contenido documento 1")
    doc2 = storage.add_document(proj_id, "Doc 2", "Contenido documento 2")
    
    # Obtener detalles
    details = storage.get_project_details(proj_id)
    print(f"\n📊 Proyecto: {details['name']}")
    print(f"   Documentos: {details['document_count']}")
    
    # Listar proyectos
    projects = storage.list_user_projects("user1")
    print(f"\n📁 Total proyectos: {len(projects)}")
