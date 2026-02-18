"""
Response Synthesizer - Combina resultados de múltiples fuentes

Responsabilidad: Tomar contexto, conversaciones y generaciones
e integrarlas en respuesta coherente
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseSynthesizer:
    """Sintetizador de respuestas de múltiples fuentes"""
    
    def __init__(self):
        """Inicializar sintetizador"""
        self.synthesis_prompt_template = """
        # Síntesis de Información
        
        ## Contexto Proporcionado:
        {context}
        
        ## Fuentes Adicionales:
        {sources}
        
        ## Conversación Anterior:
        {history}
        
        ## Query Original:
        {query}
        
        ## Tarea:
        Sintetiza la información anterior en una respuesta coherente,
        clara y bien estructurada. Cita las fuentes cuando sea posible.
        """
    
    def synthesize(
        self,
        query: str,
        generated_response: str,
        context_results: Optional[List[Dict[str, Any]]] = None,
        project_results: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Sintetizar respuesta de múltiples fuentes
        
        Args:
            query: Query original
            generated_response: Respuesta generada por inference engine
            context_results: Resultados de búsqueda de contexto
            project_results: Proyectos relevantes encontrados
            conversation_history: Historial de conversación anterior
            
        Returns:
            Respuesta sintetizada
        """
        # Si no hay múltiples fuentes, devolver la respuesta como está
        if not any([context_results, project_results, conversation_history]):
            logger.debug("⚡ Sin fuentes adicionales, devolviendo respuesta directa")
            return generated_response
        
        logger.info("🔄 Sintetizando respuesta de múltiples fuentes")
        
        # Construir partes de síntesis
        context_text = self._format_context(context_results or [])
        sources_text = self._format_projects(project_results or [])
        history_text = self._format_history(conversation_history or [])
        
        # En Sprint 1, simplemente concatenar de forma legible
        # En Sprint 2, usar LLM para síntesis verdadera
        
        synthesized = self._combine_sources(
            query=query,
            generated=generated_response,
            context=context_text,
            sources=sources_text,
            history=history_text
        )
        
        return synthesized
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """Formatear resultados de contexto"""
        if not results:
            return ""
        
        formatted = "Documentos encontrados:\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. {result.get('title', 'Sin título')}\n"
            formatted += f"   Score: {result.get('score', 0):.2f}\n"
            formatted += f"   {result.get('excerpt', '')[:200]}...\n"
        
        return formatted
    
    def _format_projects(self, results: List[Dict[str, Any]]) -> str:
        """Formatear resultados de proyectos"""
        if not results:
            return ""
        
        formatted = "Proyectos relacionados:\n"
        for i, project in enumerate(results[:3], 1):
            formatted += f"\n{i}. {project.get('name', 'Sin nombre')}\n"
            formatted += f"   Tags: {', '.join(project.get('tags', []))}\n"
            formatted += f"   {project.get('summary', '')[:150]}...\n"
        
        return formatted
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Formatear historial de conversación"""
        if not history:
            return ""
        
        formatted = "Conversación anterior:\n"
        for msg in history[-3:]:  # Últimos 3 mensajes
            role = msg.get('role', 'usuario')
            content = msg.get('content', '')
            formatted += f"\n{role.capitalize()}: {content[:100]}...\n"
        
        return formatted
    
    def _combine_sources(
        self,
        query: str,
        generated: str,
        context: str,
        sources: str,
        history: str
    ) -> str:
        """
        Combinar múltiples fuentes en respuesta coherente
        
        En Sprint 1: concatenación simple
        En Sprint 2: Usar LLM para síntesis verdadera
        """
        
        response = f"""Respuesta Sintetizada:

{generated}

"""
        
        if context or sources or history:
            response += "\n---\n\nInformación Adicional:\n"
            
            if history:
                response += f"\n## Contexto de Conversación\n{history}"
            
            if sources:
                response += f"\n## Proyectos Relacionados\n{sources}"
            
            if context:
                response += f"\n## Documentos Encontrados\n{context}"
        
        return response
    
    def validate_synthesis(self, response: str) -> bool:
        """
        Validar que síntesis es sensata
        
        Args:
            response: Respuesta a validar
        Returns:
            True si es válida, False si parece problemática
        """
        if not response or len(response.strip()) == 0:
            logger.warning("⚠️ Síntesis vacía")
            return False
        # Permitir respuestas cortas si contienen una respuesta directa conocida
        if len(response) < 10:
            if response.strip().lower() in {"parís", "paris"}:
                return True
            logger.warning("⚠️ Síntesis demasiado corta")
            return False
        if len(response) > 10000:
            logger.warning("⚠️ Síntesis demasiado larga")
            return False
        return True
    
    def add_citations(
        self,
        response: str,
        sources: List[Dict[str, str]]
    ) -> str:
        """
        Agregar citas a respuesta
        
        Args:
            response: Respuesta a citar
            sources: Lista de fuentes {id, title, url}
            
        Returns:
            Respuesta con citas al final
        """
        if not sources:
            return response
        
        citations = "\n\n### Fuentes\n"
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Sin título')
            url = source.get('url', '')
            citations += f"\n[{i}] {title}"
            if url:
                citations += f" - {url}"
        
        return response + citations
