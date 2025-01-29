from flask import Flask, request, jsonify
import os
import librosa
from io import BytesIO
import numpy as np
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import emotion_detection  # Tu archivo con el modelo de IA
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    # Obtén el archivo correctamente
    audio_file = request.files['audio']  # Esto debería ser un archivo binario
    print(request.files)
    print(f"Archivo recibido: {audio_file.filename}")
    try:
        # Cargar audio desde el archivo recibido
        audio_data, sr = librosa.load(BytesIO(audio_file.read()))
        print(f"Audio cargado: {audio_file.filename}")
        
        # Llamar a la función que hace la predicción
        emotion = emotion_detection.make_prediction(audio_data)
        
        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

