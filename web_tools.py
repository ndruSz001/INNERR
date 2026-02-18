# web_tools.py
"""
Herramientas para extracción y análisis de información web y videos online.
Modularizado para fácil integración y buenas prácticas.
"""

import requests
from bs4 import BeautifulSoup
from pytube import YouTube

class WebScraper:
    @staticmethod
    def fetch_text(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()

class VideoDownloader:
    @staticmethod
    def download_youtube(url, output_path):
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream.download(output_path)
        return f"Video descargado en: {output_path}"

if __name__ == "__main__":
    # Ejemplo de uso
    texto = WebScraper.fetch_text('https://es.wikipedia.org/wiki/Inteligencia_artificial')
    print(texto[:500])  # Muestra primeros 500 caracteres
    VideoDownloader.download_youtube('https://www.youtube.com/watch?v=dQw4w9WgXcQ', './')
