"""
models.py
Modelos y dataclasses para Conversación, Mensaje, etc.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Conversacion:
    id: str
    titulo: str
    descripcion: str = ""
    categoria: str = "general"
    fecha_inicio: str = field(default_factory=lambda: datetime.now().isoformat())
    fecha_ultima_actividad: str = field(default_factory=lambda: datetime.now().isoformat())
    num_mensajes: int = 0
    estado: str = "activa"
    tags: List[str] = field(default_factory=list)
    proyecto_relacionado: Optional[str] = None
    importancia: int = 5
    metadata: Dict = field(default_factory=dict)
    es_integradora: bool = False
    objetivo: Optional[str] = None
    conclusiones: Optional[str] = None
    resultados: Optional[str] = None

@dataclass
class Mensaje:
    id: int
    conversacion_id: str
    timestamp: str
    tipo: str
    contenido: str
    metadata: Dict = field(default_factory=dict)
