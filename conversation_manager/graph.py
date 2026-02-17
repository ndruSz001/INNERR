"""
graph.py
Gestión de relaciones y grafo de conocimiento entre conversaciones.
"""
# Aquí se migrará la lógica de relaciones y grafo
import json
import uuid
from datetime import datetime
from conversation_manager.db import execute_query

def crear_conversacion_integradora(db_path, titulo, objetivo, conversaciones_base, categoria="sintesis", descripcion=""):
	conv_id = str(uuid.uuid4())[:8]
	now = datetime.now().isoformat()
	execute_query(
		db_path,
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
			db_path,
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

def vincular_conversaciones(db_path, conv_origen, conv_destino, tipo_relacion, descripcion="", relevancia=5):
	rows = execute_query(
		db_path,
		'SELECT id FROM conversaciones WHERE id IN (?, ?)',
		[conv_origen, conv_destino],
		fetchall=True
	)
	if len(rows or []) != 2:
		return False
	now = datetime.now().isoformat()
	execute_query(
		db_path,
		'''INSERT INTO relaciones_conversaciones (conversacion_origen, conversacion_destino, tipo_relacion, descripcion, relevancia, fecha_vinculacion) VALUES (?, ?, ?, ?, ?, ?)''',
		[conv_origen, conv_destino, tipo_relacion, descripcion, relevancia, now],
		commit=True
	)
	print(f"✅ Vinculadas: {conv_origen} → {conv_destino} ({tipo_relacion})")
	return True

def obtener_conversaciones_relacionadas(db_path, conv_id, tipo_relacion=None, min_relevancia=0):
	query_salientes = '''SELECT r.conversacion_destino, r.tipo_relacion, r.descripcion, r.relevancia, r.fecha_vinculacion, c.titulo, c.categoria FROM relaciones_conversaciones r JOIN conversaciones c ON r.conversacion_destino = c.id WHERE r.conversacion_origen = ?'''
	params_salientes = [conv_id]
	if tipo_relacion:
		query_salientes += ' AND r.tipo_relacion = ?'
		params_salientes.append(tipo_relacion)
	if min_relevancia > 0:
		query_salientes += ' AND r.relevancia >= ?'
		params_salientes.append(min_relevancia)
	rows_salientes = execute_query(
		db_path,
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
		db_path,
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

def actualizar_conclusiones(db_path, conv_id, conclusiones, resultados=None):
	affected = execute_query(
		db_path,
		'''UPDATE conversaciones SET conclusiones = ?, resultados = ? WHERE id = ?''',
		[conclusiones, resultados, conv_id],
		commit=True,
		rowcount=True
	)
	if affected > 0:
		print(f"✅ Conclusiones actualizadas para {conv_id}")
		return True
	return False

def analizar_convergencias(db_path, conv_ids, modo="temas"):
	placeholders = ','.join(['?'] * len(conv_ids))
	query = f'''SELECT c.id, c.titulo, c.categoria, c.tags, c.conclusiones, r.palabras_clave, r.temas_principales FROM conversaciones c LEFT JOIN resumenes r ON c.id = r.conversacion_id WHERE c.id IN ({placeholders})'''
	conversaciones = execute_query(
		db_path,
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

def obtener_grafo_conocimiento(db_path, profundidad=2, conv_raiz=None):
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
				db_path,
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
				db_path,
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
			db_path,
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
			db_path,
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
