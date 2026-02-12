#!/usr/bin/env bash
set -eu
# Simple shell benchmark that calls llama-cli directly with timeout to avoid interactive hangs
ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
MODEL_DIR="$ROOT/models/TheBloke_WizardLM-7B-uncensored-GGUF"
PROMPTS_FILE="$ROOT/bench/prompts.txt"
OUT_DIR="$ROOT/bench/outputs_shell"
mkdir -p "$OUT_DIR"
RESULTS_CSV="$ROOT/bench/results_shell.csv"
echo "model,prompt_id,prompt,time_s,retcode,out_path" > "$RESULTS_CSV"

for model in "$MODEL_DIR"/*Q4*gguf "$MODEL_DIR"/*Q5*gguf "$MODEL_DIR"/*Q6*gguf; do
  [ -f "$model" ] || continue
  mname=$(basename "$model")
  i=0
  while IFS= read -r prompt || [ -n "$prompt" ]; do
    i=$((i+1))
    outpath="$OUT_DIR/${mname}_p${i}.txt"
    start=$(date +%s.%N)
    timeout 60s "$ROOT/llama.cpp/build/bin/llama-cli" -m "$model" -p "$prompt" -n 64 -t 6 --single-turn --no-show-timings > "$outpath" 2>&1 || rc=$?
    rc=${rc:-0}
    end=$(date +%s.%N)
    elapsed=$(printf "%.3f" "$(echo "$end - $start" | bc -l)")
    echo "${mname},${i},"""${prompt//"/"'"'"}'""",${elapsed},${rc},${outpath}" >> "$RESULTS_CSV"
    unset rc
  done < "$PROMPTS_FILE"
done

echo "Shell benchmark finished: $RESULTS_CSV"
