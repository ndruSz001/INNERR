import json
from datetime import datetime
from conversation_manager.db import execute_query

def generar_resumen_conversacion(db_path, conversacion_id):
	mensajes = execute_query(
		db_path,
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
		db_path,
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

def estadisticas_generales(db_path):
	stats = {}
	total_conv = execute_query(
		db_path,
		"SELECT COUNT(*) FROM conversaciones",
		[],
		fetchone=True
	)
	stats["total_conversaciones"] = total_conv[0] if total_conv else 0
	rows_estado = execute_query(
		db_path,
		"SELECT estado, COUNT(*) FROM conversaciones GROUP BY estado",
		[],
		fetchall=True
	)
	stats["por_estado"] = {row[0]: row[1] for row in rows_estado or []}
	rows_categoria = execute_query(
		db_path,
		"SELECT categoria, COUNT(*) FROM conversaciones GROUP BY categoria",
		[],
		fetchall=True
	)
	stats["por_categoria"] = {row[0]: row[1] for row in rows_categoria or []}
	total_msg = execute_query(
		db_path,
		"SELECT SUM(num_mensajes) FROM conversaciones",
		[],
		fetchone=True
	)
	stats["total_mensajes"] = total_msg[0] if total_msg and total_msg[0] else 0
	longest = execute_query(
		db_path,
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
