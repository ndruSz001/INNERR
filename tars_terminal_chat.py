import os
from core_ia import TarsVision

def main():
    tars = TarsVision()
    print("\nBienvenido a TARS (Terminal IA Personal)")
    print("Escribe 'salir' para terminar la sesión.\n")
    historial = []
    utilidad_log = "utilidad_respuestas_tars.txt"
    utiles_actuales = []  # Lista de comentarios útiles de la conversación actual
    modo_investigacion = False
    carpeta_guardado = None
    
    print("¿Quieres activar el modo investigación? (s/n): ", end="")
    resp_modo = input().strip().lower()
    
    if resp_modo == "s":
        modo_investigacion = True
        print("[MODO INVESTIGACIÓN ACTIVADO]")
        # Preguntar agente/carpeta/subtema
        agente = input("¿Con qué agente/tema quieres trabajar? (ejemplo: BIOMED_DB): ").strip().replace(" ", "_").upper()
        base_path = f"tars_lifelong/biomed_db/{agente}"
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        subcarpeta = input("¿Quieres guardar en una subcarpeta/proyecto? (deja vacío para carpeta principal): ").strip().replace(" ", "_")
        
        if subcarpeta:
            carpeta_guardado = os.path.join(base_path, subcarpeta)
            if not os.path.exists(carpeta_guardado):
                os.makedirs(carpeta_guardado)
        else:
            carpeta_guardado = base_path
        
        print(f"Las conversaciones de esta sesión se guardarán en: {carpeta_guardado}")
    
    while True:
        user_input = input("Tú: ")
        comando = user_input.strip().lower()
        
        # Detectar comandos especiales para guardar/cambiar tema/nueva conversación
        guardar_trigger = any(
            frase in comando for frase in [
                "guarda esto", "guardar esto", "cambiar de tema", "nueva conversación", 
                "nuevo tema", "save this", "change topic", "new conversation"]
        )
        
        salir_trigger = comando in ["salir", "terminar", "adios", "adiós"]
        marcar_util_trigger = comando in ["útil", "util", "no útil", "no util", "marcar útil", "marcar no útil"]

        if salir_trigger:
            if historial:
                _preguntar_guardar(historial, utiles_actuales, carpeta_guardado)
            print("TARS: Hasta luego.")
            break

        if marcar_util_trigger and historial:
            ultima = historial[-1]
            utilidad = "útil" if "no" not in comando else "no útil"
            if utilidad == "útil":
                utiles_actuales.append(ultima)
            with open(utilidad_log, "a", encoding="utf-8") as f:
                f.write(f"Tú: {ultima['usuario']}\nTARS: {ultima['tars']}\n>> Marcado como: {utilidad}\n\n")
            print(f"[Registro] Respuesta marcada como {utilidad}.\n")
            continue

        response = tars.generar_respuesta_texto(user_input, user_id="Ndrz")
        print(f"TARS: {response}\n")
        historial.append({"usuario": user_input, "tars": response})

        if guardar_trigger:
            _preguntar_guardar(historial, utiles_actuales, carpeta_guardado)
            historial = []
            utiles_actuales = []


def _preguntar_guardar(historial, utiles_actuales, carpeta_guardado=None):
    """Pregunta al usuario si desea guardar la conversación"""
    import datetime
    
    while True:
        guardar = input("¿Deseas guardar esta conversación/tema? (s/n): ").strip().lower()
        
        if guardar == "s":
            hoy = datetime.datetime.now().strftime("%Y-%m-%d")
            sugerencia = f"conversacion_{hoy}.txt"
            print(f"¿Cómo quieres nombrar el archivo de esta conversación? (sugerencia: {sugerencia})")
            ruta = input("Nombre de archivo: ").strip()
            
            if not ruta:
                ruta = sugerencia
            
            # Determinar ruta final basada en carpeta_guardado
            if carpeta_guardado:
                ruta_final = os.path.join(carpeta_guardado, ruta)
                os.makedirs(carpeta_guardado, exist_ok=True)
            else:
                ruta_final = ruta
            
            print(f"Se guardará como: {ruta_final}")
            
            # Guardar el archivo
            with open(ruta_final, "a", encoding="utf-8") as f:
                if utiles_actuales:
                    f.write("=== Comentarios Útiles de este tema ===\n")
                    for turno in utiles_actuales:
                        f.write(f"Tú: {turno['usuario']}\nTARS: {turno['tars']}\n\n")
                    f.write("=== Fin de comentarios útiles ===\n\n")
                
                f.write("=== Conversación completa ===\n")
                for turno in historial:
                    f.write(f"Tú: {turno['usuario']}\nTARS: {turno['tars']}\n\n")
                f.write("=== Fin de conversación ===\n\n")
            
            print(f"✅ Conversación guardada como '{ruta_final}'. Puedes revisar este archivo cuando quieras.\n")
            break
        
        elif guardar == "n":
            break
        
        else:
            print("Por favor responde 's' o 'n'.")


if __name__ == "__main__":
    main()
