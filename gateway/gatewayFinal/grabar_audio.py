import os
import time
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from scipy.signal import butter, lfilter

# Configuración de grabación
MAX_DURATION = 10  # Duración máxima de la grabación
SAMPLE_RATE = 44100  # Frecuencia de muestreo
THRESHOLD = 0.1  # Umbral para detectar sonido relevante
output_folder = "/home/gateway/AudioForestal"
os.makedirs(output_folder, exist_ok=True)

# Filtro pasa-banda
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut=300, highcut=8000, fs=SAMPLE_RATE, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

# Normalizar volumen en función del ruido base
def normalize_audio(audio_buffer, noise_level):
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        gain = 0.5 / max(max_amplitude, noise_level)  # Ajusta para que el volumen no sea excesivo
        return audio_buffer * gain
    return audio_buffer

# Calcular nivel de ruido base
def get_noise_level(duration=2):
    print("Analizando nivel de ruido base...")
    noise_sample = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    noise_level = np.max(np.abs(noise_sample))
    print(f"Nivel de ruido base: {noise_level}")
    return noise_level

# Detectar y guardar sonido relevante
def detect_and_record():
    noise_level = get_noise_level()  # Calcular nivel de ruido base
    print("Iniciando grabación continua...")
    while True:
        print("Grabando fragmento...")
        audio = sd.rec(int(SAMPLE_RATE * MAX_DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()

        # Aplicar filtro pasa-banda
        filtered_audio = bandpass_filter(audio)

        # Normalizar con base en el nivel de ruido
        normalized_audio = normalize_audio(filtered_audio, noise_level)

        # Verificar si supera el umbral
        if np.max(np.abs(normalized_audio)) > THRESHOLD:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_folder, f"audio_{timestamp}.wav")
            write(filename, SAMPLE_RATE, (normalized_audio * 32767).astype(np.int16))
            print(f"Audio guardado: {filename}")
        else:
            print("No se detectó sonido relevante.")

# Iniciar el proceso
if __name__ == "__main__":
    detect_and_record()
