#!/usr/bin/env python3
"""Generate a synthetic JSONL dataset for fine-tuning/evaluation.
Produces: data/train_500.jsonl by default.
"""
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "train_500.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)

templates = [
    ("Resume en 20 palabras: {topic}", "Resumen breve sobre {topic}.") ,
    ("Explica como funciona: {topic}", "Explicación sencilla de {topic}.") ,
    ("Da 3 recomendaciones para: {topic}", "Tres recomendaciones para {topic}.") ,
    ("Escribe un email solicitando: {topic}", "Email corto solicitando {topic}.") ,
    ("Traduce al inglés: '{text}'", "{text} (translated)") ,
]

topics = [
    "usar IA en medicina",
    "un motor eléctrico",
    "mejorar la batería de un portátil",
    "pedir reunión de trabajo",
    "la novela Cien años de soledad",
    "precisión vs recall",
    "receta de tortilla de patatas",
    "exoesqueleto médico",
    "agradecimiento formal",
    "rehabilitación física",
]

def make_example(i):
    t = random.choice(templates)
    if '{topic}' in t[0]:
        topic = random.choice(topics)
        prompt = t[0].format(topic=topic)
        completion = t[1].format(topic=topic)
    else:
        text = random.choice(["Gracias por tu ayuda, hablamos pronto.", "¿Puedes resumir esto?", "Necesito instrucciones."])
        prompt = t[0].format(text=text)
        completion = t[1].format(text=text)
    return {"prompt": prompt, "completion": completion}

def main(n=500):
    with open(OUT, 'w', encoding='utf-8') as f:
        for i in range(n):
            ex = make_example(i)
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {n} examples to {OUT}")

if __name__ == '__main__':
    main(500)
