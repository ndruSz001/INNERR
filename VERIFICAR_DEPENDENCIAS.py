#!/usr/bin/env python3
"""
Verificar que todas las dependencias requeridas están disponibles
"""

def check_dependency(package, import_name=None):
    """Verifica si un paquete está instalado"""
    import_name = import_name or package
    try:
        __import__(import_name)
        print(f"✅ {package:30} OK")
        return True
    except ImportError:
        print(f"❌ {package:30} MISSING - install: pip install {package}")
        return False

print("=" * 70)
print("VERIFICACIÓN DE DEPENDENCIAS - TARS DISTRIBUIDO")
print("=" * 70)

# Dependencias básicas
print("\n📦 DEPENDENCIAS BÁSICAS:")
dependencies = [
    ("torch", "torch"),
    ("transformers", "transformers"),
    ("numpy", "numpy"),
    ("Pillow", "PIL"),
    ("pydantic", "pydantic"),
]

for pkg, imp in dependencies:
    check_dependency(pkg, imp)

# Dependencias de inference
print("\n🧠 DEPENDENCIAS DE INFERENCIA:")
inference_deps = [
    ("llama-cpp-python", "llama_cpp"),
    ("ollama", "ollama"),
]

for pkg, imp in inference_deps:
    check_dependency(pkg, imp)

# Dependencias de processing
print("\n📄 DEPENDENCIAS DE PROCESAMIENTO:")
processing_deps = [
    ("pdfplumber", "pdfplumber"),
    ("pytesseract", "pytesseract"),
    ("opencv-python", "cv2"),
    ("sentence-transformers", "sentence_transformers"),
]

for pkg, imp in processing_deps:
    check_dependency(pkg, imp)

# Dependencias de vector DB
print("\n🔍 DEPENDENCIAS DE VECTOR DB:")
vector_deps = [
    ("faiss-cpu", "faiss"),
    ("pinecone-client", "pinecone"),
    ("weaviate-client", "weaviate"),
]

for pkg, imp in vector_deps:
    missing = [check_dependency(pkg, imp) for pkg in []]
    for pkg, imp in vector_deps:
        check_dependency(pkg, imp)

# Dependencias opcionales
print("\n🔌 DEPENDENCIAS OPCIONALES (para características avanzadas):")
optional_deps = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("redis", "redis"),
    ("psycopg2-binary", "psycopg2"),
]

for pkg, imp in optional_deps:
    check_dependency(pkg, imp)

print("\n" + "=" * 70)
print("✅ Verificación completada")
print("=" * 70)
