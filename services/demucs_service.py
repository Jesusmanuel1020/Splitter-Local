import os
import sys
import shutil
import subprocess
import librosa
import ffmpeg
import imageio_ffmpeg
from sqlmodel import Session
from models import Song
from database import engine

def process_song(song_id: str):
    with Session(engine) as session:
        song = session.get(Song, song_id)
        if not song:
            return

        try:
            # Update status to processing
            song.status = "processing"
            song.progress = 10
            session.add(song)
            session.commit()

            storage_dir = os.path.join("storage", song_id)
            original_file = os.path.join(storage_dir, "original.mp3")
            
            # 1. Run Demucs (Output temporal dentro de storage_dir)
            demucs_out_dir = os.path.join(storage_dir, "demucs_out")
            
            abs_original_file = os.path.abspath(original_file)
            abs_demucs_out_dir = os.path.abspath(demucs_out_dir)
                
            # Modelo elegido para evitar sobrecargar RAM/CPU en Hugging Face
            model_name = "mdx_extra_q"

            # Ejecutar demucs optimizado para entorno CPU de 2 núcleos
            subprocess.run([
                sys.executable,
                "-m", "demucs.separate",
                "-n", model_name,
                "-j", "2",                    # <-- Límite estricto de 2 hilos para evitar bloqueo por cuota
                "-o", abs_demucs_out_dir,
                abs_original_file
            ], check=True, capture_output=True)

            # Update progress after Demucs finishes
            song.progress = 70
            session.add(song)
            session.commit()

            # Demucs crea la estructura: demucs_out/<model_name>/<base_name>/
            base_name = os.path.splitext(os.path.basename(original_file))[0]
            stems_dir = os.path.join(demucs_out_dir, model_name, base_name)

            stems = ["vocals", "drums", "bass", "other"]
            
            # 2. Convert WAV to MP3 320kbps and delete WAV
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            for i, stem in enumerate(stems):
                wav_path = os.path.join(stems_dir, f"{stem}.wav")
                mp3_path = os.path.join(storage_dir, f"{stem}.mp3")
                
                if os.path.exists(wav_path):
                    # Convert to mp3
                    (
                        ffmpeg
                        .input(wav_path)
                        .output(mp3_path, audio_bitrate='320k')
                        .overwrite_output()
                        .run(cmd=ffmpeg_exe, quiet=True)
                    )
                    # Delete original wav
                    os.remove(wav_path)
                
                # Update progress for each stem conversion
                song.progress = 70 + int(((i + 1) / len(stems)) * 20) # Up to 90%
                session.add(song)
                session.commit()

            # Clean up demucs output directories
            if os.path.exists(demucs_out_dir):
                shutil.rmtree(demucs_out_dir)

            # 3. Calculate BPM using librosa
            y, sr = librosa.load(original_file)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # tempo can be an array or a float depending on librosa version, handle it
            if isinstance(tempo, (list, tuple)) or hasattr(tempo, 'item'):
                bpm_val = float(tempo.item() if hasattr(tempo, 'item') else tempo[0])
            else:
                bpm_val = float(tempo)

            # Update song in DB
            song.bpm = bpm_val
            song.status = "completed"
            song.progress = 100
            song.has_stems = True
            session.add(song)
            session.commit()

        except Exception as e:
            print(f"Error processing song {song_id}: {e}")
            song.status = "error"
            session.add(song)
            session.commit()