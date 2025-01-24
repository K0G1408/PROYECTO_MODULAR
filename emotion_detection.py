# Importamos librosa para el procesamiento de audios
import librosa
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model

# Definimos ruta al dataset
DATASET_PATH = r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\dataset\MESD"
max_duration = 2.53718820861678

# Buscamos la duracion máxima de los audios del dataset

def get_max_duration():
    global max_duration
    
    audio_duration = []
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".wav"):
            audio, sr = librosa.load(os.path.join(DATASET_PATH, file))
            audio_duration.append(librosa.get_duration(y=audio, sr=sr))

    max_duration = max(audio_duration)  # En segundos
    # print(f"Duración máxima: {max_duration} segundos")

# Función para extraer MFCC de un archivo de audio
# Los coeficientes MFCC extraen caracteristicas de las ondas que componen audio que permiten, entre otras cosas,
# reconocer voz o, para este caso, emociones.
def extract_mfcc(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)  # Extraer 13 coeficientes, MFCC
    return mfcc

def pad_audio(audio, sr, max_duration):
    # Calcula el número de samples necesarios para la duración máxima
    max_samples = int(max_duration * sr)

    if len(audio) < max_samples:  # Si es más corto, añadir ceros al audio (padding)
        padded_audio = np.pad(audio, (0, max_samples - len(audio)))

    else:  # Si es más largo, recortar audio (truncamiento)
        padded_audio = audio[:max_samples]

    return padded_audio

X_train, X_val, X_test, y_train, y_val, y_test = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
# Obtenemos conjuntos X e y
def make_train_test_sets():
    global X_val, X_test, y_val, y_test
    emotions = [] # Lista de etiquetas de los audios
    X = [] # Lista de audios
        
    # Añadimos padding/truncamos, normalizamos y extraemos MFCC en un solo paso
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".wav"):
            audio, sr = librosa.load(os.path.join(DATASET_PATH, file))
            padded_audio = pad_audio(audio, sr, max_duration)

            normalized_audio = padded_audio / np.max(np.abs(padded_audio)) # Normalización del audio en valores entre -1 y 1
            X.append(extract_mfcc(normalized_audio, sr).T)

    # Obtenemos las etiquetas correspondientes a cada audio
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".wav"):
            label = file.split("_")[0]  # Obtenemos la primera parte del nombre del archivo (la emoción, clase)
            emotions.append(label)
            
    # Convertimos listas a arreglos de numpy       
    X = np.array(X)
    y = np.array(emotions)

    # Dividimos conjuntos X e y en datos de entrenamiento, pruebas y validación
    from sklearn.model_selection import train_test_split

    # Codificamos las etiquetas
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    # Supongamos que X contiene las características y y contiene las etiquetas
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)  # 80% entrenamiento, 20% temp
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)  # 10% validación, 10% pruebas


# Añadimos ruido a un 20% de los datos del conjunto de entrenamiento
def add_noise(audio, noise_level=0.005):
  noise = np.random.randn(*audio.shape)
  augmented_audio = audio + noise_level * noise
  return np.clip(augmented_audio, -1.0, 1.0)

# Definimos un arreglo que tendra todos los datos con ruido o velocidad reducida
def data_augmentation():
    global X_train, y_train
    X_train_len = len(X_train)
    augmented_audios = []
    augmented_labels = []

    for index in range(0, int(X_train_len*.25) + 1): # Añadimos ruido a un 25% de los audios de X_train
      noisy_audio = add_noise(X_train[index]) # Añadimos ruido al audio

      if np.max(np.abs(noisy_audio)) > 0:
        noisy_audio /= np.max(np.abs(noisy_audio)) # Normalizamos audio si y solo si no hay una division entre cero

      augmented_audios.append(noisy_audio)
      augmented_labels.append(y_train[index])

    for index in range(int(X_train_len*.9), X_train_len): # Añadimos ruido al 10% restante de los audios de X_train
      noisy_audio = add_noise(X_train[index], noise_level=0.05) # Añadimos aun más ruido al audio

      if np.max(np.abs(noisy_audio)) > 0:
        noisy_audio /= np.max(np.abs(noisy_audio)) # Normalizamos audio si y solo si no hay una division entre cero

      augmented_audios.append(noisy_audio)
      augmented_labels.append(y_train[index])

    # Convertimos arreglo de audios procesados a un arreglo de Numpy
    augmented_audios = np.array(augmented_audios, dtype=X_train.dtype)

    # Concatenamos los nuevos audios con el conjunto de entrenamiento original
    X_train = np.concatenate([X_train, augmented_audios], axis=0)
    y_train = np.concatenate([y_train, augmented_labels], axis=0)
    
# Predicción para un nuevo audio
def get_results(path):
    # Cargamos el modelo ya entrenado
    
    # Cargamos la red LSTM entrenada
    model = load_model(r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\MODEL\bestModelBidirectional97-71.keras")

    # Definimos ruta de los audios
    AUDIOS_PATH = path
    
    # Buscamos la duracion máxima de los audios del dataset
    audio_duration = []
    
    emotions = ["Enojo", 
                "Desagrado", 
                "Miedo", 
                "Felicidad", 
                "Neutral", 
                "Tristeza"]
            
    # Convertimos listas a arreglos de numpy  
    y = np.array(emotions)

    # Dividimos conjuntos X e y en datos de entrenamiento, pruebas y validación
    from sklearn.model_selection import train_test_split

    # Codificamos las etiquetas
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    predicted_emotions = []
    for folder in os.listdir(AUDIOS_PATH):
      emotions = [] # Almacenamos todas las emociones predichas para este segmento de audio
      segment = os.path.join(AUDIOS_PATH, folder)
      for audio in os.listdir(segment):
        # Obtenemos informacion del audio
        audio_path = os.path.join(AUDIOS_PATH, folder, audio)
        audio, sr = librosa.load(audio_path)
        new_padded_audio = pad_audio(audio, sr, max_duration)
        # Añadimos padding al audio o lo truncamos y lo normalizamos en un solo paso
        new_padded_audio = new_padded_audio / np.max(np.abs(new_padded_audio))
        # Extraemos coeficientes MFCC
        mfcc_new_audio = extract_mfcc(new_padded_audio, sr).T
        # Adaptamos dimensiones del audio resultante a las requeridas por la RNN
        mfcc_new_audio = np.expand_dims(mfcc_new_audio, axis=0)  # (1, n_samples, n_features)
        # Realizamos predicciones en la RNN
        predicted_class = model.predict(mfcc_new_audio)
        predicted_emotion = label_encoder.inverse_transform([np.argmax(predicted_class)])
        emotions.append(predicted_class) # Añadimos la emoción predicha a la lista para este segmento
    
      # De las emociones obtenidas para el segmento calculamos su promedio y esa será la emoción que mostraremos: la más dominante.
      emotions = np.array(emotions)
      emotions = np.mean(emotions, axis=0)
      predicted_emotion = label_encoder.inverse_transform([np.argmax(emotions)])
      predicted_emotions.append(predicted_emotion)
      # print(f"La emoción predicha para el segmento: {segment} es: {predicted_emotion[0]}")
      # print(predicted_emotions)
   
    return predicted_emotions

def make_prediction(path):
    return get_results(path)







