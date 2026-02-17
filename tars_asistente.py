import re
from core.logging_config import get_logger
from tars_lifelong.conversation_manager import ConversationManager
from tars_lifelong.command_handler import CommandHandler
from tars_lifelong.ui_cli import TerminalUI
try:
    from processing.document_processor import DocumentProcessor
except ImportError:
    DocumentProcessor = None
try:
    import requests
except ImportError:
    requests = None
import sys
import os
from pathlib import Path
from datetime import datetime

class TarsAsistenteInteligente:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.manager = ConversationManager()
        self.commands = CommandHandler()
        self.ui = TerminalUI()
        # Inicializar DocumentProcessor si está disponible
        self.doc_processor = DocumentProcessor() if DocumentProcessor else None
        self._register_default_commands()

    def _register_default_commands(self):
        self.commands.register('/salir', self.cmd_salir)
        self.commands.register('/ayuda', self.cmd_ayuda)
        self.commands.register('/procesar_pdf', self.cmd_procesar_pdf)
        self.commands.register('/buscar_pdf', self.cmd_buscar_pdf)
        # Puedes registrar más comandos aquí
    def cmd_procesar_pdf(self):
        if not self.doc_processor:
            self.ui.print_error("Procesador de documentos no disponible.")
            return
        pdf_path = self.ui.prompt("Ruta al PDF a procesar: ")
        if not pdf_path:
            self.ui.print_warning("No se proporcionó ruta.")
            return
        self.ui.print(f"Procesando PDF: {pdf_path} ...")
        resultado = self.doc_processor.procesar_pdf(pdf_path)
        if "error" in resultado:
            self.ui.print_error(f"Error: {resultado['error']}")
        else:
            self.ui.print_success(f"PDF procesado: {resultado['nombre_archivo']} ({resultado['estadisticas']['total_palabras']} palabras, {resultado['estadisticas']['total_imagenes']} imágenes)")

    def cmd_buscar_pdf(self):
        if not self.doc_processor:
            self.ui.print_error("Procesador de documentos no disponible.")
            return
        query = self.ui.prompt("Texto a buscar en PDFs: ")
        if not query:
            self.ui.print_warning("No se proporcionó texto de búsqueda.")
            return
        resultados = self.doc_processor.buscar_en_documentos(query)
        if not resultados:
            self.ui.print("No se encontraron coincidencias en los documentos procesados.")
        else:
            self.ui.print(f"Resultados encontrados: {len(resultados)}")
            for r in resultados[:5]:
                self.ui.print(f"Documento: {r['documento']}\n...{r['contexto']}...\n---")

    def detectar_intencion_nueva_conversacion(self, mensaje: str) -> bool:
        mensaje_lower = mensaje.lower()
        palabras_clave = [
            'conversación nueva', 'conversacion nueva',
            'nueva conversación', 'nueva conversacion',
            'cambiar de tema', 'cambiemos de tema',
            'cambiar tema', 'cambiemos tema',
            'hablemos de otra cosa', 'hablemos de otro tema',
            'tema nuevo', 'nuevo tema',
            'empezar de nuevo', 'empezar algo nuevo',
            'iniciar conversación', 'iniciar conversacion',
            'empecemos con', 'empecemos algo',
            'quiero hablar de algo diferente',
            'algo completamente diferente'
        ]
        return any(palabra in mensaje_lower for palabra in palabras_clave)

    def chat_loop(self):
        self.ui.print("Bienvenido a TARS Asistente Inteligente.")
        while True:
            try:
                mensaje = self.ui.prompt()
                if not mensaje:
                    continue
                if mensaje.startswith('/'):
                    result = self.commands.execute(mensaje)
                    if result == 'exit':
                        break
                    continue
                if self.detectar_intencion_nueva_conversacion(mensaje):
                    self.ui.print("\n🔄 Detectado: Quieres cambiar de tema o iniciar conversación nueva\n")
                    self._mostrar_opciones_nueva_conversacion()
                    continue
                # Procesamiento automático de PDFs si el usuario menciona un PDF
                if self.doc_processor and ('.pdf' in mensaje.lower() or 'analiza pdf' in mensaje.lower()):
                    pdf_path = re.search(r'(\S+\.pdf)', mensaje, re.IGNORECASE)
                    if pdf_path:
                        resultado = self.doc_processor.procesar_pdf(pdf_path.group(1))
                        if "error" in resultado:
                            self.ui.print_error(f"Error al procesar PDF: {resultado['error']}")
                        else:
                            self.ui.print_success(f"PDF procesado: {resultado['nombre_archivo']} ({resultado['estadisticas']['total_palabras']} palabras)")
                        continue
                # Lógica de conversación
                self.manager.add_message(mensaje, sender="user")
                self.ui.print(f"TARS: (respuesta simulada) Procesando: {mensaje}")
            except KeyboardInterrupt:
                self.ui.print("\n\n💾 Guardando...\n👋 ¡Hasta pronto!")
                break
            except Exception as e:
                self.ui.print_error(f"Error: {e}")

    def _mostrar_opciones_nueva_conversacion(self):
        self.ui.print("¿Qué quieres hacer?\n")
        self.ui.print("1. 💬 Crear nueva conversación")
        self.ui.print("2. 📚 Ver conversaciones guardadas")
        self.ui.print("3. 🔍 Buscar conversación específica")
        self.ui.print("4. ↩️  Continuar con conversación actual")
        opcion = self.ui.prompt("Selecciona (1-4): ")
        if opcion == '1':
            topic = self.ui.prompt("Tema de la conversación: ")
            self.manager.start_new_conversation(topic=topic)
            self.ui.print_success("Nueva conversación iniciada.")
        elif opcion == '2':
            for conv in self.manager.list_conversations():
                self.ui.print(f"[{conv['id']}] {conv['topic']} ({conv['category']})")
        elif opcion == '3':
            palabra = self.ui.prompt("Palabra clave a buscar: ")
            encontrados = [c for c in self.manager.list_conversations() if palabra in c['topic']]
            for conv in encontrados:
                self.ui.print(f"[{conv['id']}] {conv['topic']} ({conv['category']})")
        elif opcion == '4':
            self.ui.print("Continuando conversación actual...")
        else:
            self.ui.print_warning("Opción inválida, continuando conversación actual")

    def cmd_salir(self):
        self.ui.print("\n💾 Guardando conversación...\n👋 ¡Hasta pronto!")
        return 'exit'

    def cmd_ayuda(self):
        self.ui.print("\n=== AYUDA TARS ===")
        self.ui.print("/salir - Guardar y salir")
        self.ui.print("/ayuda - Mostrar esta ayuda")
        self.ui.print("Puedes escribir mensajes o comandos en cualquier momento.")

# --- MAIN ---
def main():
    asistente = TarsAsistenteInteligente()
    asistente.chat_loop()

if __name__ == "__main__":
    main()
