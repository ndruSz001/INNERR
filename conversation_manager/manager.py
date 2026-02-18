"""
Copyright (c) 2026 ndrz02
Todos los derechos reservados.
Licencia MIT: ver LICENSE y AUTORÍA_Y_LICENCIA.md
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from conversation_manager.db import execute_query, init_database


class ConversationManager:
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	"""
	Gestor principal de conversaciones.
	Modular, documentado y con manejo robusto de errores.
	"""

	def __init__(self, db_path="conversations.db"):
		"""
		Inicializa el gestor y la base de datos.
		Args:
			db_path (str): Ruta a la base de datos SQLite.
		"""
		self.db_path = db_path
		self.current_conversation = None
		init_database(self.db_path)

	def agregar_mensaje(self, conversacion_id: str, tipo: str, contenido: str, metadata: dict = None):
		"""
		Agrega un mensaje a una conversación existente.
		Args:
			conversacion_id (str): ID de la conversación.
			tipo (str): Tipo de mensaje ('user', 'assistant', etc).
			contenido (str): Texto del mensaje.
			metadata (dict): Metadatos opcionales.
		Returns:
			int: ID del mensaje insertado.
		"""
		if metadata is None:
			metadata = {}
		params = [
			conversacion_id,
			datetime.now().isoformat(),
			tipo,
			contenido,
			json.dumps(metadata)
		]
		execute_query(
			self.db_path,
			'''INSERT INTO mensajes (conversacion_id, timestamp, tipo, contenido, metadata) VALUES (?, ?, ?, ?, ?)''',
			params,
			commit=True
		)
		# Actualizar contador de mensajes y última actividad
		execute_query(
			self.db_path,
			'''UPDATE conversaciones SET num_mensajes = num_mensajes + 1, fecha_ultima_actividad = ? WHERE id = ?''',
			[params[1], conversacion_id],
			commit=True
		)

	def nueva_conversacion(self, titulo=None, categoria="general", descripcion="", proyecto_relacionado=None, tags=None, auto_titulo=False):
		"""
		Crea una nueva conversación y la guarda en la base de datos.
		Args:
			titulo (str): Título de la conversación.
			categoria (str): Categoría temática.
			descripcion (str): Descripción opcional.
			proyecto_relacionado (str): Proyecto asociado.
			tags (list): Etiquetas.
			auto_titulo (bool): Generar título automáticamente si no se provee.
		Returns:
			str: ID de la conversación creada.
		"""
		import uuid
		conv_id = str(uuid.uuid4())[:8]
		now = datetime.now().isoformat()
		if auto_titulo or not titulo:
			titulo = f"Conversación {now[:10]}"
		if tags is None:
			tags = []
		try:
			execute_query(
				self.db_path,
				'''INSERT INTO conversaciones (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, estado, tags, proyecto_relacionado, importancia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
				[
					conv_id,
					titulo,
					descripcion,
					categoria,
					now,
					now,
					'activa',
					json.dumps(tags),
					proyecto_relacionado,
					5
				],
				commit=True
			)
			self.current_conversation = conv_id
			return conv_id
		except Exception as e:
			logger.error(f"No se pudo crear la conversación: {e}")
			raise

	def init_database(self):
		"""Inicializa la base de datos de conversaciones (compatibilidad para tests)."""
		init_database(self.db_path)

	def _generar_titulo_desde_mensaje(self, mensaje: str) -> str:
		"""Genera un título a partir del primer mensaje."""
		titulo = mensaje.strip()
		if len(titulo) > 60:
			for separador in ['.', ',', ';', '?', '!']:
				if separador in titulo[:60]:
					titulo = titulo.split(separador)[0]
					break
			else:
				titulo = titulo[:60]
		titulo = titulo[0].upper() + titulo[1:] if titulo else "Conversación"
		return titulo

	def guardar_contexto(self, conversacion_id: str, clave: str, valor: str):
		"""Guarda o actualiza un valor de contexto asociado a una conversación."""
		execute_query(
			self.db_path,
			'''INSERT OR REPLACE INTO contexto_conversacion (conversacion_id, clave, valor, timestamp) VALUES (?, ?, ?, ?)''',
			[conversacion_id, clave, valor, datetime.now().isoformat()],
			commit=True
		)

	def archivar_conversacion(self, conversacion_id: str):
		"""Marca una conversación como archivada."""
		execute_query(
			self.db_path,
			'''UPDATE conversaciones SET estado = 'archivada' WHERE id = ?''',
			[conversacion_id],
			commit=True
		)
		logger.info(f"📦 Conversación archivada: {conversacion_id}")

	def estadisticas_generales(self) -> Dict:
		stats = {}
		total_conv = execute_query(
			self.db_path,
			"SELECT COUNT(*) FROM conversaciones",
			[],
			fetchone=True
		)
		stats["total_conversaciones"] = total_conv[0] if total_conv else 0
		rows_estado = execute_query(
			self.db_path,
			"SELECT estado, COUNT(*) FROM conversaciones GROUP BY estado",
			[],
			fetchall=True
		)
		stats["por_estado"] = {row[0]: row[1] for row in rows_estado or []}
		rows_categoria = execute_query(
			self.db_path,
			"SELECT categoria, COUNT(*) FROM conversaciones GROUP BY categoria",
			[],
			fetchall=True
		)
		stats["por_categoria"] = {row[0]: row[1] for row in rows_categoria or []}
		total_msg = execute_query(
			self.db_path,
			"SELECT SUM(num_mensajes) FROM conversaciones",
			[],
			fetchone=True
		)
		stats["total_mensajes"] = total_msg[0] if total_msg and total_msg[0] else 0
		longest = execute_query(
			self.db_path,
			"SELECT titulo, num_mensajes FROM conversaciones ORDER BY num_mensajes DESC LIMIT 1",
			[],
			fetchone=True
		)
		if longest:
			stats["conversacion_mas_larga"] = {
				"titulo": longest[0],
				"mensajes": longest[1]
			}
		return stats

	def detectar_intencion_retomar(self, mensaje: str) -> Dict:
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
			if not palabras_clave:
				return []
			resultados_con_score = []
			rows = execute_query(
				self.db_path,
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

		def crear_conversacion_integradora(self, titulo: str, objetivo: str, conversaciones_base: List[str], categoria: str = "sintesis", descripcion: str = "") -> str:
			from conversation_manager.graph import crear_conversacion_integradora
			return crear_conversacion_integradora(self.db_path, titulo, objetivo, conversaciones_base, categoria, descripcion)

		def vincular_conversaciones(self, conv_origen: str, conv_destino: str, tipo_relacion: str, descripcion: str = "", relevancia: int = 5) -> bool:
			from conversation_manager.graph import vincular_conversaciones
			return vincular_conversaciones(self.db_path, conv_origen, conv_destino, tipo_relacion, descripcion, relevancia)

		def obtener_conversaciones_relacionadas(self, conv_id: str, tipo_relacion: Optional[str] = None, min_relevancia: int = 0) -> Dict[str, List[Dict]]:
			from conversation_manager.graph import obtener_conversaciones_relacionadas
			return obtener_conversaciones_relacionadas(self.db_path, conv_id, tipo_relacion, min_relevancia)

		def actualizar_conclusiones(self, conv_id: str, conclusiones: str, resultados: Optional[str] = None) -> bool:
			from conversation_manager.graph import actualizar_conclusiones
			return actualizar_conclusiones(self.db_path, conv_id, conclusiones, resultados)

		def analizar_convergencias(self, conv_ids: List[str], modo: str = "temas") -> Dict:
			from conversation_manager.graph import analizar_convergencias
			return analizar_convergencias(self.db_path, conv_ids, modo)

		def obtener_grafo_conocimiento(self, profundidad: int = 2, conv_raiz: Optional[str] = None) -> Dict:
			from conversation_manager.graph import obtener_grafo_conocimiento
			return obtener_grafo_conocimiento(self.db_path, profundidad, conv_raiz)

		def listar_conversaciones(self, categoria: str = None, estado: str = "activa", proyecto: str = None, limit: int = 20, orden: str = "reciente") -> List[Dict]:
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
			orden_sql = {
				"reciente": "fecha_ultima_actividad DESC",
				"antiguo": "fecha_inicio ASC",
				"mensajes": "num_mensajes DESC",
				"importancia": "importancia DESC, fecha_ultima_actividad DESC"
			}
			query += f" ORDER BY {orden_sql.get(orden, 'fecha_ultima_actividad DESC')}"
			query += f" LIMIT {limit}"
			rows = execute_query(self.db_path, query, params, fetchall=True)
			conversaciones = []
			for row in rows or []:
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
			return conversaciones

		def continuar_conversacion(self, conversacion_id: str) -> Dict:
			conv = execute_query(
				self.db_path,
				'SELECT * FROM conversaciones WHERE id = ?',
				[conversacion_id],
				fetchone=True
			)
			if not conv:
				return {"error": "Conversación no encontrada"}
			rows = execute_query(
				self.db_path,
				'''SELECT tipo, contenido, timestamp FROM mensajes WHERE conversacion_id = ? ORDER BY timestamp DESC LIMIT 10''',
				[conversacion_id],
				fetchall=True
			)
			mensajes = []
			for row in rows or []:
				mensajes.append({
					"tipo": row[0],
					"contenido": row[1],
					"timestamp": row[2]
				})
			mensajes.reverse()
			contexto_rows = execute_query(
				self.db_path,
				'SELECT clave, valor FROM contexto_conversacion WHERE conversacion_id = ?',
				[conversacion_id],
				fetchall=True
			)
			contexto = {row[0]: row[1] for row in contexto_rows or []}
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
			logger.info(f"\n📂 Conversación recuperada: {conv[1]}")
			logger.info(f"   Mensajes previos: {conv[6]}")
			logger.info(f"   Última actividad: {conv[5][:10]}")
			return resultado

	def __init__(self, db_path="conversations.db"):
		"""
		Inicializa el gestor y la base de datos.
		Args:
			db_path (str): Ruta a la base de datos SQLite.
		"""
		self.db_path = db_path
		self.current_conversation = None
		init_database(self.db_path)

	def nueva_conversacion(self, titulo=None, categoria="general", descripcion="", proyecto_relacionado=None, tags=None, auto_titulo=False):
		"""
		Crea una nueva conversación y la guarda en la base de datos.
		Args:
			titulo (str): Título de la conversación.
			categoria (str): Categoría temática.
			descripcion (str): Descripción opcional.
			proyecto_relacionado (str): Proyecto asociado.
			tags (list): Etiquetas.
			auto_titulo (bool): Generar título automáticamente si no se provee.
		Returns:
			str: ID de la conversación creada.
		"""
		import uuid
		conv_id = str(uuid.uuid4())[:8]
		now = datetime.now().isoformat()
		if auto_titulo or not titulo:
			titulo = f"Conversación {now[:10]}"
		if tags is None:
			tags = []
		try:
			execute_query(
				self.db_path,
				'''INSERT INTO conversaciones (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, estado, tags, proyecto_relacionado, importancia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
				[
					conv_id,
					titulo,
					descripcion,
					categoria,
					now,
					now,
					'activa',
					json.dumps(tags),
					proyecto_relacionado,
					5
				],
				commit=True
			)
			self.current_conversation = conv_id
			return conv_id
		except Exception as e:
			print(f"[ERROR] No se pudo crear la conversación: {e}")
			raise

	def init_database(self):
		"""Inicializa la base de datos de conversaciones (compatibilidad para tests)."""
		init_database(self.db_path)

	def _generar_titulo_desde_mensaje(self, mensaje: str) -> str:
		"""Genera un título a partir del primer mensaje."""
		titulo = mensaje.strip()
		if len(titulo) > 60:
			for separador in ['.', ',', ';', '?', '!']:
				if separador in titulo[:60]:
					titulo = titulo.split(separador)[0]
					break
			else:
				titulo = titulo[:60]
		titulo = titulo[0].upper() + titulo[1:] if titulo else "Conversación"
		return titulo

	def guardar_contexto(self, conversacion_id: str, clave: str, valor: str):
		execute_query(
			self.db_path,
			'''INSERT OR REPLACE INTO contexto_conversacion (conversacion_id, clave, valor, timestamp) VALUES (?, ?, ?, ?)''',
			[conversacion_id, clave, valor, datetime.now().isoformat()],
			commit=True
		)

	def archivar_conversacion(self, conversacion_id: str):
		execute_query(
			self.db_path,
			'''UPDATE conversaciones SET estado = 'archivada' WHERE id = ?''',
			[conversacion_id],
			commit=True
		)
		logger.info(f"📦 Conversación archivada: {conversacion_id}")

	def buscar_conversaciones(self, query: str, limit: int = 10) -> List[Dict]:
		rows = execute_query(
			self.db_path,
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

	def generar_resumen_conversacion(self, conversacion_id: str) -> Dict:
		mensajes = execute_query(
			self.db_path,
			'''SELECT tipo, contenido FROM mensajes WHERE conversacion_id = ? ORDER BY timestamp ASC''',
			[conversacion_id],
			fetchall=True
		)
		if len(mensajes) < 3:
			resumen_corto = "Conversación breve"
			resumen_largo = "\n".join([m[1][:100] for m in mensajes])
		else:
			inicio = mensajes[:2]
			final = mensajes[-2:]
			resumen_corto = f"Tema: {mensajes[0][1][:60]}..."
			resumen_largo = (
				"Inicio:\n" + "\n".join([f"{m[0]}: {m[1][:100]}..." for m in inicio]) +
				"\n...\n" +
				"Final:\n" + "\n".join([f"{m[0]}: {m[1][:100]}..." for m in final])
			)
		from collections import Counter
		import re
		texto_completo = " ".join([m[1] for m in mensajes])
		palabras = re.findall(r'\b\w{4,}\b', texto_completo.lower())
		stopwords = {'para', 'esto', 'este', 'esta', 'está', 'como', 'cual', 'pero', 'sobre', 'hacer', 'puede', 'desde', 'entre'}
		palabras_filtradas = [p for p in palabras if p not in stopwords]
		palabras_clave = [p for p, _ in Counter(palabras_filtradas).most_common(5)]
		execute_query(
			self.db_path,
			'''INSERT OR REPLACE INTO resumenes (conversacion_id, resumen_corto, resumen_largo, palabras_clave, temas_principales, fecha_generacion) VALUES (?, ?, ?, ?, ?, ?)''',
			[
				conversacion_id,
				resumen_corto,
				resumen_largo,
				json.dumps(palabras_clave),
				json.dumps(["general"]),
				datetime.now().isoformat()
			],
			commit=True
		)
		return {
			"resumen_corto": resumen_corto,
			"resumen_largo": resumen_largo,
			"palabras_clave": palabras_clave
		}

	def estadisticas_generales(self) -> Dict:
		stats = {}
		total_conv = execute_query(
			self.db_path,
			"SELECT COUNT(*) FROM conversaciones",
			[],
			fetchone=True
		)
		stats["total_conversaciones"] = total_conv[0] if total_conv else 0
		rows_estado = execute_query(
			self.db_path,
			"SELECT estado, COUNT(*) FROM conversaciones GROUP BY estado",
			[],
			fetchall=True
		)
		stats["por_estado"] = {row[0]: row[1] for row in rows_estado or []}
		rows_categoria = execute_query(
			self.db_path,
			"SELECT categoria, COUNT(*) FROM conversaciones GROUP BY categoria",
			[],
			fetchall=True
		)
		stats["por_categoria"] = {row[0]: row[1] for row in rows_categoria or []}
		total_msg = execute_query(
			self.db_path,
			"SELECT SUM(num_mensajes) FROM conversaciones",
			[],
			fetchone=True
		)
		stats["total_mensajes"] = total_msg[0] if total_msg and total_msg[0] else 0
		longest = execute_query(
			self.db_path,
			"SELECT titulo, num_mensajes FROM conversaciones ORDER BY num_mensajes DESC LIMIT 1",
			[],
			fetchone=True
		)
		if longest:
			stats["conversacion_mas_larga"] = {
				"titulo": longest[0],
				"mensajes": longest[1]
			}
		return stats

	def detectar_intencion_retomar(self, mensaje: str) -> Dict:
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
		if not palabras_clave:
			return []
		resultados_con_score = []
		rows = execute_query(
			self.db_path,
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

	def crear_conversacion_integradora(self, titulo: str, objetivo: str, conversaciones_base: List[str], categoria: str = "sintesis", descripcion: str = "") -> str:
		from conversation_manager.graph import crear_conversacion_integradora
		return crear_conversacion_integradora(self.db_path, titulo, objetivo, conversaciones_base, categoria, descripcion)

	def vincular_conversaciones(self, conv_origen: str, conv_destino: str, tipo_relacion: str, descripcion: str = "", relevancia: int = 5) -> bool:
		from conversation_manager.graph import vincular_conversaciones
		return vincular_conversaciones(self.db_path, conv_origen, conv_destino, tipo_relacion, descripcion, relevancia)

	def obtener_conversaciones_relacionadas(self, conv_id: str, tipo_relacion: Optional[str] = None, min_relevancia: int = 0) -> Dict[str, List[Dict]]:
		from conversation_manager.graph import obtener_conversaciones_relacionadas
		return obtener_conversaciones_relacionadas(self.db_path, conv_id, tipo_relacion, min_relevancia)

	def actualizar_conclusiones(self, conv_id: str, conclusiones: str, resultados: Optional[str] = None) -> bool:
		from conversation_manager.graph import actualizar_conclusiones
		return actualizar_conclusiones(self.db_path, conv_id, conclusiones, resultados)

	def analizar_convergencias(self, conv_ids: List[str], modo: str = "temas") -> Dict:
		from conversation_manager.graph import analizar_convergencias
		return analizar_convergencias(self.db_path, conv_ids, modo)

	def obtener_grafo_conocimiento(self, profundidad: int = 2, conv_raiz: Optional[str] = None) -> Dict:
		from conversation_manager.graph import obtener_grafo_conocimiento
		return obtener_grafo_conocimiento(self.db_path, profundidad, conv_raiz)
