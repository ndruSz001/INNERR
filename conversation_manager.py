"""
Sistema de Gestión de Conversaciones para TARS
Permite:
- Crear, listar, retomar, archivar conversaciones
- Elegir modo: ocasional vs continuar conversación
- Filtros al inicio para contexto
- Guardado inteligente al inicio y al final
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid


class ConversationManager:
    """
    Gestor de conversaciones con memoria persistente
    Diferenciador: TARS recuerda TODAS tus conversaciones anteriores
    """
    
    def __init__(self, db_path="tars_lifelong/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_conversation = None
        self.init_database()
    
    def init_database(self):
        """Inicializa base de datos de conversaciones"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tabla de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones (
                id TEXT PRIMARY KEY,
                titulo TEXT,
                descripcion TEXT,
                categoria TEXT,
                fecha_inicio TEXT,
                fecha_ultima_actividad TEXT,
                num_mensajes INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'activa',
                tags TEXT,
                proyecto_relacionado TEXT,
                importancia INTEGER DEFAULT 5,
                metadata TEXT,
                es_integradora INTEGER DEFAULT 0,
                objetivo TEXT,
                conclusiones TEXT,
                resultados TEXT
            )
        ''')
        
        # Tabla de mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversacion_id TEXT,
                timestamp TEXT,
                tipo TEXT,
                contenido TEXT,
                metadata TEXT,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id)
            )
        ''')
        
        # Tabla de contexto de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contexto_conversacion (
                conversacion_id TEXT,
                clave TEXT,
                valor TEXT,
                timestamp TEXT,
                PRIMARY KEY (conversacion_id, clave),
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id)
            )
        ''')
        
        # Tabla de resúmenes de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumenes (
                conversacion_id TEXT PRIMARY KEY,
                resumen_corto TEXT,
                resumen_largo TEXT,
                palabras_clave TEXT,
                temas_principales TEXT,
                fecha_generacion TEXT,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id)
            )
        ''')
        
        # Tabla de relaciones entre conversaciones (grafo de conocimiento)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relaciones_conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversacion_origen TEXT,
                conversacion_destino TEXT,
                tipo_relacion TEXT,
                descripcion TEXT,
                relevancia INTEGER DEFAULT 5,
                fecha_vinculacion TEXT,
                metadata TEXT,
                FOREIGN KEY (conversacion_origen) REFERENCES conversaciones(id),
                FOREIGN KEY (conversacion_destino) REFERENCES conversaciones(id)
            )
        ''')
        
        # Índices para búsquedas eficientes en grafo
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relaciones_origen 
            ON relaciones_conversaciones(conversacion_origen)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relaciones_destino 
            ON relaciones_conversaciones(conversacion_destino)
        ''')
        
        conn.commit()
        conn.close()
    
    def nueva_conversacion(
        self,
        titulo: str = None,
        categoria: str = "general",
        descripcion: str = "",
        proyecto_relacionado: str = None,
        tags: List[str] = None,
        auto_titulo: bool = True
    ) -> str:
        """
        Crea nueva conversación
        
        Args:
            titulo: Título de la conversación (None = auto-generado)
            categoria: Tipo (investigacion, desarrollo, analisis, casual, etc.)
            descripcion: Descripción opcional
            proyecto_relacionado: ID de proyecto relacionado
            tags: Etiquetas para organización
            auto_titulo: Si es True, genera título automático después
        
        Returns:
            ID de la conversación
        """
        conv_id = str(uuid.uuid4())[:8]  # ID corto
        
        # Título por defecto si no se proporciona
        if titulo is None:
            if auto_titulo:
                titulo = f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            else:
                titulo = "Sin título"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        tags_str = json.dumps(tags) if tags else json.dumps([])
        
        cursor.execute('''
            INSERT INTO conversaciones 
            (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, 
             estado, tags, proyecto_relacionado, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id, titulo, descripcion, categoria, now, now,
            'activa', tags_str, proyecto_relacionado,
            json.dumps({"auto_titulo": auto_titulo})
        ))
        
        conn.commit()
        conn.close()
        
        self.current_conversation = conv_id
        
        print(f"\n💬 Nueva conversación iniciada")
        print(f"   ID: {conv_id}")
        print(f"   Categoría: {categoria}")
        if proyecto_relacionado:
            print(f"   Proyecto: {proyecto_relacionado}")
        
        return conv_id
    
    def agregar_mensaje(
        self,
        conversacion_id: str,
        tipo: str,  # "user", "tars", "system"
        contenido: str,
        metadata: Dict = None
    ):
        """Agrega mensaje a conversación existente"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_str = json.dumps(metadata) if metadata else json.dumps({})
        
        cursor.execute('''
            INSERT INTO mensajes (conversacion_id, timestamp, tipo, contenido, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversacion_id, timestamp, tipo, contenido, metadata_str))
        
        # Actualizar última actividad y contador
        cursor.execute('''
            UPDATE conversaciones
            SET fecha_ultima_actividad = ?,
                num_mensajes = num_mensajes + 1
            WHERE id = ?
        ''', (timestamp, conversacion_id))
        
        conn.commit()
        conn.close()
        
        # Auto-generar título si es el primer mensaje del usuario
        self._auto_generar_titulo_si_necesario(conversacion_id)
    
    def _auto_generar_titulo_si_necesario(self, conversacion_id: str):
        """Genera título automático basado en primer mensaje si está configurado"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Verificar si necesita auto-título
        cursor.execute('''
            SELECT titulo, num_mensajes, metadata
            FROM conversaciones
            WHERE id = ?
        ''', (conversacion_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        titulo, num_mensajes, metadata_str = result
        metadata = json.loads(metadata_str) if metadata_str else {}
        
        # Solo generar si tiene auto_titulo=True y es el primer mensaje del usuario
        if metadata.get("auto_titulo") and num_mensajes == 1:
            # Obtener primer mensaje del usuario
            cursor.execute('''
                SELECT contenido FROM mensajes
                WHERE conversacion_id = ? AND tipo = 'user'
                ORDER BY timestamp ASC
                LIMIT 1
            ''', (conversacion_id,))
            
            primer_mensaje = cursor.fetchone()
            if primer_mensaje:
                # Generar título basado en primeras palabras (máximo 60 caracteres)
                nuevo_titulo = self._generar_titulo_desde_mensaje(primer_mensaje[0])
                
                cursor.execute('''
                    UPDATE conversaciones
                    SET titulo = ?
                    WHERE id = ?
                ''', (nuevo_titulo, conversacion_id))
                
                conn.commit()
                print(f"   📝 Título generado: {nuevo_titulo}")
        
        conn.close()
    
    def _generar_titulo_desde_mensaje(self, mensaje: str) -> str:
        """Genera título descriptivo desde mensaje"""
        # Limpiar y truncar
        titulo = mensaje.strip()
        
        # Quitar preguntas muy largas
        if len(titulo) > 60:
            # Buscar primer punto o coma
            for separador in ['.', ',', ';', '?', '!']:
                if separador in titulo[:60]:
                    titulo = titulo.split(separador)[0]
                    break
            else:
                titulo = titulo[:60]
        
        # Capitalizar primera letra
        titulo = titulo[0].upper() + titulo[1:] if titulo else "Conversación"
        
        return titulo
    
    def listar_conversaciones(
        self,
        categoria: str = None,
        estado: str = "activa",
        proyecto: str = None,
        limit: int = 20,
        orden: str = "reciente"  # "reciente", "antiguo", "mensajes", "importancia"
    ) -> List[Dict]:
        """
        Lista conversaciones con filtros
        
        Args:
            categoria: Filtrar por categoría
            estado: 'activa', 'archivada', 'todas'
            proyecto: Filtrar por proyecto relacionado
            limit: Número máximo de resultados
            orden: Criterio de ordenamiento
        
        Returns:
            Lista de conversaciones
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM conversaciones WHERE 1=1"
        params = []
        
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        
        if estado != "todas":
            query += " AND estado = ?"
            params.append(estado)
        
        if proyecto:
            query += " AND proyecto_relacionado = ?"
            params.append(proyecto)
        
        # Ordenamiento
        orden_sql = {
            "reciente": "fecha_ultima_actividad DESC",
            "antiguo": "fecha_inicio ASC",
            "mensajes": "num_mensajes DESC",
            "importancia": "importancia DESC, fecha_ultima_actividad DESC"
        }
        
        query += f" ORDER BY {orden_sql.get(orden, 'fecha_ultima_actividad DESC')}"
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        
        conversaciones = []
        for row in cursor.fetchall():
            conversaciones.append({
                "id": row[0],
                "titulo": row[1],
                "descripcion": row[2],
                "categoria": row[3],
                "fecha_inicio": row[4],
                "fecha_ultima_actividad": row[5],
                "num_mensajes": row[6],
                "estado": row[7],
                "tags": json.loads(row[8]) if row[8] else [],
                "proyecto_relacionado": row[9],
                "importancia": row[10]
            })
        
        conn.close()
        return conversaciones
    
    def continuar_conversacion(self, conversacion_id: str) -> Dict:
        """
        Carga contexto de conversación anterior para continuar
        
        Returns:
            Dict con información de la conversación y últimos mensajes
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Obtener info de conversación
        cursor.execute('''
            SELECT * FROM conversaciones WHERE id = ?
        ''', (conversacion_id,))
        
        conv = cursor.fetchone()
        if not conv:
            conn.close()
            return {"error": "Conversación no encontrada"}
        
        # Obtener últimos 10 mensajes para contexto
        cursor.execute('''
            SELECT tipo, contenido, timestamp
            FROM mensajes
            WHERE conversacion_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (conversacion_id,))
        
        mensajes = []
        for row in cursor.fetchall():
            mensajes.append({
                "tipo": row[0],
                "contenido": row[1],
                "timestamp": row[2]
            })
        
        mensajes.reverse()  # Orden cronológico
        
        # Obtener contexto guardado
        cursor.execute('''
            SELECT clave, valor FROM contexto_conversacion
            WHERE conversacion_id = ?
        ''', (conversacion_id,))
        
        contexto = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        self.current_conversation = conversacion_id
        
        resultado = {
            "id": conv[0],
            "titulo": conv[1],
            "categoria": conv[3],
            "fecha_inicio": conv[4],
            "num_mensajes_total": conv[6],
            "ultimos_mensajes": mensajes,
            "contexto": contexto
        }
        
        print(f"\n📂 Conversación recuperada: {conv[1]}")
        print(f"   Mensajes previos: {conv[6]}")
        print(f"   Última actividad: {conv[5][:10]}")
        
        return resultado
    
    def guardar_contexto(self, conversacion_id: str, clave: str, valor: str):
        """Guarda contexto específico de la conversación"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO contexto_conversacion
            (conversacion_id, clave, valor, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (conversacion_id, clave, valor, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def archivar_conversacion(self, conversacion_id: str):
        """Marca conversación como archivada"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversaciones
            SET estado = 'archivada'
            WHERE id = ?
        ''', (conversacion_id,))
        
        conn.commit()
        conn.close()
        
        print(f"📦 Conversación archivada: {conversacion_id}")
    
    def buscar_conversaciones(self, query: str, limit: int = 10) -> List[Dict]:
        """Busca en títulos, descripciones y contenido de mensajes"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Buscar en conversaciones
        cursor.execute('''
            SELECT DISTINCT c.id, c.titulo, c.descripcion, c.categoria, 
                   c.fecha_ultima_actividad, c.num_mensajes
            FROM conversaciones c
            LEFT JOIN mensajes m ON c.id = m.conversacion_id
            WHERE c.titulo LIKE ? OR c.descripcion LIKE ? OR m.contenido LIKE ?
            ORDER BY c.fecha_ultima_actividad DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append({
                "id": row[0],
                "titulo": row[1],
                "descripcion": row[2],
                "categoria": row[3],
                "fecha": row[4],
                "mensajes": row[5]
            })
        
        conn.close()
        return resultados
    
    def generar_resumen_conversacion(self, conversacion_id: str) -> Dict:
        """Genera resumen de conversación completa"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Obtener todos los mensajes
        cursor.execute('''
            SELECT tipo, contenido FROM mensajes
            WHERE conversacion_id = ?
            ORDER BY timestamp ASC
        ''', (conversacion_id,))
        
        mensajes = cursor.fetchall()
        
        # Generar resumen simple (primeros y últimos mensajes)
        if len(mensajes) < 3:
            resumen_corto = "Conversación breve"
            resumen_largo = "\n".join([m[1][:100] for m in mensajes])
        else:
            # Primeros 2 mensajes
            inicio = mensajes[:2]
            # Últimos 2 mensajes
            final = mensajes[-2:]
            
            resumen_corto = f"Tema: {mensajes[0][1][:60]}..."
            resumen_largo = (
                "Inicio:\n" + "\n".join([f"{m[0]}: {m[1][:100]}..." for m in inicio]) +
                "\n...\n" +
                "Final:\n" + "\n".join([f"{m[0]}: {m[1][:100]}..." for m in final])
            )
        
        # Extraer palabras clave (palabras más frecuentes)
        from collections import Counter
        import re
        
        texto_completo = " ".join([m[1] for m in mensajes])
        palabras = re.findall(r'\b\w{4,}\b', texto_completo.lower())
        
        # Palabras comunes a ignorar
        stopwords = {'para', 'esto', 'este', 'esta', 'está', 'como', 'cual', 
                     'pero', 'sobre', 'hacer', 'puede', 'desde', 'entre'}
        
        palabras_filtradas = [p for p in palabras if p not in stopwords]
        palabras_clave = [p for p, _ in Counter(palabras_filtradas).most_common(5)]
        
        # Guardar resumen
        cursor.execute('''
            INSERT OR REPLACE INTO resumenes
            (conversacion_id, resumen_corto, resumen_largo, palabras_clave, 
             temas_principales, fecha_generacion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            conversacion_id,
            resumen_corto,
            resumen_largo,
            json.dumps(palabras_clave),
            json.dumps(["general"]),  # Mejorar con NLP
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "resumen_corto": resumen_corto,
            "resumen_largo": resumen_largo,
            "palabras_clave": palabras_clave
        }
    
    def estadisticas_generales(self) -> Dict:
        """Genera estadísticas generales de todas las conversaciones"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de conversaciones
        cursor.execute("SELECT COUNT(*) FROM conversaciones")
        stats["total_conversaciones"] = cursor.fetchone()[0]
        
        # Por estado
        cursor.execute('''
            SELECT estado, COUNT(*) FROM conversaciones GROUP BY estado
        ''')
        stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Por categoría
        cursor.execute('''
            SELECT categoria, COUNT(*) FROM conversaciones GROUP BY categoria
        ''')
        stats["por_categoria"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total mensajes
        cursor.execute("SELECT SUM(num_mensajes) FROM conversaciones")
        stats["total_mensajes"] = cursor.fetchone()[0] or 0
        
        # Conversación más larga
        cursor.execute('''
            SELECT titulo, num_mensajes FROM conversaciones
            ORDER BY num_mensajes DESC LIMIT 1
        ''')
        longest = cursor.fetchone()
        if longest:
            stats["conversacion_mas_larga"] = {
                "titulo": longest[0],
                "mensajes": longest[1]
            }
        
        conn.close()
        return stats
    
    def detectar_intencion_retomar(self, mensaje: str) -> Dict:
        """
        Detecta si el usuario quiere retomar una conversación anterior
        
        Palabras clave:
        - volvamos a, regresemos a, continuemos con, retomemos
        - vamos a seguir con, sigamos con
        - recupera la conversación de/sobre
        - abre la conversación de
        
        Returns:
            Dict con 'quiere_retomar' (bool) y 'palabras_busqueda' (list)
        """
        import re
        
        mensaje_lower = mensaje.lower()
        
        # Patrones de detección
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
                # Extraer palabras clave de la búsqueda
                texto_busqueda = match.group(1).strip()
                
                # Limpiar palabras comunes
                palabras_ignorar = {'la', 'el', 'de', 'del', 'sobre', 'con', 'que', 
                                   'conversacion', 'charla', 'platica', 'tema'}
                
                palabras = [p for p in texto_busqueda.split() 
                           if p not in palabras_ignorar and len(p) > 2]
                
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
    
    def buscar_conversacion_inteligente(self, palabras_clave: List[str]) -> List[Dict]:
        """
        Búsqueda inteligente de conversaciones usando palabras clave
        Ordena por relevancia (más coincidencias primero)
        """
        if not palabras_clave:
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Buscar en títulos, descripciones, tags y contenido
        resultados_con_score = []
        
        # Obtener todas las conversaciones activas
        cursor.execute('''
            SELECT c.id, c.titulo, c.descripcion, c.categoria, c.tags,
                   c.fecha_ultima_actividad, c.num_mensajes, c.proyecto_relacionado
            FROM conversaciones c
            WHERE c.estado = 'activa'
            ORDER BY c.fecha_ultima_actividad DESC
        ''')
        
        for row in cursor.fetchall():
            conv_id, titulo, desc, cat, tags_json, fecha, num_msg, proyecto = row
            
            # Calcular score de relevancia
            score = 0
            texto_busqueda = f"{titulo} {desc} {cat} {proyecto}".lower()
            
            # Tags
            if tags_json:
                tags = json.loads(tags_json)
                texto_busqueda += " " + " ".join(tags)
            
            # Contar coincidencias
            for palabra in palabras_clave:
                if palabra.lower() in texto_busqueda:
                    score += texto_busqueda.count(palabra.lower())
            
            # Bonus por coincidencia en título
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
        
        conn.close()
        
        # Ordenar por score descendente
        resultados_con_score.sort(key=lambda x: x['score'], reverse=True)
        
        return resultados_con_score[:5]  # Top 5 resultados
    
    # ========================================================================
    # SISTEMA DE GRAFOS DE CONOCIMIENTO
    # Arquitectura de memoria episódica estructurada
    # ========================================================================
    
    def crear_conversacion_integradora(
        self,
        titulo: str,
        objetivo: str,
        conversaciones_base: List[str],
        categoria: str = "sintesis",
        descripcion: str = ""
    ) -> str:
        """
        Crea una conversación de nivel superior que integra conocimiento
        de múltiples conversaciones independientes.
        
        Esta conversación NO modifica las originales, actúa como nodo conector
        que mantiene trazabilidad del origen de cada fragmento de conocimiento.
        
        Args:
            titulo: Título de la síntesis
            objetivo: Propósito declarado de la integración
            conversaciones_base: IDs de conversaciones que se integran
            categoria: Tipo (sintesis, analisis_cruzado, convergencia)
            descripcion: Contexto de por qué se integran
        
        Returns:
            ID de la conversación integradora
        """
        conv_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Crear conversación integradora
        cursor.execute('''
            INSERT INTO conversaciones 
            (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, 
             estado, es_integradora, objetivo, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id, titulo, descripcion, categoria, now, now,
            'activa', 1, objetivo,
            json.dumps({
                "conversaciones_base": conversaciones_base,
                "tipo_integracion": "sintesis",
                "fecha_integracion": now
            })
        ))
        
        # Crear relaciones con conversaciones base
        for conv_base in conversaciones_base:
            cursor.execute('''
                INSERT INTO relaciones_conversaciones
                (conversacion_origen, conversacion_destino, tipo_relacion, 
                 descripcion, fecha_vinculacion, relevancia)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                conv_id, conv_base, 'integra',
                f"Conversación integradora que sintetiza conocimiento de {conv_base}",
                now, 10
            ))
        
        conn.commit()
        conn.close()
        
        print(f"\n🔗 Conversación integradora creada: {conv_id}")
        print(f"   Integra {len(conversaciones_base)} conversaciones base")
        print(f"   Objetivo: {objetivo}")
        
        return conv_id
    
    def vincular_conversaciones(
        self,
        conv_origen: str,
        conv_destino: str,
        tipo_relacion: str,
        descripcion: str = "",
        relevancia: int = 5
    ) -> bool:
        """
        Vincula dos conversaciones explícitamente (control del usuario).
        
        Tipos de relación:
        - 'relacionada': Temas relacionados
        - 'continua': Una continúa la otra
        - 'complementa': Información complementaria
        - 'contradice': Información contradictoria
        - 'depende': Requiere contexto de la otra
        - 'converge': Llegan a conclusiones similares
        - 'diverge': Llegan a conclusiones diferentes
        
        Args:
            conv_origen: ID conversación origen
            conv_destino: ID conversación destino
            tipo_relacion: Tipo de relación
            descripcion: Descripción de la relación
            relevancia: 1-10, importancia de la relación
        
        Returns:
            True si se vinculó exitosamente
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Verificar que ambas conversaciones existen
        cursor.execute('SELECT id FROM conversaciones WHERE id IN (?, ?)', 
                      (conv_origen, conv_destino))
        
        if len(cursor.fetchall()) != 2:
            conn.close()
            return False
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO relaciones_conversaciones
            (conversacion_origen, conversacion_destino, tipo_relacion, 
             descripcion, relevancia, fecha_vinculacion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conv_origen, conv_destino, tipo_relacion, descripcion, relevancia, now))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Vinculadas: {conv_origen} → {conv_destino} ({tipo_relacion})")
        
        return True
    
    def obtener_conversaciones_relacionadas(
        self,
        conv_id: str,
        tipo_relacion: Optional[str] = None,
        min_relevancia: int = 0
    ) -> Dict[str, List[Dict]]:
        """
        Obtiene todas las conversaciones relacionadas con una dada.
        
        Returns:
            Dict con 'salientes' (esta→otras) y 'entrantes' (otras→esta)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Relaciones salientes (esta conversación referencia otras)
        query_salientes = '''
            SELECT r.conversacion_destino, r.tipo_relacion, r.descripcion, 
                   r.relevancia, r.fecha_vinculacion, c.titulo, c.categoria
            FROM relaciones_conversaciones r
            JOIN conversaciones c ON r.conversacion_destino = c.id
            WHERE r.conversacion_origen = ?
        '''
        
        params = [conv_id]
        
        if tipo_relacion:
            query_salientes += ' AND r.tipo_relacion = ?'
            params.append(tipo_relacion)
        
        if min_relevancia > 0:
            query_salientes += ' AND r.relevancia >= ?'
            params.append(min_relevancia)
        
        cursor.execute(query_salientes, params)
        
        salientes = []
        for row in cursor.fetchall():
            salientes.append({
                'id': row[0],
                'tipo_relacion': row[1],
                'descripcion': row[2],
                'relevancia': row[3],
                'fecha_vinculacion': row[4],
                'titulo': row[5],
                'categoria': row[6]
            })
        
        # Relaciones entrantes (otras conversaciones referencian esta)
        query_entrantes = '''
            SELECT r.conversacion_origen, r.tipo_relacion, r.descripcion, 
                   r.relevancia, r.fecha_vinculacion, c.titulo, c.categoria
            FROM relaciones_conversaciones r
            JOIN conversaciones c ON r.conversacion_origen = c.id
            WHERE r.conversacion_destino = ?
        '''
        
        params = [conv_id]
        
        if tipo_relacion:
            query_entrantes += ' AND r.tipo_relacion = ?'
            params.append(tipo_relacion)
        
        if min_relevancia > 0:
            query_entrantes += ' AND r.relevancia >= ?'
            params.append(min_relevancia)
        
        cursor.execute(query_entrantes, params)
        
        entrantes = []
        for row in cursor.fetchall():
            entrantes.append({
                'id': row[0],
                'tipo_relacion': row[1],
                'descripcion': row[2],
                'relevancia': row[3],
                'fecha_vinculacion': row[4],
                'titulo': row[5],
                'categoria': row[6]
            })
        
        conn.close()
        
        return {
            'salientes': salientes,
            'entrantes': entrantes,
            'total': len(salientes) + len(entrantes)
        }
    
    def actualizar_conclusiones(
        self,
        conv_id: str,
        conclusiones: str,
        resultados: Optional[str] = None
    ) -> bool:
        """
        Actualiza las conclusiones y resultados de una conversación.
        
        Esto permite que cada conversación preserve su conocimiento destilado
        para ser reutilizado en conversaciones integradoras.
        
        Args:
            conv_id: ID de la conversación
            conclusiones: Conclusiones principales
            resultados: Resultados obtenidos (opcional)
        
        Returns:
            True si se actualizó exitosamente
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversaciones
            SET conclusiones = ?, resultados = ?
            WHERE id = ?
        ''', (conclusiones, resultados, conv_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            print(f"✅ Conclusiones actualizadas para {conv_id}")
            return True
        
        return False
    
    def analizar_convergencias(
        self,
        conv_ids: List[str],
        modo: str = "temas"
    ) -> Dict:
        """
        Analiza convergencias, contradicciones o vacíos entre conversaciones.
        
        Modos:
        - 'temas': Analiza temas comunes
        - 'conclusiones': Compara conclusiones
        - 'palabras_clave': Analiza overlap de palabras clave
        
        Returns:
            Dict con análisis de convergencias/divergencias
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Obtener información de todas las conversaciones
        placeholders = ','.join(['?'] * len(conv_ids))
        query = f'''
            SELECT c.id, c.titulo, c.categoria, c.tags, c.conclusiones,
                   r.palabras_clave, r.temas_principales
            FROM conversaciones c
            LEFT JOIN resumenes r ON c.id = r.conversacion_id
            WHERE c.id IN ({placeholders})
        '''
        
        cursor.execute(query, conv_ids)
        conversaciones = cursor.fetchall()
        conn.close()
        
        if len(conversaciones) < 2:
            return {"error": "Se requieren al menos 2 conversaciones"}
        
        analisis = {
            'num_conversaciones': len(conversaciones),
            'conversaciones': [],
            'temas_comunes': [],
            'categorias': {},
            'palabras_frecuentes': {},
            'convergencias': [],
            'divergencias': []
        }
        
        # Recopilar información
        todas_palabras = []
        todas_categorias = []
        
        for conv in conversaciones:
            conv_id, titulo, categoria, tags_json, conclusiones, palabras_clave, temas = conv
            
            analisis['conversaciones'].append({
                'id': conv_id,
                'titulo': titulo,
                'categoria': categoria
            })
            
            # Categorías
            todas_categorias.append(categoria)
            
            # Palabras clave
            if palabras_clave:
                palabras = palabras_clave.split(',')
                todas_palabras.extend([p.strip().lower() for p in palabras])
            
            # Tags
            if tags_json:
                tags = json.loads(tags_json)
                todas_palabras.extend([t.lower() for t in tags])
        
        # Análisis de frecuencias
        from collections import Counter
        
        palabra_freq = Counter(todas_palabras)
        categoria_freq = Counter(todas_categorias)
        
        # Palabras que aparecen en múltiples conversaciones (convergencias)
        for palabra, freq in palabra_freq.most_common():
            if freq > 1:
                analisis['temas_comunes'].append({
                    'palabra': palabra,
                    'frecuencia': freq,
                    'porcentaje': (freq / len(conversaciones)) * 100
                })
        
        analisis['categorias'] = dict(categoria_freq)
        
        # Detectar convergencias (misma categoría, temas comunes)
        if len(set(todas_categorias)) == 1:
            analisis['convergencias'].append({
                'tipo': 'categoria_unica',
                'valor': todas_categorias[0],
                'descripcion': 'Todas las conversaciones pertenecen a la misma categoría'
            })
        
        # Detectar divergencias (categorías muy diferentes)
        if len(set(todas_categorias)) == len(conversaciones):
            analisis['divergencias'].append({
                'tipo': 'categorias_diversas',
                'descripcion': 'Cada conversación tiene categoría diferente'
            })
        
        return analisis
    
    def obtener_grafo_conocimiento(
        self,
        profundidad: int = 2,
        conv_raiz: Optional[str] = None
    ) -> Dict:
        """
        Genera representación del grafo de conocimiento.
        
        Args:
            profundidad: Niveles de relaciones a explorar
            conv_raiz: Conversación desde la que empezar (None = todas activas)
        
        Returns:
            Dict con nodos (conversaciones) y aristas (relaciones)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Obtener nodos (conversaciones)
        if conv_raiz:
            # Empezar desde conversación específica
            nodos_visitados = set([conv_raiz])
            nodos_pendientes = [conv_raiz]
            nivel_actual = 0
            
            grafo = {
                'nodos': {},
                'aristas': [],
                'estadisticas': {}
            }
            
            while nodos_pendientes and nivel_actual < profundidad:
                nodo_actual = nodos_pendientes.pop(0)
                
                # Obtener info del nodo
                cursor.execute('''
                    SELECT titulo, categoria, es_integradora, objetivo, num_mensajes
                    FROM conversaciones WHERE id = ?
                ''', (nodo_actual,))
                
                row = cursor.fetchone()
                if row:
                    grafo['nodos'][nodo_actual] = {
                        'titulo': row[0],
                        'categoria': row[1],
                        'es_integradora': bool(row[2]),
                        'objetivo': row[3],
                        'num_mensajes': row[4],
                        'nivel': nivel_actual
                    }
                
                # Obtener relaciones
                cursor.execute('''
                    SELECT conversacion_destino, tipo_relacion, relevancia
                    FROM relaciones_conversaciones
                    WHERE conversacion_origen = ?
                ''', (nodo_actual,))
                
                for rel in cursor.fetchall():
                    destino, tipo, relevancia = rel
                    
                    grafo['aristas'].append({
                        'origen': nodo_actual,
                        'destino': destino,
                        'tipo': tipo,
                        'relevancia': relevancia
                    })
                    
                    if destino not in nodos_visitados:
                        nodos_visitados.add(destino)
                        nodos_pendientes.append(destino)
                
                nivel_actual += 1
        
        else:
            # Todas las conversaciones activas
            cursor.execute('''
                SELECT id, titulo, categoria, es_integradora, objetivo, num_mensajes
                FROM conversaciones
                WHERE estado = 'activa'
            ''')
            
            grafo = {
                'nodos': {},
                'aristas': [],
                'estadisticas': {}
            }
            
            for row in cursor.fetchall():
                conv_id, titulo, cat, es_int, obj, num_msg = row
                grafo['nodos'][conv_id] = {
                    'titulo': titulo,
                    'categoria': cat,
                    'es_integradora': bool(es_int),
                    'objetivo': obj,
                    'num_mensajes': num_msg
                }
            
            # Todas las relaciones
            cursor.execute('''
                SELECT conversacion_origen, conversacion_destino, tipo_relacion, relevancia
                FROM relaciones_conversaciones
            ''')
            
            for row in cursor.fetchall():
                grafo['aristas'].append({
                    'origen': row[0],
                    'destino': row[1],
                    'tipo': row[2],
                    'relevancia': row[3]
                })
        
        conn.close()
        
        # Estadísticas
        grafo['estadisticas'] = {
            'num_nodos': len(grafo['nodos']),
            'num_aristas': len(grafo['aristas']),
            'nodos_integradores': sum(1 for n in grafo['nodos'].values() if n['es_integradora']),
            'nodos_independientes': sum(1 for nid in grafo['nodos'].keys() 
                                       if not any(a['origen'] == nid or a['destino'] == nid 
                                                 for a in grafo['aristas']))
        }
        
        return grafo


if __name__ == "__main__":
    # Demo
    print("\n" + "="*70)
    print("TARS - Sistema de Gestión de Conversaciones")
    print("="*70)
    
    manager = ConversationManager()
    
    # Estadísticas
    stats = manager.estadisticas_generales()
    print(f"\n📊 Estadísticas:")
    print(f"   Total conversaciones: {stats['total_conversaciones']}")
    print(f"   Total mensajes: {stats['total_mensajes']}")
