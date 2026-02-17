"""
Search and intelligent retrieval functions for conversation management.
"""

# Functions to be moved from conversation_manager.py:
# - buscar_conversaciones
# - detectar_intencion_retomar
# - buscar_conversacion_inteligente

from conversation_manager.db import execute_query

# Stub implementations (to be filled with actual logic)
def buscar_conversaciones(db_path, query, limit=10):
    rows = execute_query(
        db_path,
        '''SELECT DISTINCT c.id, c.titulo, c.descripcion, c.categoria, c.fecha_ultima_actividad, c.num_mensajes FROM conversaciones c LEFT JOIN mensajes m ON c.id = m.conversacion_id WHERE c.titulo LIKE ? OR c.descripcion LIKE ? OR m.contenido LIKE ? ORDER BY c.fecha_ultima_actividad DESC LIMIT ?''',
        [f'%{query}%', f'%{query}%', f'%{query}%', limit],
        fetchall=True
    )
    resultados = []
    for row in rows or []:
        resultados.append({
            "id": row[0],
            "titulo": row[1],
            "descripcion": row[2],
            "categoria": row[3],
            "fecha": row[4],
            "mensajes": row[5]
        })
    return resultados

def detectar_intencion_retomar(mensaje):
    import re
    mensaje_lower = mensaje.lower()
    patrones_retomar = [
        r'(?:volvamos|regresemos|retomemos)\s+(?:a|con)?\s+(.+)',
        r'(?:vamos|sigamos)\s+(?:a\s+)?(?:seguir|continuar)\s+(?:con|la)?\s+(.+)',
        r'(?:continuemos|continua|sigue)\s+(?:con|la)?\s+(.+)',
        r'(?:recupera|abre|carga)\s+(?:la\s+)?(?:conversaci[oó]n|charla)\s+(?:de|sobre|con)?\s+(.+)',
        r'(?:donde|en\s+la\s+que)\s+(?:habl[aá]bamos|estábamos)\s+(?:de|sobre)?\s+(.+)',
        r'(?:aquella|esa)\s+(?:conversaci[oó]n|charla|plática)\s+(?:de|sobre|del)?\s+(.+)'
    ]
    for patron in patrones_retomar:
        match = re.search(patron, mensaje_lower)
        if match:
            texto_busqueda = match.group(1).strip()
            palabras_ignorar = {'la', 'el', 'de', 'del', 'sobre', 'con', 'que', 'conversacion', 'charla', 'platica', 'tema'}
            palabras = [p for p in texto_busqueda.split() if p not in palabras_ignorar and len(p) > 2]
            return {
                'quiere_retomar': True,
                'palabras_busqueda': palabras,
                'texto_original': texto_busqueda
            }
    return {
        'quiere_retomar': False,
        'palabras_busqueda': [],
        'texto_original': ''
    }

def buscar_conversacion_inteligente(db_path, palabras_clave):
    import json
    if not palabras_clave:
        return []
    resultados_con_score = []
    rows = execute_query(
        db_path,
        '''SELECT c.id, c.titulo, c.descripcion, c.categoria, c.tags, c.fecha_ultima_actividad, c.num_mensajes, c.proyecto_relacionado FROM conversaciones c WHERE c.estado = 'activa' ORDER BY c.fecha_ultima_actividad DESC''',
        [],
        fetchall=True
    )
    for row in rows or []:
        conv_id, titulo, desc, cat, tags_json, fecha, num_msg, proyecto = row
        score = 0
        texto_busqueda = f"{titulo} {desc} {cat} {proyecto}".lower()
        if tags_json:
            tags = json.loads(tags_json)
            texto_busqueda += " " + " ".join(tags)
        for palabra in palabras_clave:
            if palabra.lower() in texto_busqueda:
                score += texto_busqueda.count(palabra.lower())
        for palabra in palabras_clave:
            if palabra.lower() in titulo.lower():
                score += 3
        if score > 0:
            resultados_con_score.append({
                'id': conv_id,
                'titulo': titulo,
                'descripcion': desc,
                'categoria': cat,
                'tags': json.loads(tags_json) if tags_json else [],
                'fecha': fecha,
                'mensajes': num_msg,
                'proyecto': proyecto,
                'score': score
            })
    resultados_con_score.sort(key=lambda x: x['score'], reverse=True)
    return resultados_con_score[:5]
