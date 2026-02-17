#!/bin/bash
# Script para iniciar la PC secundaria (worker)
# Cambia <IP_PC1> por la IP real de la PC principal

python3 dimensity/distributed/api_distributed.py --pc_name PC2 --host 0.0.0.0 --port 8001 --remote_host 192.168.1.190 --remote_port 8000
