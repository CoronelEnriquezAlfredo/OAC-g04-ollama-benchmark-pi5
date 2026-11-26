<div align="center">

# 🧠 IA Local (Ollama) y Benchmark Automatizado en Raspberry Pi 5

**Despliegue 100% replicable con Docker Compose para inferencia local de LLMs, interfaz web y monitoreo dinámico de rendimiento en arquitectura ARM64.**

![Raspberry Pi 5](https://img.shields.io/badge/Raspberry%20Pi%205-16GB%20RAM-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Architecture](https://img.shields.io/badge/Arch-ARM64-0091BD?style=for-the-badge&logo=arm&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-000000?style=for-the-badge&logo=ollama&logoColor=white)

</div>

---

## 📋 Información Académica

| Campo | Detalle |
| :--- | :--- |
| **Materia** | Organización y Arquitectura de Computadoras — Grupo 04 |
| **Profesor** | Ing. Ricardo Daniel Vega Gutiérrez |
| **Autores** | • Arroyo Onofre Leonardo<br>• Coronel Enríquez Alfredo<br>• De la Rosa Flores Fernando<br>• Núñez Pozos Jorge Carlos |
| **Plataforma Objetivo** | Raspberry Pi 5 (16 GB RAM, CPU ARM Cortex-A76, 64-bit) |

---

## 📖 Descripción General

Este repositorio provee un entorno contenedorizado y replicable con **Docker Compose** para ejecutar modelos de lenguaje (LLMs) de forma **100% local** en una Raspberry Pi 5 sin depender de servicios en la nube ni GPU externa.

El stack despliega automáticamente:
1. **Motor de Inferencia (Ollama):** Descarga y optimiza 5 modelos cuantizados en 4 bits.
2. **Interfaz Web (Open WebUI):** Plataforma tipo ChatGPT para interactuar y alternar entre modelos.
3. **Benchmark Web Dinámico:** Servicio en Python que evalúa todos los modelos al iniciar y publica gráficas interactivas (**Chart.js**) junto con un archivo `.csv` descargable.

### 🏗️ Arquitectura de Contenedores

| Servicio | Contenedor | Puerto | Función |
| :--- | :--- | :---: | :--- |
| **Motor de IA** | `c-ollama-proyfinal` | `11434` | Ejecuta Ollama y descarga automáticamente los 5 modelos optimizados. |
| **Interfaz Web** | `open-webui` | `8080` | Panel web interactivo para chatear y gestionar parámetros de contexto. |
| **Benchmark Web** | `c-benchmark-web` | `8085` | Evalúa los modelos al iniciar y publica gráficas dinámicas y un CSV descargable. |

---

## 🤖 Modelos Precargados y Optimizaciones

Al iniciar el despliegue por primera vez, el script `init-ollama.sh` descarga automáticamente **5 modelos cuantizados (4-bit)** seleccionados para el ancho de banda de memoria y los 4 núcleos ARM Cortex-A76 de la Raspberry Pi 5:

| Nivel | Modelo | Peso Aprox. | Enfoque Principal |
| :---: | :--- | :---: | :--- |
| 🟢 **Bajo** | `qwen2.5:0.5b` | ~397 MB | Respuestas ultra rápidas y baja latencia. |
| 🟡 **Medio** | `gemma3:1b` | ~806 MB | Balance equilibrado entre velocidad y redacción. |
| 🟡 **Medio** | `llama3.2:1b` | ~1.3 GB | Chat general, resúmenes e instrucciones. |
| 🔵 **Alto** | `qwen2.5:1.5b` | ~986 MB | Alta precisión técnica y excelente español. |
| 🔵 **Alto** | `qwen2.5-coder:1.5b` | ~986 MB | Generación de código, Bash, Python y Linux. |

### ⚡ Variables de Optimización (`docker-compose.yml`)
* **`OLLAMA_KEEP_ALIVE=24h`** y **`OLLAMA_MAX_LOADED_MODELS=3`**: Mantienen los modelos precargados en RAM para evitar recargas lentas desde la microSD.
* **`OLLAMA_FLASH_ATTENTION=1`** y **`OLLAMA_KV_CACHE_TYPE=q8_0`**: Reducen el uso de ancho de banda de memoria y aceleran la generación de tokens.
* **`OLLAMA_NUM_PARALLEL=1`**: Dedica los 4 núcleos del CPU a una petición a la vez para maximizar los `tokens/s`.

---

## 🛠️ Requisitos Previos

* **Hardware:** Raspberry Pi 5 (8 GB o 16 GB de RAM) con disipación activa (*Active Cooler* recomendada) y fuente oficial de 5V/5A (27W).
* **Sistema Operativo:** Ubuntu Server/Desktop o Raspberry Pi OS de **64 bits (`arm64`)**.
* **Software:** `git`, `docker` y `docker compose` (v2) instalados.
* **Almacenamiento:** Al menos **10 GB libres** en disco.

---

## 🚀 Guía de Replicación Paso a Paso

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

### 4. Monitorear la descarga y el benchmark automático
> [!NOTE]
> La primera ejecución tardará unos minutos mientras descarga los 5 modelos y ejecuta las pruebas de rendimiento. Puedes seguir el progreso en tiempo real con estos comandos (`Ctrl + C` para salir sin detener los contenedores):

```bash
# Ver progreso de descarga de los 5 modelos
sudo docker logs -f c-ollama-proyfinal

# Ver progreso del benchmark automático (en otra terminal)
sudo docker logs -f c-benchmark-web
```

### 5. Acceder a los servicios
Sustituye `<IP_RASPBERRY>` por la IP local de tu Raspberry Pi (consúltala con `hostname -I`):

* 💬 **Chat IA (Open WebUI):** `http://<IP_RASPBERRY>:8080`
* 📊 **Gráficas Dinámicas del Benchmark:** `http://<IP_RASPBERRY>:8085`
* 📄 **Resultados en formato CSV:** `http://<IP_RASPBERRY>:8085/resultados_benchmark.csv`
* ⚙️ **API REST de Ollama:** `http://<IP_RASPBERRY>:11434`

---

## ⚠️ Solución de Errores Comunes

| Error o Síntoma | Causa Probable | Solución |
| :--- | :--- | :--- |
| **`Bind for 0.0.0.0:11434 failed: port is already allocated`** | Ya existe una instalación nativa de Ollama corriendo en el sistema. | Detén el servicio nativo antes de levantar Docker:<br>`sudo systemctl stop ollama && sudo systemctl disable ollama`<br>Luego ejecuta `sudo docker compose up -d`. |
| **`exec /init-ollama.sh: permission denied`** | El archivo `init-ollama.sh` perdió permisos de ejecución al clonarse. | Ejecuta `chmod +x init-ollama.sh` y reinicia con `sudo docker compose restart ollama`. |
| **`/bin/sh: /init-ollama.sh: not found` o error `\r`** | El script se editó en Windows y guardó saltos de línea `CRLF`. | Convierte el formato a Unix (`LF`):<br>`sed -i 's/\r$//' init-ollama.sh`<br>y reinicia con `sudo docker compose up -d --force-recreate`. |
| **Puerto `8080` o `8085` ya ocupado** | Otro contenedor o servicio web (Nginx, Apache) usa ese puerto. | Edita `docker-compose.yml` y cambia el puerto izquierdo (ej. `"8081:8080"` o `"8086:8085"`), luego corre `sudo docker compose up -d`. |
| **El puerto `8085` sigue en "Benchmark en progreso"** | Ollama aún descarga modelos o el benchmark sigue evaluando. | Revisa `sudo docker logs -f c-ollama-proyfinal` hasta ver `Todos los modelos estan listos.` y espera a que `c-benchmark-web` imprima `Benchmark finalizado`. |
| **Temperatura alta (>80 °C) o caída de velocidad** | *Thermal throttling* del CPU por carga sostenida sin ventilación adecuada. | Verifica con `awk '{printf "%.1f °C\n", $1/1000}' /sys/class/thermal/thermal_zone0/temp`. Usa disipador activo y fuente de 27W. |
| **Open WebUI no muestra los modelos** | La interfaz arrancó antes de terminar la descarga de modelos. | Presiona `F5` en el navegador para recargar; los modelos aparecerán en el selector superior izquierdo. |

---

## 🧰 Comandos Útiles de Mantenimiento

```bash
# Ver estado de los contenedores activos
sudo docker ps

# Volver a ejecutar el benchmark y actualizar las gráficas
sudo docker compose restart benchmark-web

# Detener todos los servicios (conservando modelos descargados)
sudo docker compose down

# Detener y eliminar también los volúmenes y modelos (limpieza total)
sudo docker compose down -v
```
