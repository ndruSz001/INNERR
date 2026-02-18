import asyncio
import time
import requests

# Prueba de carga: envía muchas inferencias a PC2
async def stress_test(pc2_url, n_requests=50):
    payload = {
        "prompt": "Test stress distributed",
        "max_tokens": 16,
        "temperature": 0.7,
        "gpu_index": 0
    }
    successes = 0
    failures = 0
    for i in range(n_requests):
        try:
            r = requests.post(pc2_url, json=payload, timeout=5)
            if r.status_code == 200:
                successes += 1
            else:
                failures += 1
        except Exception as e:
            failures += 1
        time.sleep(0.1)
    print(f"Stress test completed: {successes} successes, {failures} failures out of {n_requests} requests.")

if __name__ == "__main__":
    asyncio.run(stress_test("http://127.0.0.1:8001/inference", n_requests=50))
