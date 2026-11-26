```markdown
# Despliegue Replicable de IA Local (Ollama) y Benchmark Automatizado en Raspberry Pi 5

* **Materia:** Organización y Arquitectura de Computadoras — Grupo 04
* **Profesor:** Ing. Ricardo Daniel Vega Gutiérrez
* **Autor:**

Arroyo Onofre Leonardo
Coronel Enriquez Alfredo
De la Rosa Flores Fernando
Núñez Pozos Jorge Carlos

* **Plataforma objetivo:** Raspberry Pi 5 (16 GB RAM, Arquitectura ARM64)

---

## Descripción General

Este repositorio contiene un entorno completamente replicable con **Docker Compose** para ejecutar modelos de lenguaje (LLMs) de forma 100% local en una Raspberry Pi 5, junto con una interfaz web tipo ChatGPT (**Open WebUI**) y un **servidor web de benchmarks dinámicos** (Chart.js) que evalúa automáticamente el rendimiento de cada modelo.

### Arquitectura de Contenedores

| Servicio | Contenedor | Puerto | Función |
| :--- | :--- | :---: | :--- |
| **Motor de IA** | `c-ollama-proyfinal` | `11434` | Ejecuta Ollama y descarga automáticamente los 5 modelos optimizados. |
| **Interfaz Web** | `open-webui` | `8080` | Panel web interactivo para chatear y alternar entre modelos. |
| **Benchmark Web** | `c-benchmark-web` | `8085` | Evalúa los modelos al iniciar y publica gráficas dinámicas y un CSV descargable. |

---

## Modelos Precargados y Optimizaciones

Al iniciar el despliegue por primera vez, el script `init-ollama.sh` descarga automáticamente 5 modelos cuantizados (4-bit) seleccionados específicamente para el ancho de banda de memoria y CPU ARM Cortex-A76 de la Raspberry Pi 5:

* **Nivel Bajo (Ultra rápido):** `qwen2.5:0.5b` (~397 MB)
* **Nivel Medio (Equilibrado):** `gemma3:1b` (~806 MB) y `llama3.2:1b` (~1.3 GB)
* **Nivel Alto (Técnico y código):** `qwen2.5:1.5b` (~986 MB) y `qwen2.5-coder:1.5b` (~986 MB)

**Variables de optimización aplicadas en `docker-compose.yml`:**
* `OLLAMA_KEEP_ALIVE=24h` y `OLLAMA_MAX_LOADED_MODELS=3`: Mantienen los modelos en RAM para evitar recargas lentas desde la microSD.
* `OLLAMA_FLASH_ATTENTION=1` y `OLLAMA_KV_CACHE_TYPE=q8_0`: Reducen el uso de ancho de banda de memoria y aceleran la generación de tokens.
* `OLLAMA_NUM_PARALLEL=1`: Dedica los 4 núcleos del CPU a una petición a la vez para maximizar los tokens/s.

---

## Requisitos Previos

* **Hardware:** Raspberry Pi 5 (8 GB o 16 GB de RAM) con disipación activa (*Active Cooler* recomendada).
* **Sistema Operativo:** Ubuntu Server/Desktop o Raspberry Pi OS de **64 bits (`arm64`)**.
* **Software:** `git`, `docker` y `docker compose` (v2) instalados.
* **Almacenamiento:** Al menos **10 GB libres** en disco.

---

## Guía de Replicación Paso a Paso

### 1. Clonar el repositorio y entrar al módulo
```bash
git clone [https://github.com/CoronelEnriquezAlfredo/OAC-g04-ollama-benchmark-pi5.git](https://github.com/CoronelEnriquezAlfredo/OAC-g04-ollama-benchmark-pi5.git)
cd OAC-g04-ollama-benchmark-pi5/03-ia-local-ollama-nodo1

```

### 2. Asignar permisos de ejecución al script de inicio

```bash
chmod +x init-ollama.sh

```

### 3. Levantar los contenedores

```bash
sudo docker compose up -d

```

### 4. Monitorear la descarga de modelos y el benchmark

La primera vez tardará unos minutos mientras descarga los 5 modelos y ejecuta las pruebas de rendimiento. Puedes ver el progreso en tiempo real con:

```bash
# Ver progreso de descarga de los 5 modelos
sudo docker logs -f c-ollama-proyfinal

# Ver progreso del benchmark automático (en otra terminal)
sudo docker logs -f c-benchmark-web

```

*(Presiona `Ctrl + C` para salir de los logs sin detener los contenedores).*

### 5. Acceder a los servicios

Sustituye `<IP_RASPBERRY>` por la IP local de tu Raspberry Pi (puedes consultarla con `hostname -I`):

* **Chat IA (Open WebUI):** `http://<IP_RASPBERRY>:8080`
* **Gráficas Dinámicas del Benchmark:** `http://<IP_RASPBERRY>:8085`
* **Resultados en formato CSV:** `http://<IP_RASPBERRY>:8085/resultados_benchmark.csv`
* **API REST de Ollama:** `http://<IP_RASPBERRY>:11434`

---

## Consideraciones de Errores Comunes y Soluciones

| Error o Síntoma | Causa Probable | Solución |
| --- | --- | --- |
| **`Bind for 0.0.0.0:11434 failed: port is already allocated`** | Ya existe una instalación nativa de Ollama corriendo en el sistema operativo de la Raspberry Pi. | Detén el servicio nativo antes de levantar Docker:<br>

<br>`sudo systemctl stop ollama && sudo systemctl disable ollama`<br>

<br>Luego ejecuta `sudo docker compose up -d`. |
| **`exec /init-ollama.sh: permission denied`** | El archivo `init-ollama.sh` perdió permisos de ejecución al clonarse o copiarse. | Ejecuta `chmod +x init-ollama.sh` y reinicia el contenedor con `sudo docker compose restart ollama`. |
| **`/bin/sh: /init-ollama.sh: not found` o error `\r**` | El script se editó en Windows y guardó saltos de línea `CRLF` en lugar de `LF` (Unix). | Convierte el formato en Linux:<br>

<br>`sed -i 's/\r$//' init-ollama.sh`<br>

<br>y reinicia con `sudo docker compose up -d --force-recreate`. |
| **Puerto `8080` o `8085` ya ocupado** | Otro contenedor o servicio web (Nginx, Apache, etc.) está usando ese puerto. | Edita `docker-compose.yml` y cambia el puerto izquierdo (por ejemplo, `"8081:8080"` o `"8086:8085"`), luego corre `sudo docker compose up -d`. |
| **El puerto `8085` se queda en "Benchmark en progreso"** | Ollama todavía está descargando alguno de los 5 modelos o el benchmark sigue evaluando. | Revisa `sudo docker logs -f c-ollama-proyfinal` para confirmar que diga `Todos los modelos estan listos.` y espera a que `c-benchmark-web` imprima `Benchmark finalizado`. |
| **Temperatura alta (>80 °C) o caída de velocidad** | *Thermal throttling* del procesador ARM por carga sostenida sin ventilación adecuada. | Verifica la temperatura con `awk '{printf "%.1f °C\n", $1/1000}' /sys/class/thermal/thermal_zone0/temp`. Asegúrate de usar disipador activo y fuente oficial de 5V/5A (27W). |
| **Open WebUI no muestra los modelos** | Open WebUI arrancó antes de que Ollama terminara de descargar los modelos. | Presiona `F5` en el navegador para recargar la interfaz; los modelos aparecerán automáticamente en el selector superior izquierdo. |

---

## Comandos Útiles de Mantenimiento

* **Ver estado de los contenedores:** `sudo docker ps`
* **Volver a ejecutar el benchmark:** `sudo docker compose restart benchmark-web`
* **Detener todos los servicios:** `sudo docker compose down`
* **Detener y borrar también los modelos descargados (limpieza total):** `sudo docker compose down -v`

```

```
