import numpy as np
import os
from flask import Flask, request, jsonify
import emotion_detection  # Tu archivo con el modelo de IA
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
  if 'audio' not in request.files:
      return jsonify({"error": "No se recibió ningún audio"}), 400

  audio_file = request.files['audio']
  print(request.files)
  print(f"Archivo recibido: {audio_file.filename}")
  audio_file = request.files['audio']
 
  try:
      # Llamar a la función que hace la predicción
      emotion = emotion_detection.make_prediction(audio_file)
      print(f"emocion2 {emocion}")

      return jsonify({"emotion": emotion})
     
  except Exception as e:
      return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  
