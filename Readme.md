---
title: Splitter Local
emoji: 🎵
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---


# Moises Local

Una aplicación web local para separación de pistas de audio (stems) y cambio de tonalidad (pitch shifting), optimizada para ejecutarse localmente sin costos de nube.

## 1. Descripción de la Arquitectura

El proyecto está construido con una arquitectura modular basada en Python:

- **FastAPI**: Framework web principal que maneja las peticiones HTTP, la subida de archivos y sirve los archivos estáticos.
- **SQLite + SQLModel**: Base de datos local (`moises_db.sqlite`) para almacenar el estado de las canciones, metadatos (BPM) y rutas de archivos.
- **Demucs**: Motor de IA ejecutado mediante subprocesos (`subprocess`) para separar las canciones en 4 stems (vocals, drums, bass, other).
- **FFmpeg**: Utilizado para convertir los archivos `.wav` pesados generados por Demucs a `.mp3` a 320 kbps, ahorrando espacio en disco.
- **RubberBand (pyrubberband) + Librosa**: Utilizados para el análisis de BPM y el pitch-shifting de alta calidad sin alterar el tempo.
- **BackgroundTasks**: FastAPI utiliza tareas en segundo plano para procesar la separación de audio sin bloquear la respuesta al cliente.

## 2. Requisitos Previos del Sistema

Para ejecutar este proyecto, necesitas tener instalado en tu sistema:

1. **Python 3.10+**
2. **FFmpeg**: Debe estar instalado y accesible en el PATH del sistema.
   - Windows: Descargar desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) o usar `winget install ffmpeg`.
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **RubberBand Library**: Requerido por `pyrubberband`.
   - Windows: Descargar los binarios desde [breakfastquay.com](https://breakfastquay.com/rubberband/) y agregarlos al PATH.
   - macOS: `brew install rubberband`
   - Linux: `sudo apt install rubberband-cli`

## 3. Instalación Paso a Paso

1. **Clonar o descargar el proyecto** y navegar a la carpeta raíz:
   ```bash
   cd moises-local
   ```

2. **Crear un entorno virtual**:
   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Guía de Ejecución Rápida

1. **Iniciar el servidor FastAPI**:
   ```bash
   uvicorn main:app --reload
   ```
   El servidor estará disponible en `http://localhost:8000`.
   La documentación interactiva de la API estará en `http://localhost:8000/docs`.

2. **Inspeccionar la Base de Datos (Opcional)**:
   Abre una nueva terminal, activa el entorno virtual y ejecuta:
   ```bash
   sqlite_web moises_db.sqlite --port 8080
   ```
   Podrás ver la base de datos en `http://localhost:8080`.

## 5. Ejemplos de Uso de la API

### Subir una canción para procesar
```bash
curl -X 'POST' \
  'http://localhost:8000/api/songs/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@mi_cancion.mp3'
```
*Respuesta esperada:*
```json
{
  "message": "Upload successful, processing started",
  "song_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Consultar el estado de la canción
```bash
curl -X 'GET' 'http://localhost:8000/api/songs/123e4567-e89b-12d3-a456-426614174000'
```
*Cuando termine, `status` será `"completed"` y `has_stems` será `true`.*

### Aplicar Pitch-Shift (Ej: +2 semitonos a las voces)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/songs/123e4567-e89b-12d3-a456-426614174000/pitch-shift?semitones=2&stem=vocals' \
  -H 'accept: application/json' \
  -d ''
```
*Respuesta esperada:*
```json
{
  "message": "Pitch shift successful",
  "url": "/storage/123e4567-e89b-12d3-a456-426614174000/pitch_2_vocals.mp3"
}
```
Puedes reproducir el archivo resultante directamente en tu navegador accediendo a `http://localhost:8000/storage/123e4567-e89b-12d3-a456-426614174000/pitch_2_vocals.mp3`.
