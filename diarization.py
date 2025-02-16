# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 21:21:49 2024

@author: Kevin
"""

# Importamos librerías necesarias para la tarea de diarización
from pyAudioAnalysis import audioSegmentation
import numpy as np
import librosa
import os
import math
import whisper
import re
from sklearn.preprocessing import LabelEncoder
from scipy.stats import mode
import emotion_detection
import flask_file
import shutil
import soundfile as sf
      
# Definimos ruta del audio
audio_path = ""
y, sr = "", ""
speaker = 0

# Funcion para unir pequeños segmentos de audio
def join_audio_segments(time_list):
    for index in range (0, len(time_list)):
        if isinstance(time_list[index], tuple): # Verificamos que no sea un elemento eliminado
            if index + 1 <= len(time_list) - 1 and isinstance(time_list[index + 1], tuple):
                # Unimos dos segmentos si y solo si la diferencia de sus tiempos de fin e inicio
                # no superan los 1.5 segundos.
                # Esto implica que son el mismo segmento (continuación de la conversación)
                if time_list[index + 1][0] - time_list[index][1] < 1.5:
                    time_list[index] = (time_list[index][0], time_list[index + 1][1])
                    # Una vez unidos los segmentos, eliminamos el siguiente elemento 
                    # (pues ya fue unido al actual)
                    time_list[index + 1] = None

def remove_current_segments():
    SEGMENTS_PATH = r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\segmentos"
    # Verifica si la carpeta existe
    if not os.path.exists(SEGMENTS_PATH):
        return
    
    # Recorre todos los elementos dentro de la carpeta
    for file in os.listdir(SEGMENTS_PATH):
        file_path = os.path.join(SEGMENTS_PATH, file)
        
        if os.path.isfile(file_path) or os.path.islink(file_path):  # Si es un archivo o un enlace
            os.remove(file_path)
        elif os.path.isdir(file_path):  # Si es una carpeta
            shutil.rmtree(file_path)

# Funcion para crear subsegmentaciones pequeñas (de máximo 2.5 segundos) a cada segmentación
def make_segmentation(time_list):
    max_duration = 2.5  # Duración máxima de cada segmento en segundos
    i = 1
    pyAA_times_arr = []

    # Eliminamos segmentos generados previamente
    remove_current_segments()
    
    for m, (start, end) in enumerate(time_list):
        if speaker == 0:  # Filtramos solo segmentos del hablante 1
            # Guardamos SOLO audios cuya duración sea mayor a dos segundos
            # (donde es MÁS PROBABLE que no haya habido una segmentación por ruido u otros factores)
            if end - start >= 2:
                # print(math.ceil(start), math.ceil(end))
                pyAA_times_arr.append([math.ceil(start), math.ceil(end)])
                start_sample = int(start * sr)
                end_sample = int(end * sr)
    
                # Extraemos el segmento
                segment = y[start_sample:end_sample]
                duration = len(segment) / sr  # Duración del segmento en segundos
    
                # Dividimos segmento en partes de 2.5 segundos (que es el tamaño de audios máximo que nuestra RNN puede clasificar)
                num_parts = int(np.ceil(duration / max_duration))
                
                # Almacenamos cada segmentación en su propia carpeta
                output_folder = f"C:/Users/Kevin/Desktop/PROYECTO MODULAR/segmentos/segmento{i}"
                os.makedirs(output_folder, exist_ok=True)
    
                for j in range(num_parts):
                    part_start_sample = j * int(max_duration * sr)
                    part_end_sample = min((j + 1) * int(max_duration * sr), len(segment))
    
                    # Calculamos duración del segmento en segundos
                    duration_in_seconds = (part_end_sample - part_start_sample) / sr
                    # Filtramos segmentos mayores a 0.5 segundos
                    if duration_in_seconds > 0.5:
                        # Extraemos parte
                        part = segment[part_start_sample:part_end_sample]
    
                        output_path = f"{output_folder}/parte_{j+1}.wav"
                        sf.write(output_path, part, sr)
                        print(f"Segmento {i}, parte {j+1} guardado en {output_path}")
                i = i+1
                
    return pyAA_times_arr

# Crea la transcripción del audio
def make_transcription():
    # Definimos el modelo preentrenado "small" de Whisper para la tarea de transcripción de audio
    model = whisper.load_model("small")

    # Realizamos la transcripción del audio
    result = model.transcribe(audio_path, language="es", task="transcribe", verbose=True)

    # Creamos una lista con las segmentaciones del audio generadas por Whisper
    segments = result["segments"]
    # Guardamos cada transcripción de cada segmento en un archivo de texto
    with open(r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\transcripciones\transcripcion.txt", "w") as f:
        for segment in segments:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]
            f.write(f"[{start_time:.2f}s - {end_time:.2f}s]: {text}\n")
            
# Obtenemos el texto que mostraremos en la interfaz como resultados
def get_results(pyAA_times_arr):
    # Preprocesamiento del texto de transcripción de whisper
    whisper_times_arr = []
    whisper_text_arr = []
    with open(r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\transcripciones\transcripcion.txt", "r") as file:
        # Ejemplo de linea:
        # [29.00s - 30.00s]:  Sí, sí, sí.
        # Resultado esperado:
        # 29.00, 30.00
        # De modo que solo extraigamos los tiempos de cada linea de la transcripción leída
        for line in file:
            # Pasos:
            # Separamos tiempo del texto de la transcripción
            # Usamos expresion regular para eliminar corchetes de los intervalos de tiempo,
            # los espacios y las letras "s" de los tiempos
            newLine = line.split(":")
            text = re.sub(r"[\[\]s ]", "", newLine[0])
            # Resultado hasta el momento:
            # 29.00-30.00
            # Finalmente, separamos ambos tiempos y los metemos en una arreglo:
            text = text.split("-")
            whisper_times_arr.append(text)
            whisper_text_arr.append(newLine[1])

    # Asociamos segmentos de pyAudioAnalysis y whisper
    segmented_transcription = []
    whisper_text_index = 0
    text = ""
    for audio_index, (audio_start, audio_end) in enumerate(pyAA_times_arr):
        for transcription_index, (transcription_start, transcription_end) in enumerate(whisper_times_arr):
            if whisper_text_index < transcription_index: # Ignoramos la parte ya considerada en segmentos previos
                text = text + whisper_text_arr[transcription_index]
            
            # Identificamos posicion de cada elemento de pyAA_times_arr en whisper_times_arr
            if audio_end <= int(float(transcription_end)):
                segmented_transcription.append(text)
                # Reiniciamos variables
                text = ""
                whisper_text_index = transcription_index
                
                break

    segmented_transcription_text = ""
    #predicted_emotions = emotion_detection.make_prediction()
    
    # Buscamos la duracion máxima de los audios del dataset
    audio_duration = []
            
    # Convertimos listas a arreglos de numpy  
    y = np.array(["Enojo", 
                "Desagrado", 
                "Miedo", 
                "Felicidad", 
                "Neutral", 
                "Tristeza"])

    # Codificamos las etiquetas
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    predicted_emotions = []
    AUDIOS_PATH = r"C:\Users\Kevin\Desktop\PROYECTO MODULAR\segmentos"
    for folder in os.listdir(AUDIOS_PATH):
        emotions = [] # Almacenamos todas las emociones predichas para este segmento de audio
        segment = os.path.join(AUDIOS_PATH, folder)
        
        # Ciclo for que procesa cada audio en la carpeta especificada para el segmenti i-ésimo
        for audio in os.listdir(segment):
            audio_path = os.path.join(AUDIOS_PATH, folder, audio)
            # TRABAJO CON FLASK
            # Cada ruta de audio DEBE SER enviada al archivo flask_file.py,
            # de modo que, en ese archivo, se abra este audio y se envíe al servidor de IA
            # de Render.
            # Finalmente, este archivo flask_file.py retorna la respuesta a la emoción detectada
            # por el servidor de IA (que contiene el archivo emotion_detection.py)
            # predicted_class = flask_file.send_audio(audio_path)
            
            # with open(audio_path, 'rb') as audio_file:
                # predicted_class = emotion_detection.make_prediction(audio_file)
            
            predicted_class = flask_file.send_audio(audio_path)
            print(f"Emocion detectada: {predicted_class}")
                
            emotions.append(predicted_class['emotion']) # Añadimos la emoción predicha a la lista para este segmento

        # De las emociones obtenidas para el segmento calculamos su moda y esa será la emoción que mostraremos: la predominante.
        
        emotions = np.array(emotions)
        # print(f"emociones, no moda: {emotions}")
        unique_values, counts = np.unique(emotions, return_counts=True)
        mode_emotions = unique_values[np.argmax(counts)]
        # print(f"emociones, moda: {mode_emotions}")
        predicted_emotions.append(mode_emotions)
    
    for index, (start, end) in enumerate(pyAA_times_arr):
        segment = f"Segmento {index + 1} ({start}s - {end}s)"
        transcription_title = "Transcripción:"
        transcription_text = segmented_transcription[index]
        result = f"Emoción predominante detectada: {predicted_emotions[index]}"
        segmented_transcription_text = f"{segmented_transcription_text} <b>{segment}</b><br> <b>{transcription_title}</b><br> {transcription_text}<br> <b>{result}</b><br><br>"

    return segmented_transcription_text


# Realiza la diarización en el audio de entrada
def audio_diarization(selected_speaker, selected_audio_path):
    np.random.seed(42)  # Fijamos semilla para resultados deterministas
    global speaker, audio_path, y, sr
    speaker = selected_speaker
    audio_path = selected_audio_path
        
    y, sr = librosa.load(audio_path, sr=None) # Cargamos audio a memoria
    
    # Usamos el método speaker_diarization para esta tarea
    # En este método indicamos la ruta del audio y el número de hablantes en el audio (dos en este caso)
    # Finalmente, el método retorna tres parámetros, siendo "flags" el que contiene al hablante dominante en un segmento de audio determinado
    [speakers, classes, centers] = audioSegmentation.speaker_diarization(filename = audio_path, n_speakers = 2)
    
    # Imprimimos resultados
    # for segment, speaker in enumerate(speakers):
        # print(f"Segmento: {segment}, Hablante identificado: HABLANTE_{speaker}")
    
    # Obtener la duración en segundos
    audio_duration = librosa.get_duration(y=y, sr=sr)
    
    # print(f"Duración del audio: {audio_duration} segundos")
    
    segment_duration = audio_duration / len(speakers) # Obtenemos duración de cada segmento de audio
    # print(segment_duration)
    
    # Filtramos hablante de interes en la conversacion
    current_speaker = speakers[0]
    start_time_set = False
    times_arr = []
    
    for segment, speaker in enumerate(speakers):
        if speaker == current_speaker and start_time_set is False: # Tomamos todos los segmentos de audio correspondiente a este hablante hasta detectar un cambio de hablante
            start_time = segment * segment_duration # Obtenemos tiempo donde el hablador comienza
            start_time_set = True # Ya tenemos el tiempo donde comienza a hablar, no volver a calcular en la próxima iteración
    
        if speaker != current_speaker: # Se detectó un cambio de hablante, calcular fin de segmento
            end_time = segment * segment_duration # Obtenemos tiempo donde el hablador termina
            times_arr.append((start_time, end_time, current_speaker)) # Guardamos tiempos de inicio y fin y hablador
            current_speaker = speaker # Obtenemos hablante actual
            start_time_set = False # Reiniciamos variable para obtener el tiempo de inicio del siguiente hablante
    
    time_list = []
    for index, time in enumerate(times_arr):
        if(time[2] == 0):
          time_list.append((time[0], time[1]))
    
    # Unimos tantos segmentos como sea posible de acuerdo a la condición (end - start < 1.5)
    # llamando tantas veces como sea necesario a la función join_audio_segments
    join_audio_segments(time_list)
    
    while None in time_list:
        time_list = [item for item in time_list if item is not None] # Eliminamos todos los None de la lista
        join_audio_segments(time_list)   
        
    # Segmentamos los audios ya filtrados por hablante y duración
    pyAA_times_arr = make_segmentation(time_list)
    
    # Obtenemos la transcripción del audio
    make_transcription()
    
    # Una vez realizadas las segmentaciones, obtenemos los resultados
    return get_results(pyAA_times_arr)

# audio_diarization()




