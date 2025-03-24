# Importamos librosa para el procesamiento de audios
import librosa
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.models import model_from_json

# Cargar la arquitectura
with open("model.json", "r") as json_file:
    loaded_model_json = json_file.read()
model = model_from_json(loaded_model_json)
print(model.summary())

# Cargar pesos comprimidos
weights = np.load("model_weights.npz")
model.set_weights([weights[f"arr_{i}"] for i in range(len(weights.files))])
print("Modelo cargado correctamente con pesos comprimidos.")
max_duration = 24.973514739229024

# Función para extraer MFCC de un archivo de audio
# Los coeficientes MFCC extraen caracteristicas de las ondas que componen audio que permiten, entre otras cosas,
# reconocer voz o, para este caso, emociones.
def extract_mfcc(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)  # Extraer 13 coeficientes, MFCC
    return mfcc

def pad_audio(audio, sr, max_duration):
    # Calcula el número de samples necesarios para la duración máxima
    max_samples = int(max_duration * sr)

    if len(audio) < max_samples:  # Si es más corto, añadir ceros al audio (padding)
        padded_audio = np.pad(audio, (0, max_samples - len(audio)))

    else:  # Si es más largo, recortar audio (truncamiento)
        padded_audio = audio[:max_samples]

    return padded_audio

# Predicción para un nuevo audio
def make_prediction(audio_file):
    
    global max_duration
    
    print(audio_file)
    # Buscamos la duracion máxima de los audios del dataset
    audio_duration = []
    
    emotions = ["Tristeza", "Alegría", "Neutral", "Disgusto", "Enojo"]
    print(emotions)
            
    # Convertimos listas a arreglos de numpy  
    y = np.array(emotions)

    # Dividimos conjuntos X e y en datos de entrenamiento, pruebas y validación
    from sklearn.model_selection import train_test_split

    # Codificamos las etiquetas
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    # Llevamos el audio recibido al formato esperado por nuestra red neuronal
    from io import BytesIO
    # Cargar el archivo de audio directamente desde el flujo de bytes
    audio_data, sr = librosa.load(BytesIO(audio_file.read()))
    print(audio_data.shape)

    # Añadir padding o truncarlo al máximo permitido (por ejemplo, max_duration en segundos)
    new_padded_audio = pad_audio(audio_data, sr, max_duration)
    new_padded_audio = new_padded_audio / np.max(np.abs(new_padded_audio))  # Normalizar

    # Extraer los coeficientes MFCC
    mfcc_new_audio = extract_mfcc(new_padded_audio, sr).T

    # Ajustar dimensiones para que sean compatibles con el modelo RNN
    mfcc_new_audio = np.expand_dims(mfcc_new_audio, axis=0)  # (1, n_samples, n_features)

    # Realizar la predicción usando el modelo
    try:
        print("Realizando la predicción... hola3")
        predicted_class = model.predict(mfcc_new_audio)
        predicted_emotion = label_encoder.inverse_transform([np.argmax(predicted_class)])
        print("HOLA5")
        print(f"Resultado de la predicción1: {predicted_class}")
        
        return predicted_emotion
    except Exception as e:
        print(f"Error al hacer la predicción: {e}")

    




