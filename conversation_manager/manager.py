
import sqlite3, uuid, json
from datetime import datetime
from typing import List, Dict, Optional
from conversation_manager.db import execute_query, init_database


class ConversationManager:
	def __init__(self, db_path="conversations.db"):
		self.db_path = db_path
		self.current_conversation = None
		init_database(self.db_path)

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

	def nueva_conversacion(self, titulo: str = None, categoria: str = "general", descripcion: str = "", proyecto_relacionado: str = None, tags: List[str] = None, auto_titulo: bool = True) -> str:
		"""
		Crea nueva conversación
		"""
		conv_id = str(uuid.uuid4())[:8]
		if titulo is None:
			if auto_titulo:
				titulo = f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"
			else:
				titulo = "Sin título"
		now = datetime.now().isoformat()
		tags_str = json.dumps(tags) if tags else json.dumps([])
		execute_query(
			self.db_path,
			'''
			INSERT INTO conversaciones 
			(id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, 
			 estado, tags, proyecto_relacionado, metadata)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			''',
			[
				conv_id, titulo, descripcion, categoria, now, now,
				'activa', tags_str, proyecto_relacionado,
				json.dumps({"auto_titulo": auto_titulo})
			],
			commit=True
		)
		self.current_conversation = conv_id
		print(f"\n💬 Nueva conversación iniciada")
		print(f"   ID: {conv_id}")
		print(f"   Categoría: {categoria}")
		if proyecto_relacionado:
			print(f"   Proyecto: {proyecto_relacionado}")
		return conv_id

	def agregar_mensaje(self, conversacion_id: str, tipo: str, contenido: str, metadata: Dict = None):
		"""Agrega mensaje a conversación existente"""
		timestamp = datetime.now().isoformat()
		metadata_str = json.dumps(metadata) if metadata else json.dumps({})
		execute_query(
			self.db_path,
			'''
			INSERT INTO mensajes (conversacion_id, timestamp, tipo, contenido, metadata)
			VALUES (?, ?, ?, ?, ?)
			''',
			[conversacion_id, timestamp, tipo, contenido, metadata_str],
			commit=True
		)
		execute_query(
			self.db_path,
			'''
			UPDATE conversaciones
			SET fecha_ultima_actividad = ?,
				num_mensajes = num_mensajes + 1
			WHERE id = ?
			''',
			[timestamp, conversacion_id],
			commit=True
		)
		self._auto_generar_titulo_si_necesario(conversacion_id)

	def _auto_generar_titulo_si_necesario(self, conversacion_id: str):
		"""Genera título automático basado en primer mensaje si está configurado"""
		result = execute_query(
			self.db_path,
			'''SELECT titulo, num_mensajes, metadata FROM conversaciones WHERE id = ?''',
			[conversacion_id],
			fetchone=True
		)
		if not result:
			return
		titulo, num_mensajes, metadata_str = result
		metadata = json.loads(metadata_str) if metadata_str else {}
		if metadata.get("auto_titulo") and num_mensajes == 1:
			primer_mensaje = execute_query(
				self.db_path,
				'''SELECT contenido FROM mensajes WHERE conversacion_id = ? AND tipo = 'user' ORDER BY timestamp ASC LIMIT 1''',
				[conversacion_id],
				fetchone=True
			)
			if primer_mensaje:
				nuevo_titulo = self._generar_titulo_desde_mensaje(primer_mensaje[0])
				execute_query(
					self.db_path,
					'''UPDATE conversaciones SET titulo = ? WHERE id = ?''',
					[nuevo_titulo, conversacion_id],
					commit=True
				)
				print(f"   📝 Título generado: {nuevo_titulo}")

	def _generar_titulo_desde_mensaje(self, mensaje: str) -> str:
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
		print(f"\n📂 Conversación recuperada: {conv[1]}")
		print(f"   Mensajes previos: {conv[6]}")
		print(f"   Última actividad: {conv[5][:10]}")
		return resultado

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
		print(f"📦 Conversación archivada: {conversacion_id}")

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
		conv_id = str(uuid.uuid4())[:8]
		now = datetime.now().isoformat()
		execute_query(
			self.db_path,
			'''INSERT INTO conversaciones (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, estado, es_integradora, objetivo, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
			[
				conv_id, titulo, descripcion, categoria, now, now,
				'activa', 1, objetivo,
				json.dumps({
					"conversaciones_base": conversaciones_base,
					"tipo_integracion": "sintesis",
					"fecha_integracion": now
				})
			],
			commit=True
		)
		for conv_base in conversaciones_base:
			execute_query(
				self.db_path,
				'''INSERT INTO relaciones_conversaciones (conversacion_origen, conversacion_destino, tipo_relacion, descripcion, fecha_vinculacion, relevancia) VALUES (?, ?, ?, ?, ?, ?)''',
				[
					conv_id, conv_base, 'integra',
					f"Conversación integradora que sintetiza conocimiento de {conv_base}",
					now, 10
				],
				commit=True
			)
		print(f"\n🔗 Conversación integradora creada: {conv_id}")
		print(f"   Integra {len(conversaciones_base)} conversaciones base")
		print(f"   Objetivo: {objetivo}")
		return conv_id

	def vincular_conversaciones(self, conv_origen: str, conv_destino: str, tipo_relacion: str, descripcion: str = "", relevancia: int = 5) -> bool:
		rows = execute_query(
			self.db_path,
			'SELECT id FROM conversaciones WHERE id IN (?, ?)',
			[conv_origen, conv_destino],
			fetchall=True
		)
		if len(rows or []) != 2:
			return False
		now = datetime.now().isoformat()
		execute_query(
			self.db_path,
			'''INSERT INTO relaciones_conversaciones (conversacion_origen, conversacion_destino, tipo_relacion, descripcion, relevancia, fecha_vinculacion) VALUES (?, ?, ?, ?, ?, ?)''',
			[conv_origen, conv_destino, tipo_relacion, descripcion, relevancia, now],
			commit=True
		)
		print(f"✅ Vinculadas: {conv_origen} → {conv_destino} ({tipo_relacion})")
		return True

	def obtener_conversaciones_relacionadas(self, conv_id: str, tipo_relacion: Optional[str] = None, min_relevancia: int = 0) -> Dict[str, List[Dict]]:
		query_salientes = '''SELECT r.conversacion_destino, r.tipo_relacion, r.descripcion, r.relevancia, r.fecha_vinculacion, c.titulo, c.categoria FROM relaciones_conversaciones r JOIN conversaciones c ON r.conversacion_destino = c.id WHERE r.conversacion_origen = ?'''
		params_salientes = [conv_id]
		if tipo_relacion:
			query_salientes += ' AND r.tipo_relacion = ?'
			params_salientes.append(tipo_relacion)
		if min_relevancia > 0:
			query_salientes += ' AND r.relevancia >= ?'
			params_salientes.append(min_relevancia)
		rows_salientes = execute_query(
			self.db_path,
			query_salientes,
			params_salientes,
			fetchall=True
		)
		salientes = []
		for row in rows_salientes or []:
			salientes.append({
				'id': row[0],
				'tipo_relacion': row[1],
				'descripcion': row[2],
				'relevancia': row[3],
				'fecha_vinculacion': row[4],
				'titulo': row[5],
				'categoria': row[6]
			})
		query_entrantes = '''SELECT r.conversacion_origen, r.tipo_relacion, r.descripcion, r.relevancia, r.fecha_vinculacion, c.titulo, c.categoria FROM relaciones_conversaciones r JOIN conversaciones c ON r.conversacion_origen = c.id WHERE r.conversacion_destino = ?'''
		params_entrantes = [conv_id]
		if tipo_relacion:
			query_entrantes += ' AND r.tipo_relacion = ?'
			params_entrantes.append(tipo_relacion)
		if min_relevancia > 0:
			query_entrantes += ' AND r.relevancia >= ?'
			params_entrantes.append(min_relevancia)
		rows_entrantes = execute_query(
			self.db_path,
			query_entrantes,
			params_entrantes,
			fetchall=True
		)
		entrantes = []
		for row in rows_entrantes or []:
			entrantes.append({
				'id': row[0],
				'tipo_relacion': row[1],
				'descripcion': row[2],
				'relevancia': row[3],
				'fecha_vinculacion': row[4],
				'titulo': row[5],
				'categoria': row[6]
			})
		return {
			'salientes': salientes,
			'entrantes': entrantes,
			'total': len(salientes) + len(entrantes)
		}

	def actualizar_conclusiones(self, conv_id: str, conclusiones: str, resultados: Optional[str] = None) -> bool:
		affected = execute_query(
			self.db_path,
			'''UPDATE conversaciones SET conclusiones = ?, resultados = ? WHERE id = ?''',
			[conclusiones, resultados, conv_id],
			commit=True,
			rowcount=True
		)
		if affected > 0:
			print(f"✅ Conclusiones actualizadas para {conv_id}")
			return True
		return False

	def analizar_convergencias(self, conv_ids: List[str], modo: str = "temas") -> Dict:
		placeholders = ','.join(['?'] * len(conv_ids))
		query = f'''SELECT c.id, c.titulo, c.categoria, c.tags, c.conclusiones, r.palabras_clave, r.temas_principales FROM conversaciones c LEFT JOIN resumenes r ON c.id = r.conversacion_id WHERE c.id IN ({placeholders})'''
		conversaciones = execute_query(
			self.db_path,
			query,
			conv_ids,
			fetchall=True
		)
		if len(conversaciones or []) < 2:
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
		todas_palabras = []
		todas_categorias = []
		for conv in conversaciones:
			conv_id, titulo, categoria, tags_json, conclusiones, palabras_clave, temas = conv
			analisis['conversaciones'].append({
				'id': conv_id,
				'titulo': titulo,
				'categoria': categoria
			})
			todas_categorias.append(categoria)
			if palabras_clave:
				palabras = palabras_clave.split(',')
				todas_palabras.extend([p.strip().lower() for p in palabras])
			if tags_json:
				tags = json.loads(tags_json)
				todas_palabras.extend([t.lower() for t in tags])
		from collections import Counter
		palabra_freq = Counter(todas_palabras)
		categoria_freq = Counter(todas_categorias)
		for palabra, freq in palabra_freq.most_common():
			if freq > 1:
				analisis['temas_comunes'].append({
					'palabra': palabra,
					'frecuencia': freq,
					'porcentaje': (freq / len(conversaciones)) * 100
				})
		analisis['categorias'] = dict(categoria_freq)
		if len(set(todas_categorias)) == 1:
			analisis['convergencias'].append({
				'tipo': 'categoria_unica',
				'valor': todas_categorias[0],
				'descripcion': 'Todas las conversaciones pertenecen a la misma categoría'
			})
		if len(set(todas_categorias)) == len(conversaciones):
			analisis['divergencias'].append({
				'tipo': 'categorias_diversas',
				'descripcion': 'Cada conversación tiene categoría diferente'
			})
		return analisis

	def obtener_grafo_conocimiento(self, profundidad: int = 2, conv_raiz: Optional[str] = None) -> Dict:
		grafo = {
			'nodos': {},
			'aristas': [],
			'estadisticas': {}
		}
		if conv_raiz:
			nodos_visitados = set([conv_raiz])
			nodos_pendientes = [conv_raiz]
			nivel_actual = 0
			while nodos_pendientes and nivel_actual < profundidad:
				nodo_actual = nodos_pendientes.pop(0)
				row = execute_query(
					self.db_path,
					'''SELECT titulo, categoria, es_integradora, objetivo, num_mensajes FROM conversaciones WHERE id = ?''',
					[nodo_actual],
					fetchone=True
				)
				if row:
					grafo['nodos'][nodo_actual] = {
						'titulo': row[0],
						'categoria': row[1],
						'es_integradora': bool(row[2]),
						'objetivo': row[3],
						'num_mensajes': row[4],
						'nivel': nivel_actual
					}
				rels = execute_query(
					self.db_path,
					'''SELECT conversacion_destino, tipo_relacion, relevancia FROM relaciones_conversaciones WHERE conversacion_origen = ?''',
					[nodo_actual],
					fetchall=True
				)
				for rel in rels or []:
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
			rows = execute_query(
				self.db_path,
				'''SELECT id, titulo, categoria, es_integradora, objetivo, num_mensajes FROM conversaciones WHERE estado = 'activa' ''',
				[],
				fetchall=True
			)
			for row in rows or []:
				conv_id, titulo, cat, es_int, obj, num_msg = row
				grafo['nodos'][conv_id] = {
					'titulo': titulo,
					'categoria': cat,
					'es_integradora': bool(es_int),
					'objetivo': obj,
					'num_mensajes': num_msg
				}
			rels = execute_query(
				self.db_path,
				'''SELECT conversacion_origen, conversacion_destino, tipo_relacion, relevancia FROM relaciones_conversaciones''',
				[],
				fetchall=True
			)
			for row in rels or []:
				grafo['aristas'].append({
					'origen': row[0],
					'destino': row[1],
					'tipo': row[2],
					'relevancia': row[3]
				})
		grafo['estadisticas'] = {
			'num_nodos': len(grafo['nodos']),
			'num_aristas': len(grafo['aristas']),
			'nodos_integradores': sum(1 for n in grafo['nodos'].values() if n['es_integradora']),
			'nodos_independientes': sum(1 for nid in grafo['nodos'].keys() if not any(a['origen'] == nid or a['destino'] == nid for a in grafo['aristas']))
		}
		return grafo
