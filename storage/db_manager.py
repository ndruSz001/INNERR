"""
Database Manager - Persistencia en SQLite
Sprint 3 - FASE 8

Responsabilidad: Gestionar base de datos
- Modelos ORM para Conversaciones, Proyectos, Documentos
- Migrations automáticas
- Connection pooling
- Query helpers
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class Conversation(Base):
    """Modelo de conversación"""
    __tablename__ = 'conversations'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    message_count = Column(Integer, default=0)
    
    # Relación
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id} - {self.title}>"


class Message(Base):
    """Modelo de mensaje"""
    __tablename__ = 'messages'
    
    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # Relación
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Message {self.id} - {self.role}>"


class Project(Base):
    """Modelo de proyecto"""
    __tablename__ = 'projects'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relación
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.id} - {self.name}>"


class Document(Base):
    """Modelo de documento"""
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relación
    project = relationship("Project", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.id} - {self.title}>"


class DatabaseManager:
    """Gestor de base de datos"""
    
    def __init__(self, db_path: str = "sqlite:////tmp/tars.db", echo: bool = False):
        """
        Args:
            db_path: Ruta de la base de datos SQLite
            echo: Log SQL queries
        """
        self.db_path = db_path
        self.engine = create_engine(db_path, echo=echo)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Crear tablas
        Base.metadata.create_all(self.engine)
        logger.info(f"✅ Database Manager inicializado: {db_path}")
    
    def get_session(self) -> Session:
        """Obtener sesión de DB"""
        return self.SessionLocal()
    
    # ========== CONVERSATIONS ==========
    
    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> Conversation:
        """Crear nueva conversación"""
        session = self.get_session()
        try:
            conv = Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title
            )
            session.add(conv)
            session.commit()
            logger.info(f"✅ Conversación creada: {conversation_id}")
            return conv
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Obtener conversación por ID"""
        session = self.get_session()
        try:
            return session.query(Conversation).filter_by(id=conversation_id).first()
        finally:
            session.close()
    
    def list_conversations(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """Listar conversaciones del usuario"""
        session = self.get_session()
        try:
            return session.query(Conversation)\
                .filter_by(user_id=user_id)\
                .order_by(Conversation.updated_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    # ========== MESSAGES ==========
    
    def add_message(
        self,
        message_id: str,
        conversation_id: str,
        role: str,
        content: str
    ) -> Message:
        """Agregar mensaje a conversación"""
        session = self.get_session()
        try:
            msg = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            session.add(msg)
            
            # Actualizar contador
            conv = session.query(Conversation).filter_by(id=conversation_id).first()
            if conv:
                conv.message_count += 1
            
            session.commit()
            logger.info(f"✅ Mensaje agregado: {message_id}")
            return msg
        finally:
            session.close()
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        """Obtener todos los mensajes de una conversación"""
        session = self.get_session()
        try:
            return session.query(Message)\
                .filter_by(conversation_id=conversation_id)\
                .order_by(Message.created_at.asc())\
                .all()
        finally:
            session.close()
    
    # ========== PROJECTS ==========
    
    def create_project(
        self,
        project_id: str,
        user_id: str,
        name: str,
        description: str = ""
    ) -> Project:
        """Crear nuevo proyecto"""
        session = self.get_session()
        try:
            proj = Project(
                id=project_id,
                user_id=user_id,
                name=name,
                description=description
            )
            session.add(proj)
            session.commit()
            logger.info(f"✅ Proyecto creado: {project_id}")
            return proj
        finally:
            session.close()
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Obtener proyecto por ID"""
        session = self.get_session()
        try:
            return session.query(Project).filter_by(id=project_id).first()
        finally:
            session.close()
    
    def list_projects(self, user_id: str) -> List[Project]:
        """Listar proyectos del usuario"""
        session = self.get_session()
        try:
            return session.query(Project)\
                .filter_by(user_id=user_id)\
                .order_by(Project.updated_at.desc())\
                .all()
        finally:
            session.close()
    
    # ========== DOCUMENTS ==========
    
    def add_document(
        self,
        document_id: str,
        project_id: str,
        title: str,
        content: str,
        file_path: str = ""
    ) -> Document:
        """Agregar documento a proyecto"""
        session = self.get_session()
        try:
            doc = Document(
                id=document_id,
                project_id=project_id,
                title=title,
                content=content,
                file_path=file_path
            )
            session.add(doc)
            session.commit()
            logger.info(f"✅ Documento agregado: {document_id}")
            return doc
        finally:
            session.close()
    
    def get_documents(self, project_id: str) -> List[Document]:
        """Obtener todos los documentos de un proyecto"""
        session = self.get_session()
        try:
            return session.query(Document)\
                .filter_by(project_id=project_id)\
                .order_by(Document.created_at.asc())\
                .all()
        finally:
            session.close()
    
    # ========== CLEANUP ==========
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Limpiar conversaciones >N días"""
        session = self.get_session()
        try:
            from sqlalchemy import and_
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted = session.query(Conversation)\
                .filter(Conversation.updated_at < cutoff_date)\
                .delete()
            
            session.commit()
            logger.info(f"🧹 {deleted} conversaciones eliminadas")
            return deleted
        finally:
            session.close()
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de DB"""
        session = self.get_session()
        try:
            return {
                'conversations': session.query(Conversation).count(),
                'messages': session.query(Message).count(),
                'projects': session.query(Project).count(),
                'documents': session.query(Document).count(),
            }
        finally:
            session.close()


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    db = DatabaseManager()
    
    # Crear conversación
    conv_id = "conv-001"
    conv = db.create_conversation(conv_id, "user1", "Test Conversation")
    
    # Agregar mensajes
    db.add_message("msg-001", conv_id, "user", "Hola")
    db.add_message("msg-002", conv_id, "assistant", "Hola! ¿Cómo estás?")
    
    # Crear proyecto
    proj_id = "proj-001"
    proj = db.create_project(proj_id, "user1", "Mi Proyecto", "Descripción")
    
    # Agregar documento
    db.add_document("doc-001", proj_id, "Doc 1", "Contenido del documento")
    
    # Listar
    print("\n📊 Estadísticas:")
    print(db.get_stats())
