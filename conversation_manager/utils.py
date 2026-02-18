# utils.py
"""
Funciones utilitarias para gestión de conversaciones en TARS.

Ejemplo de uso:
	# from conversation_manager.utils import <funcion>
	# resultado = <funcion>(...)
	# print(resultado)
"""
"""
utils.py
Funciones auxiliares y helpers para ConversationManager.
"""
# Aquí se migrarán funciones utilitarias y validaciones
import json
from conversation_manager.db import execute_query

def auto_generar_titulo_si_necesario(db_path, conversacion_id):
	result = execute_query(
		db_path,
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
			db_path,
			'''SELECT contenido FROM mensajes WHERE conversacion_id = ? AND tipo = 'user' ORDER BY timestamp ASC LIMIT 1''',
			[conversacion_id],
			fetchone=True
		)
		if primer_mensaje:
			nuevo_titulo = generar_titulo_desde_mensaje(primer_mensaje[0])
			execute_query(
				db_path,
				'''UPDATE conversaciones SET titulo = ? WHERE id = ?''',
				[nuevo_titulo, conversacion_id],
				commit=True
			)
			print(f"   📝 Título generado: {nuevo_titulo}")

def generar_titulo_desde_mensaje(mensaje):
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
