#!/bin/bash
# Instala Ollama en Raspberry Pi 5 (Ubuntu ARM64) y descarga modelo ligero
set -e

curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama

echo "Descargando modelo llama3.2:1b..."
ollama pull llama3.2:1b
ollama list
