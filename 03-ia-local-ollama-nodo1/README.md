# Modulo 03: IA Local (Ollama + Open WebUI + Benchmark Automatico)

Despliegue replicable con Docker Compose optimizado para Raspberry Pi 5 (ARM64).

## Modelos precargados automaticamente
* qwen2.5:0.5b (Nivel bajo / ultra rapido)
* gemma3:1b y llama3.2:1b (Nivel medio / equilibrado)
* qwen2.5:1.5b y qwen2.5-coder:1.5b (Nivel alto / tecnico y codigo)

## Como replicarlo en otra Raspberry Pi 5
1. Clona el repositorio y entra a la carpeta 03-ia-local-ollama-nodo1
2. Ejecuta: chmod +x init-ollama.sh
3. Ejecuta: sudo docker compose up -d

## Servicios disponibles
* Open WebUI (Chat IA): http://<IP_RASPBERRY>:8080
* Dashboard de Graficas Dinamicas: http://<IP_RASPBERRY>:8085
* Resultados en CSV: http://<IP_RASPBERRY>:8085/resultados_benchmark.csv
* API Ollama: http://<IP_RASPBERRY>:11434