#!/bin/sh
/bin/ollama serve &
pid=$!

echo "Esperando a que Ollama inicie..."
until ollama list >/dev/null 2>&1; do
  sleep 2
done

for modelo in qwen2.5:0.5b gemma3:1b llama3.2:1b qwen2.5:1.5b qwen2.5-coder:1.5b; do
  echo "Verificando/descargando modelo: $modelo"
  ollama pull "$modelo"
done

echo "Todos los modelos estan listos."
wait $pid