import csv
import http.server
import json
import os
import socketserver
import threading
import time
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
WEB_DIR = "/app/web"
PORT = 8085
PROMPT = "Explica en 4 lineas que es Docker y cual es su ventaja principal frente a una maquina virtual."
EXPECTED_MODELS = 5

os.makedirs(WEB_DIR, exist_ok=True)

def write_loading_page(msg):
    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="10">
<title>Ejecutando Benchmark...</title>
<style>body{{font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;}}</style>
</head><body><div><h1 style="color:#38bdf8;">Benchmark Ollama en progreso</h1><p>{msg}</p><p style="color:#94a3b8;">Esta pagina se actualizara automaticamente...</p></div></body></html>"""
    with open(f"{WEB_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)

def start_http_server():
    os.chdir(WEB_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"Servidor web de graficas activo en http://0.0.0.0:{PORT}")
        httpd.serve_forever()

def get_models():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000.0, 1)
    except Exception:
        return 0.0

def benchmark_model(model):
    payload = json.dumps({
        "model": model,
        "prompt": PROMPT,
        "stream": False,
        "options": {"num_ctx": 2048}
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        res = json.loads(resp.read().decode())

    load_s = res.get("load_duration", 0) / 1e9
    prompt_s = max(res.get("prompt_eval_duration", 1) / 1e9, 0.001)
    eval_s = max(res.get("eval_duration", 1) / 1e9, 0.001)

    return {
        "modelo": model,
        "load_s": round(load_s, 2),
        "prompt_tps": round(res.get("prompt_eval_count", 0) / prompt_s, 2),
        "eval_tps": round(res.get("eval_count", 0) / eval_s, 2),
        "temp_c": get_cpu_temp(),
    }

def build_html(rows):
    data_json = json.dumps(rows)
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Benchmark Dinamico Ollama - Raspberry Pi 5</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
    h1 {{ text-align: center; color: #38bdf8; margin-bottom: 0.25rem; }}
    p.sub {{ text-align: center; color: #94a3b8; margin-top: 0; margin-bottom: 2rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 0 auto; }}
    .card {{ background: #1e293b; padding: 1.5rem; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.35); }}
    table {{ width: 100%; max-width: 1200px; margin: 2rem auto 0; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
    th, td {{ padding: 0.85rem 1rem; text-align: center; border-bottom: 1px solid #334155; }}
    th {{ background: #0284c7; color: #fff; }}
    tr:hover {{ background: #334155; }}
  </style>
</head>
<body>
  <h1>Benchmark Dinamico de IA Local (Ollama)</h1>
  <p class="sub">Despliegue Docker Replicable | Raspberry Pi 5 (ARM64)</p>
  <div class="grid">
    <div class="card"><canvas id="chartTokens"></canvas></div>
    <div class="card"><canvas id="chartCargaTemp"></canvas></div>
  </div>
  <table>
    <thead><tr><th>Modelo</th><th>Carga (s)</th><th>Lectura (tok/s)</th><th>Generacion (tok/s)</th><th>Temp CPU (C)</th></tr></thead>
    <tbody id="tablaDatos"></tbody>
  </table>
  <script>
    const data = {data_json};
    const labels = data.map(d => d.modelo);
    const opts = {{
      responsive: true,
      plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#cbd5e1' }}, grid: {{ color: '#334155' }} }},
        y: {{ ticks: {{ color: '#cbd5e1' }}, grid: {{ color: '#334155' }} }}
      }}
    }};
    new Chart(document.getElementById('chartTokens'), {{
      type: 'bar',
      data: {{
        labels,
        datasets: [
          {{ label: 'Generacion (tokens/s)', data: data.map(d => d.eval_tps), backgroundColor: '#38bdf8' }},
          {{ label: 'Lectura Prompt (tokens/s)', data: data.map(d => d.prompt_tps), backgroundColor: '#818cf8' }}
        ]
      }},
      options: {{ ...opts, plugins: {{ ...opts.plugins, title: {{ display: true, text: 'Velocidad de Tokens por Modelo', color: '#f8fafc' }} }} }}
    }});
    new Chart(document.getElementById('chartCargaTemp'), {{
      type: 'line',
      data: {{
        labels,
        datasets: [
          {{ label: 'Temperatura CPU (C)', data: data.map(d => d.temp_c), borderColor: '#ef4444', backgroundColor: '#ef4444', tension: 0.3 }},
          {{ label: 'Tiempo de Carga (s)', data: data.map(d => d.load_s), borderColor: '#a855f7', backgroundColor: '#a855f7', tension: 0.3 }}
        ]
      }},
      options: {{ ...opts, plugins: {{ ...opts.plugins, title: {{ display: true, text: 'Temperatura y Tiempo de Carga', color: '#f8fafc' }} }} }}
    }});
    const tbody = document.getElementById('tablaDatos');
    data.forEach(r => {{
      tbody.innerHTML += `<tr><td><b>${{r.modelo}}</b></td><td>${{r.load_s}}</td><td>${{r.prompt_tps}}</td><td><b>${{r.eval_tps}}</b></td><td>${{r.temp_c}}C</td></tr>`;
    }});
  </script>
</body>
</html>"""
    with open(f"{WEB_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    write_loading_page("Esperando a que Ollama termine de descargar los modelos...")
    threading.Thread(target=start_http_server, daemon=True).start()

    while True:
        modelos = get_models()
        if len(modelos) >= EXPECTED_MODELS:
            break
        print(f"Modelos listos: {len(modelos)}/{EXPECTED_MODELS}. Esperando...")
        time.sleep(10)

    resultados = []
    for m in modelos:
        write_loading_page(f"Evaluando modelo: <b>{m}</b>...")
        print(f" -> Evaluando {m}...")
        resultados.append(benchmark_model(m))

    with open(f"{WEB_DIR}/resultados_benchmark.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados)

    build_html(resultados)
    print("Benchmark finalizado. Dashboard publicado en el puerto 8085.")

    while True:
        time.sleep(3600)