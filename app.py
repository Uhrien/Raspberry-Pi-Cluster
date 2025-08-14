from fastapi import FastAPI, File, UploadFile
from faster_whisper import WhisperModel
import tempfile
import os # Importa os per la pulizia

app = FastAPI()

# Carica il modello all'avvio (più efficiente)
# "small" è un buon compromesso. Potresti anche usare "base".
print("Caricando il modello faster-whisper 'small'...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Modello caricato.")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Crea un file temporaneo con un nome sicuro
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
        # Scrivi il contenuto del file caricato nel file temporaneo
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    print(f"File ricevuto: {file.filename}, salvato in {tmp_path}. Inizio trascrizione...")

    try:
        segments, _ = model.transcribe(tmp_path, language="it") # Lingua specificata
        # Unisci tutti i segmenti di testo in una singola stringa
        transcription = " ".join([segment.text for segment in segments])
        print("Trascrizione completata.")
    finally:
        # Assicurati che il file temporaneo venga sempre cancellato
        os.remove(tmp_path)
    
    return {"text": transcription}
