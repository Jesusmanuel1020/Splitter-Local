import os
import librosa
import pyrubberband as pyrb
import soundfile as sf
import ffmpeg

def apply_pitch_shift(song_id: str, semitones: int, stem: str = "all") -> str:
    """
    Applies pitch shifting to a specific stem or the original song.
    Returns the relative path to the generated file.
    """
    storage_dir = os.path.join("storage", song_id)
    
    # Determine input file
    if stem == "all":
        input_filename = "original.mp3"
    else:
        input_filename = f"{stem}.mp3"
        
    input_path = os.path.join(storage_dir, input_filename)
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Source file not found: {input_path}")

    # Determine output file
    output_filename = f"pitch_{semitones}_{stem}.mp3"
    output_path = os.path.join(storage_dir, output_filename)
    
    # If it already exists, return it (caching)
    if os.path.exists(output_path):
        return f"/storage/{song_id}/{output_filename}"

    # Process with pyrubberband
    # 1. Load audio
    y, sr = librosa.load(input_path, sr=None)
    
    # 2. Apply pitch shift
    y_shifted = pyrb.pitch_shift(y, sr, semitones)
    
    # 3. Save to temporary WAV (soundfile doesn't support mp3 export directly)
    temp_wav = os.path.join(storage_dir, f"temp_pitch_{semitones}_{stem}.wav")
    sf.write(temp_wav, y_shifted, sr)
    
    # 4. Convert WAV to MP3 320kbps using ffmpeg
    try:
        (
            ffmpeg
            .input(temp_wav)
            .output(output_path, audio_bitrate='320k')
            .overwrite_output()
            .run(quiet=True)
        )
    finally:
        # 5. Clean up temp WAV
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

    return f"/storage/{song_id}/{output_filename}"
