#!/bin/bash
# Simula ambos nodos distribuidos en la misma máquina

# Lanzar PC1 (coordinador) en el puerto 8000
echo "Iniciando PC1 (coordinador) en puerto 8000..."
nohup python3 -m distributed.api_distributed --pc-name PC1 --host 127.0.0.1 --port 8000 > pc1.log 2>&1 &
PC1_PID=$!
sleep 3

# Lanzar PC2 (worker) en el puerto 8001, conectado a PC1

echo "Iniciando PC2 (worker) en puerto 8001, conectado a PC1..."
nohup python3 -m distributed.api_distributed --pc-name PC2 --host 127.0.0.1 --port 8001 --remote-host 127.0.0.1 --remote-port 8000 > pc2.log 2>&1 &
PC2_PID=$!
sleep 3

echo "Ambos nodos están corriendo. (PC1 PID: $PC1_PID, PC2 PID: $PC2_PID)"
echo "Para detenerlos: kill $PC1_PID $PC2_PID"
