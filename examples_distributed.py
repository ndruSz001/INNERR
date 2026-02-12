#!/usr/bin/env python3
"""
Example: Using the Distributed System
Ejemplos de cómo usar el sistema distribuido PC1 + PC2
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any

# ============================================================================
# EXAMPLE 1: Health Checks y Status
# ============================================================================

async def example_health_checks(pc1_host: str = "localhost"):
    """
    Verificar que ambas PCs están online y respondiendo
    """
    print("\n" + "="*70)
    print("📊 EXAMPLE 1: Health Checks")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        # PC1 Health
        print("\n1️⃣  PC1 Health Check:")
        async with session.get(f"http://{pc1_host}:8000/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📍 PC: {data['pc_name']}")
                print(f"   💾 Total VRAM: {data['total_vram_gb']:.1f}GB")
                print(f"   🎮 GPUs: {data['gpu_count']}")
            else:
                print(f"   ❌ Failed with status {resp.status}")
        
        # PC2 Health
        print("\n2️⃣  PC2 Health Check:")
        async with session.get(f"http://{pc1_host}:8001/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📍 PC: {data['pc_name']}")
                print(f"   💾 Total VRAM: {data['total_vram_gb']:.1f}GB")
                print(f"   🎮 GPUs: {data['gpu_count']}")
            else:
                print(f"   ❌ Failed with status {resp.status}")


# ============================================================================
# EXAMPLE 2: Ver Modelos Disponibles
# ============================================================================

async def example_get_models(pc1_host: str = "localhost"):
    """
    Ver qué modelos están disponibles en cada PC
    """
    print("\n" + "="*70)
    print("📦 EXAMPLE 2: Available Models")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        # PC1 Models
        print("\n🖥️  PC1 (RTX 3060) - Models:")
        async with session.get(f"http://{pc1_host}:8000/models") as resp:
            if resp.status == 200:
                data = await resp.json()
                models = data.get("models", {})
                for gpu_key, model_list in models.items():
                    print(f"  {gpu_key}:")
                    for model in model_list:
                        print(f"    - {model}")
        
        # PC2 Models
        print("\n🖥️  PC2 (GTX 1660 Super) - Models:")
        async with session.get(f"http://{pc1_host}:8001/models") as resp:
            if resp.status == 200:
                data = await resp.json()
                models = data.get("models", {})
                for gpu_key, model_list in models.items():
                    print(f"  {gpu_key}:")
                    for model in model_list:
                        print(f"    - {model}")


# ============================================================================
# EXAMPLE 3: Inference en PC1
# ============================================================================

async def example_inference_pc1(pc1_host: str = "localhost", 
                               prompt: str = "¿Cuál es la capital de España?"):
    """
    Hacer inference usando PC1 (modelos grandes)
    """
    print("\n" + "="*70)
    print("🧠 EXAMPLE 3: Inference on PC1 (Large Models)")
    print("="*70)
    
    request_body = {
        "prompt": prompt,
        "max_tokens": 256,
        "temperature": 0.7,
        "gpu_index": 0
    }
    
    print(f"\nSending inference request to PC1...")
    print(f"  Prompt: {prompt}")
    print(f"  Max tokens: {request_body['max_tokens']}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{pc1_host}:8000/inference",
            json=request_body
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"\n✅ Response from PC1:")
                print(f"  Generated: {data.get('response', 'N/A')}")
                print(f"  Tokens: {data.get('tokens_generated', 'N/A')}")
                print(f"  GPU Used: {data.get('gpu_used', 'N/A')}")
            else:
                print(f"❌ Failed with status {resp.status}")


# ============================================================================
# EXAMPLE 4: Embeddings en PC2
# ============================================================================

async def example_embeddings_pc2(pc1_host: str = "localhost",
                                 texts: List[str] = None):
    """
    Generar embeddings usando PC2 (optimizado para esto)
    """
    if texts is None:
        texts = [
            "Hola, ¿cómo estás?",
            "¿Cuál es tu nombre?",
            "Esto es una prueba de embeddings",
        ]
    
    print("\n" + "="*70)
    print("📊 EXAMPLE 4: Embeddings on PC2 (Optimized)")
    print("="*70)
    
    request_body = {
        "texts": texts,
        "gpu_index": 0
    }
    
    print(f"\nSending {len(texts)} texts to PC2 for embedding...")
    for i, text in enumerate(texts):
        print(f"  {i+1}. {text}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{pc1_host}:8001/embed-batch",
            json=request_body
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"\n✅ Response from PC2:")
                print(f"  Texts: {data.get('count', 'N/A')}")
                print(f"  Embeddings generated: {len(data.get('embeddings', []))}")
                print(f"  Embedding dimension: {len(data.get('embeddings', [[]])[0])}")
                
                # Show first embedding sample
                if data.get('embeddings'):
                    first_embedding = data['embeddings'][0]
                    print(f"  First embedding (first 5 values): {first_embedding[:5]}")
            else:
                print(f"❌ Failed with status {resp.status}")


# ============================================================================
# EXAMPLE 5: Single Embedding
# ============================================================================

async def example_single_embedding(pc1_host: str = "localhost",
                                   text: str = "Ejemplo de embedding simple"):
    """
    Generar embedding para un único texto
    """
    print("\n" + "="*70)
    print("📝 EXAMPLE 5: Single Embedding")
    print("="*70)
    
    request_body = {
        "text": text,
        "gpu_index": 0
    }
    
    print(f"\nSending text to PC2 for embedding...")
    print(f"  Text: {text}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{pc1_host}:8001/embed",
            json=request_body
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"\n✅ Response from PC2:")
                print(f"  Text: {data.get('text', 'N/A')}")
                print(f"  Model: {data.get('model', 'N/A')}")
                print(f"  Embedding size: {len(data.get('embedding', []))}")
                print(f"  First 5 values: {data.get('embedding', [])[:5]}")
            else:
                print(f"❌ Failed with status {resp.status}")


# ============================================================================
# EXAMPLE 6: System Configuration
# ============================================================================

async def example_system_config(pc1_host: str = "localhost"):
    """
    Ver configuración completa del sistema
    """
    print("\n" + "="*70)
    print("⚙️  EXAMPLE 6: System Configuration")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        print("\n📋 PC1 Configuration:")
        async with session.get(f"http://{pc1_host}:8000/config") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"  Name: {data.get('pc_name', 'N/A')}")
                print(f"  Host: {data.get('host', 'N/A')}:{data.get('port', 'N/A')}")
                print(f"  Coordinator: {data.get('is_coordinator', 'N/A')}")
                print(f"  Total VRAM: {data.get('total_vram_gb', 'N/A'):.1f}GB")
                print(f"  CPU Cores: {data.get('cpu_cores', 'N/A')}")
                print(f"  RAM: {data.get('ram_gb', 'N/A'):.1f}GB")
                print(f"  GPUs: {len(data.get('gpus', []))}")


# ============================================================================
# EXAMPLE 7: Status Check
# ============================================================================

async def example_status_check(pc1_host: str = "localhost"):
    """
    Ver estado actual de cada PC
    """
    print("\n" + "="*70)
    print("📊 EXAMPLE 7: System Status")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        for pc_num, port in [("PC1", 8000), ("PC2", 8001)]:
            print(f"\n🖥️  {pc_num} Status:")
            async with session.get(f"http://{pc1_host}:{port}/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  Name: {data.get('pc_name', 'N/A')}")
                    print(f"  Host: {data.get('host', 'N/A')}:{data.get('port', 'N/A')}")
                    print(f"  Is Coordinator: {data.get('is_coordinator', 'N/A')}")
                    print(f"  Uptime: {data.get('uptime_seconds', 0):.1f}s")
                    
                    gpu_info = data.get('gpu_info', {})
                    for gpu_key, gpu_data in gpu_info.items():
                        print(f"\n  {gpu_key}:")
                        print(f"    Name: {gpu_data.get('name', 'N/A')}")
                        print(f"    Type: {gpu_data.get('type', 'N/A')}")
                        print(f"    VRAM Total: {gpu_data.get('vram_total_gb', 'N/A'):.1f}GB")
                        print(f"    VRAM Free: {gpu_data.get('vram_free_gb', 'N/A'):.1f}GB")
                        print(f"    CUDA Cores: {gpu_data.get('cuda_cores', 'N/A'):,}")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all examples"""
    
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║         🎯 TARS DISTRIBUTED SYSTEM - USAGE EXAMPLES              ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Askfor PC1 host
    pc1_host = input("\nEnter PC1 host (default: localhost): ").strip() or "localhost"
    
    try:
        # Run examples
        await example_health_checks(pc1_host)
        await example_get_models(pc1_host)
        await example_system_config(pc1_host)
        await example_status_check(pc1_host)
        await example_single_embedding(pc1_host)
        await example_embeddings_pc2(pc1_host)
        await example_inference_pc1(pc1_host)
        
        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70)
        
    except aiohttp.ClientConnectorError as e:
        print(f"\n❌ Connection error: {e}")
        print(f"\nMake sure:")
        print(f"  1. PC1 is running at {pc1_host}:8000")
        print(f"  2. PC2 is running at {pc1_host}:8001")
        print(f"  3. Network connectivity is available")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
