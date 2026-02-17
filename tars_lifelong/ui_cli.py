"""
Módulo: ui_cli.py
Interfaz de usuario para entrada/salida en terminal (CLI).
"""
from typing import Optional

class TerminalUI:
    def prompt(self, message: str = "> ") -> str:
        return input(message)

    def print(self, message: str = ""):
        print(message)

    def print_warning(self, message: str):
        print(f"⚠️  {message}")

    def print_success(self, message: str):
        print(f"✅ {message}")

    def print_error(self, message: str):
        print(f"❌ {message}")
