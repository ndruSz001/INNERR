# benchmark_gguf.py
"""
Benchmark GGUF models (Q4/Q5/Q6) using run_gguf.py on a small prompt set.

- Produce resultados en bench/results.csv y bench/outputs/*.txt
- Auto-detecta modelos Q4/Q5/Q6 en WizardLM
- Ejecuta cada modelo con cada prompt y mide tiempo de ejecución
- Escribe resultados y salidas en archivos

Ejemplo de uso:
$ python bench/benchmark_gguf.py

Requiere:
- Modelos GGUF en models/TheBloke_WizardLM-7B-uncensored-GGUF
- run_gguf.py en el directorio raíz
- prompts.txt en bench/

"""

# ...existing code...
