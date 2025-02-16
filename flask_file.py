import requests

# URL del servidor Flask (ajústalo según tu configuración)
SERVER_URL = "https://proyectomodular-production-cdbb.up.railway.app/predict"

# Función para enviar un archivo de audio
def send_audio(audio_path):
    # Abrir el archivo de audio
    with open(audio_path, 'rb') as audio_file:
        # Crear una solicitud POST con el archivo
        files = {'audio': audio_file}
        response = requests.post(SERVER_URL, files=files)
        print("Archivo recibido")

    # Procesar la respuesta
    if response.status_code == 200:
        print(f"Emoción detectada: {response.json()}")
        return response.json()
    else:
        print(f"Error: {response.json()['error']}")









