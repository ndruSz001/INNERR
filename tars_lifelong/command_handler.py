"""
Módulo: command_handler.py
Gestión y ejecución de comandos especiales del asistente.
"""
from typing import Callable, Dict

class CommandHandler:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}

    def register(self, command: str, func: Callable):
        self.commands[command] = func

    def execute(self, command: str, *args, **kwargs):
        if command in self.commands:
            return self.commands[command](*args, **kwargs)
        return None
