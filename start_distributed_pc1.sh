#!/bin/bash
# Script para iniciar la PC principal (coordinador)

/home/ndrz02/keys_1/.venv/bin/python -m distributed.api_distributed --pc-name PC1 --host 0.0.0.0 --port 8000
