"""
Prueba de inferencia distribuida local (PC1 + PC2 en la misma máquina)
"""
import requests
import time

# Esperar a que ambos servidores estén listos
def wait_for_server(url, timeout=30):
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

if __name__ == "__main__":
    pc1_url = "http://127.0.0.1:8000/health"
    pc2_url = "http://127.0.0.1:8001/health"
    print("Esperando a que PC1 esté listo...")
    assert wait_for_server(pc1_url), "PC1 no responde en /health"
    print("Esperando a que PC2 esté listo...")
    assert wait_for_server(pc2_url), "PC2 no responde en /health"

    # Prueba de inferencia distribuida: enviar un prompt a PC2, que debe reenviar a PC1 si corresponde
    print("Enviando inferencia a PC2 (debería reenviar a PC1 si es necesario)...")
    payload = {
        "prompt": "¿Cuál es la capital de Francia?",
        "max_tokens": 32,
        "temperature": 0.7,
        "gpu_index": 0
    }
    r = requests.post("http://127.0.0.1:8001/inference", json=payload)
    print("Respuesta de PC2:", r.json())

    print("Enviando inferencia a PC1 directamente...")
    r2 = requests.post("http://127.0.0.1:8000/inference", json=payload)
    print("Respuesta de PC1:", r2.json())
