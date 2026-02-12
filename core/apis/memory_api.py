"""
Memory API - Contrato de comunicación RPC entre PC1 y PC2

Define los métodos que pueden invocarse remotamente
entre los dos nodos del cluster.
"""


class MemoryAPI:
    """
    API de Memoria - Contrato JSON-RPC entre PC1 y PC2
    
    Métodos que PC1 invoca en PC2:
    - search_similar(query_embedding, top_k)
    - add_embedding(text_id, embedding, metadata)
    - get_embedding_status()
    - clear_embeddings()
    
    Métodos que PC2 invoca en PC1:
    - get_conversation(conversation_id)
    - get_project_summary(project_id)
    - sync_memory_state()
    """
    
    # ========== RPC Methods: PC1 → PC2 ==========
    
    # Búsqueda semántica
    SEARCH_SIMILAR = "memory.search_similar"
    """
    Buscar documentos similares por embeddings
    Args: {query_embedding: List[float], top_k: int}
    Returns: List[{id: str, score: float, metadata: dict}]
    """
    
    # Gestión de embeddings
    ADD_EMBEDDING = "memory.add_embedding"
    """
    Agregar embedding a índice
    Args: {text_id: str, embedding: List[float], metadata: dict}
    Returns: {success: bool, embedding_id: str}
    """
    
    # Estado del índice
    GET_EMBEDDING_STATUS = "memory.get_embedding_status"
    """
    Obtener estado del índice vectorial
    Args: {}
    Returns: {total_embeddings: int, index_size: int, last_sync: str}
    """
    
    # Mantenimiento
    CLEAR_EMBEDDINGS = "memory.clear_embeddings"
    """Limpiar todos los embeddings"""
    
    REBUILD_INDEX = "memory.rebuild_index"
    """Reconstruir índice (operación pesada)"""
    
    # ========== RPC Methods: PC2 → PC1 ==========
    
    # Conversaciones
    GET_CONVERSATION = "memory.get_conversation"
    """
    Obtener conversación por ID
    Args: {conversation_id: str}
    Returns: {id: str, user_id: str, messages: List[dict], ...}
    """
    
    LIST_CONVERSATIONS = "memory.list_conversations"
    """
    Listar conversaciones de usuario
    Args: {user_id: str, limit: int}
    Returns: List[{id: str, title: str, ...}]
    """
    
    ADD_MESSAGE = "memory.add_message"
    """
    Agregar mensaje a conversación
    Args: {conversation_id: str, role: str, content: str}
    Returns: {success: bool}
    """
    
    # Proyectos
    GET_PROJECT_SUMMARY = "memory.get_project_summary"
    """
    Obtener resumen de proyecto
    Args: {project_id: str}
    Returns: {id: str, name: str, summary: str, keywords: List[str], ...}
    """
    
    SEARCH_PROJECTS = "memory.search_projects"
    """
    Buscar proyectos por keywords/tags
    Args: {keywords: List[str], tags: List[str], limit: int}
    Returns: List[{id: str, name: str, ...}]
    """
    
    CREATE_PROJECT_SUMMARY = "memory.create_project_summary"
    """
    Crear resumen de proyecto
    Args: {name: str, summary: str, keywords: List[str], tags: List[str]}
    Returns: {project_id: str}
    """
    
    # Sincronización
    SYNC_MEMORY_STATE = "memory.sync_memory_state"
    """
    Sincronizar estado general de memoria
    Args: {}
    Returns: {conversations: int, projects: int, embeddings: int}
    """


class MemoryRPCServer:
    """
    Servidor RPC que escucha invocaciones remotas
    
    En Sprint 2 se implementará con:
    - aiohttp para requests HTTP
    - Serialización JSON
    - Error handling distribuido
    """
    
    def __init__(self, host: str = "localhost", port: int = 9999):
        """
        Args:
            host: Host a escuchar
            port: Puerto a escuchar
        """
        self.host = host
        self.port = port
        self.routes = {}
    
    def register_handler(self, method: str, handler):
        """
        Registrar handler para método RPC
        
        Args:
            method: Nombre del método (ej: "memory.search_similar")
            handler: Función que procesa la solicitud
        """
        self.routes[method] = handler
    
    def start(self):
        """
        Iniciar servidor RPC
        
        TODO: Implementar en Sprint 2 con aiohttp
        """
        pass


class MemoryRPCClient:
    """
    Cliente RPC para invocar métodos remotos
    
    En Sprint 2:
    - Conexión a servidor remoto
    - Timeouts y retry
    - Error handling
    """
    
    def __init__(self, remote_host: str, remote_port: int):
        """
        Args:
            remote_host: Host del servidor remoto
            remote_port: Puerto del servidor remoto
        """
        self.remote_host = remote_host
        self.remote_port = remote_port
    
    async def call(self, method: str, params: dict) -> dict:
        """
        Invocar método remoto
        
        Args:
            method: Nombre del método RPC
            params: Parámetros
            
        Returns:
            Resultado de invocación
            
        TODO: Implementar en Sprint 2
        """
        pass
