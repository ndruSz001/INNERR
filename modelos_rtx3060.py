# Modelos Optimizados para RTX 3060 (12GB VRAM)
# Configuración preparada para cuando tengas la Dell dedicada

# Modelos de Visión - Más grandes y mejores
VISION_MODELS = {
    "llava_13b": "llava-hf/llava-1.5-13b-hf",  # 13B parámetros - Superior calidad
    "llava_7b": "llava-hf/llava-1.5-7b-hf",    # Fallback si 13B no cabe
}

# Modelos de Conversación - Más inteligentes
TEXT_MODELS = {
    "mistral_7b": "mistralai/Mistral-7B-Instruct-v0.1",  # Mejor que Phi-2
    "zephyr_7b": "HuggingFaceH4/zephyr-7b-beta",         # Alternativa optimizada
    "phi_2": "microsoft/phi-2",                         # Fallback actual
}

# Configuración de Quantization para RTX 3060
QUANTIZATION_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_compute_dtype": "torch.float16",
    "bnb_4bit_use_double_quant": True,
    "bnb_4bit_quant_type": "nf4",
    "device_map": "auto",
    "low_cpu_mem_usage": True,
}

# Configuración de Generación Optimizada
GENERATION_CONFIG = {
    "max_new_tokens": 300,      # Más tokens que actual
    "temperature": 0.8,         # Más creativo
    "top_p": 0.9,
    "repetition_penalty": 1.1,  # Evitar repeticiones
    "do_sample": True,
}

# Configuración de Memoria para RTX 3060
MEMORY_CONFIG = {
    "max_memory": {0: "12GB", "cpu": "32GB"},
    "offload_folder": "/tmp/tars_offload",
    "torch_dtype": "torch.float16",
}