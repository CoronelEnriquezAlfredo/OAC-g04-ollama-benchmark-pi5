#!/bin/bash
# Despliega Open WebUI conectado al servicio local de Ollama en el puerto 8080
set -e

sudo docker rm -f open-webui 2>/dev/null || true
sudo docker run -d \
  --name open-webui \
  --restart always \
  -p 8080:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

echo "Open WebUI disponible en http://localhost:8080"
