import numpy as np
import os
import tensorflow as tf
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.config.set_visible_devices([], 'GPU')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = all messages, 1 = no info, 2 = no warnings, 3 = no errors

from flask import Flask, request, jsonify
import emotion_detection  # Tu archivo con el modelo de IA
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
  if 'audio' not in request.files:
      return jsonify({"error": "No se recibió ningún audio"}), 400

  audio_file = request.files['audio']
 
  try:
      # Llamar a la función que hace la predicción
      print("HOLA")
      emotion = emotion_detection.make_prediction(audio_file)

      print(f"HOLA DE VUELTA {emotion}")
      return jsonify({"emotion": emotion})
     
  except Exception as e:
      return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  
