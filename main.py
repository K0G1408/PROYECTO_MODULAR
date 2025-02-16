from PySide2.QtWidgets import QApplication, QMainWindow
import mainwindow, sys

app = QApplication()
window = mainwindow.MainWindow()
window.show()

sys.exit(app.exec_())

# Tareas pendientes:
    # 1) Conectar elementos de la interfaz:
        # 1.1) Elegir hablante y pasarlo dinámicamente de mainwindow.py a diarization.py
        # 1.2) Conectar archivos diarization.py con el archivo emotion_detection.py,
        #      de modo que se puedan detectar las emociones del audio seleccionado
        #      y obtener el resultado de manera dinámica (sadness, neutral, anger, etc.)
        
        # COMPLETADO
        
    # 2) Crear una base de datos simple para el sistema (base de datos para visualizar
    #    los resultados de análisis previos, sin necesidad de volver a procesar todo de nuevo)
    
    # Posible solucion: usar SQLite.
        # CARGAR RESULTADOS
        # De este modo, al presionar "cargar resultados", simplemente podemos mostrar un
        # listado de resultados almacenados en nuestra base de datos y dejar que el
        # usuario seleccione entre uno de ellos.
        # Finalmente, la carga de la información sería sencilla, pues es solo insertar textos
        # en pantalla.
        
        # GUARDAR RESULTADOS
        # Por otro lado, para guardar resultados es igualmente sencillo, simplemente debemos
        # almacenar algunos textos (nombre de proyecto, de audio, resultado, etc.) y permitir
        # al usuario elegir un nombre para identificar estos resultados en la base de datos,
        # de modo que, posteriormente, pueda cargarlos en CARGAR RESULTADOS.






