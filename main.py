from flask import Flask, request, jsonify
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import emotion_detection  # Tu archivo con el modelo de IA
app = Flask(__name__)

# Ruta para predicción de emociones
@app.route('/predict', methods=['POST'])
def predict():
    # Verificar si el archivo está en la solicitud
    if 'audio' not in request.files:
        return jsonify({'error': 'No se encontró el archivo de audio'}), 400

    # Obtener el archivo enviado
    audio_file = request.files['audio']

    # Guardar temporalmente el archivo
    audio_path = f"/tmp/{audio_file.filename}"
    audio_file.save(audio_path)

    # Usar tu modelo de IA para predecir emociones
    emotion = emotion_detection.make_prediction(audio_path)

    # Opcional: borrar el archivo después del procesamiento
    os.remove(audio_path)

    # Enviar la emoción detectada como respuesta
    return jsonify({'emotion': emotion})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

