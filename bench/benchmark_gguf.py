#!/usr/bin/env python3
"""
Benchmark GGUF models (Q4/Q5/Q6) using run_gguf.py on a small prompt set.
Produces: bench/results.csv and bench/outputs/*.txt

Este script:
- Detecta modelos GGUF Q4/Q5/Q6 en WizardLM
- Ejecuta cada modelo con cada prompt
- Mide tiempo de ejecución y escribe resultados
- Guarda salidas en archivos bench/outputs/*.txt

Ejemplo de uso:
    $ python bench/benchmark_gguf.py

Requiere:
- Modelos GGUF en models/TheBloke_WizardLM-7B-uncensored-GGUF
- run_gguf.py en el directorio raíz
- prompts.txt en bench/
"""
import subprocess
import time
import csv
from pathlib import Path
import glob

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "run_gguf.py"
PROMPTS = (ROOT / "bench" / "prompts.txt").read_text(encoding="utf-8").strip().splitlines()
OUT_DIR = ROOT / "bench" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# auto-detect models: look for Q4, Q5, Q6 in WizardLM folder
model_folder = ROOT / "models" / "TheBloke_WizardLM-7B-uncensored-GGUF"
models = []
if model_folder.exists():
    for patt in ("*Q4*gguf", "*Q5*gguf", "*Q6*gguf"):
        models.extend(sorted(glob.glob(str(model_folder / patt))))

if not models:
    print("No GGUF models found in", model_folder)
    raise SystemExit(1)

results_csv = ROOT / "bench" / "results.csv"
with open(results_csv, "w", encoding="utf-8", newline="") as csvf:
    writer = csv.writer(csvf)
    writer.writerow(["model", "prompt_id", "prompt", "time_s", "returncode", "out_path"])

for model in models:
    mname = Path(model).name
    print("== Model:", mname)
    for i, prompt in enumerate(PROMPTS, start=1):
        out_path = OUT_DIR / f"{mname}_p{i}.txt"
        cmd = [str(RUN_SCRIPT), "--model", model, "--prompt", prompt, "--n", "64", "--threads", "6", "--out", str(out_path)]
        t0 = time.perf_counter()
        # Run via the venv python to ensure correct env; add timeout to avoid hangs
        try:
            proc = subprocess.run([str(ROOT / ".venv" / "bin" / "python")] + cmd, capture_output=True, text=True, timeout=60)
            t1 = time.perf_counter()
            elapsed = t1 - t0
        except subprocess.TimeoutExpired as e:
            t1 = time.perf_counter()
            elapsed = t1 - t0
            proc = e
        # write combined output
        with open(out_path, "w", encoding="utf-8") as f:
            if hasattr(proc, 'stdout') and proc.stdout:
                f.write(proc.stdout)
            if hasattr(proc, 'stderr') and proc.stderr:
                f.write("\n--- STDERR ---\n")
                f.write(proc.stderr)
            if isinstance(proc, subprocess.TimeoutExpired):
                f.write("\n--- TIMEOUT: process exceeded 60s ---\n")

        with open(results_csv, "a", encoding="utf-8", newline="") as csvf:
            writer = csv.writer(csvf)
            retcode = proc.returncode if hasattr(proc, 'returncode') else -9
            writer.writerow([mname, i, prompt, f"{elapsed:.3f}", retcode, str(out_path)])

print("Benchmark complete. Results:", results_csv)
