from PySide2.QtWidgets import QMainWindow, QGraphicsScene, QFileDialog, QMessageBox, QTableWidgetItem, QTextEdit
from PySide2.QtCore import Slot, Qt, QStringListModel
from PySide2.QtGui import QFont
import os
import Ui_mainwindow, diarization, db
from PySide2.QtWidgets import QAbstractItemView


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Definimos objeto de interfaz de usuario
        self.ui = Ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Definimos variables
        self.ui.file_path = ""
        self.selected_project = ""
        self.any_changes = False
        
        # Creamos la base de datos si aún no existe
        db.make_database()
        
        # Mostramos listados de proyectos ya creados
        self.show_all_projects()
        
        # Asociamos función de abrir audio al botón
        self.ui.load_audio.triggered.connect(self.action_open_file)
        
        # Inicialmente algunos elementos de la interfaz están ocultos, hasta cargar
        # un nuevo audio (proyecto de análisis)
        self.ui.audio_name.hide()
        self.ui.label_1_speaker.hide()
        self.ui.label_2_speaker.hide()
        self.ui.comboBox.hide()
        self.ui.detect_emotions.hide()
        self.ui.textEdit.hide()
        self.ui.label_result.hide()
        self.ui.label_result_2.hide()
        
        # Definimos llamados a funciones cuando se hace click en los botones
        self.ui.detect_emotions.clicked.connect(self.detect_emotions)
        self.ui.save_project_btn.clicked.connect(self.save_project)
        self.ui.delete_project_btn.clicked.connect(self.delete_project)
        self.ui.saved_projects_list.clicked.connect(self.item_seleccionado)
        self.ui.load_project_list.clicked.connect(self.item_seleccionado)
        self.ui.load_project_btn.clicked.connect(self.load_projects)
        
        self.ui.saved_projects_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.load_project_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    # Muestra alertas en pantalla
    def show_message(self, msg1, msg2):
        if msg1 == "Error":
            QMessageBox.critical(
                self,
                msg1,
                msg2
            )
        else:
            QMessageBox.information(
                self,
                msg1,
                msg2
            )
    
    # Muestra preguntas en pantalla
    def show_question(self, msg1, msg2):
        response = QMessageBox.question(
            self,
            msg1,
            msg2,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # El valor por defecto si no se hace clic
        )
        
        return response # Retornamos la respuesta del usuario
    
    # Habilita y deshabilita ciertos textos en pantalla de inicio
    def hide_show_window_texts(self, start = False, enable_result_texts = False):
        if start:
            self.ui.audio_name.show()
            self.ui.label_1_speaker.show()
            self.ui.label_2_speaker.show()
            self.ui.comboBox.show()
            self.ui.detect_emotions.show()
            self.ui.start_text.hide()
        
        if enable_result_texts:
            self.ui.textEdit.show()
            self.ui.label_result.show()
            self.ui.label_result_2.show()
        
    # Indica que elemento está seleccionado de las listas
    def item_seleccionado(self, index):
        self.selected_project = self.model.data(index)
        
    # Muestra los proyectos creados
    def show_all_projects(self):
        self.model = QStringListModel()
        projects = db.load_all_projects()
        
        # Indicamos la lista de datos que será mostrada
        self.model.setStringList(projects)
        
        # Mostramos las listas
        self.ui.saved_projects_list.setModel(self.model)
        self.ui.load_project_list.setModel(self.model)
                
    # Nuevo proyecto
    # Función para cargar un nuevo audio
    @Slot()
    def action_open_file(self):
        # Obtenemos ruta de archivo
        self.ui.file_path = QFileDialog.getOpenFileName(
            self,
            'Selecciona el audio a analizar (extensión .wav)',
            '.',
            'wav (*.wav)'
        )[0]
        # Intentamos abrirlo para extraer su contenido
        if os.path.exists(self.ui.file_path):
            # El audio ya fue cargado, mostrar elementos ocultos
            self.ui.audio_name.setText(f"Analizando el audio: {os.path.basename(self.ui.file_path)}")
            
            self.hide_show_window_texts(start = True)
            
            self.show_message("Correcto",
                              "El audio se cargó correctamente.")
        else:
            self.show_message("Error",
                              f"Hubo un error al intentar abrir el archivo en la ruta: {self.ui.file_path}")

    # Función para detectar emociones en un audio
    @Slot()
    def detect_emotions(self):
        self.any_changes = True
        # Definimos fuente del texto y lo obtenemos del archivo diarization.py
        font = QFont()
        font.setPointSize(12)
        
        # Enviamos el hablante y la ruta seleccionados
        content = diarization.audio_diarization(self.ui.comboBox.currentIndex(), self.ui.file_path) 
       
        self.ui.textEdit.setFont(font)
        self.ui.textEdit.setHtml(content)
        self.hide_show_window_texts(enable_result_texts = True)
        
        self.show_message("Correcto",
                          "El análisis ha terminado.")
        
        print(self.ui.textEdit.toHtml())
    
    @Slot()
    # Guardar resultados
    def save_project(self):
        # Validamos si el input de nombre de proyecto está vacío o no
        project_name = str(self.ui.save_project_name.text())
        print(project_name)
    
        # Validamos si ya existe un proyecto con el nombre ingresado
        if db.check_project_name_exists(project_name):
            
            response = self.show_question("Alerta",
                                          "Ya existe un proyecto con ese nombre, ¿deseas reemplazarlo?")
            
            if response == QMessageBox.Yes:
                if self.ui.textEdit.toPlainText() != "":
                    db.replace_project(
                        self.ui.file_path,
                        project_name,
                        self.ui.comboBox.currentIndex(), 
                        self.ui.textEdit.toHtml()
                    )
                    
                    self.show_message("Correcto",
                                      "El proyecto se guardó correctamente.")
                else:
                    # Mostramos alerta de creación de proyecto correcta
                    self.show_message("Error",
                                      "Aún no se ha realizado ningún análisis en este proyecto.")
        
        # Validamos si el campo de nombre de proyecto está vacío
        elif str(project_name) == "":
            self.show_message("Error",
                              "Primero debes ingresar un nombre de proyecto.")
        
        # Todo está correcto, guardar proyecto
        else:
            if self.ui.textEdit.toPlainText() != "":
                db.new_project(
                    self.ui.file_path,
                    project_name,
                    self.ui.comboBox.currentIndex(),
                    self.ui.textEdit.toHtml()
                )
                
                self.show_message("Correcto",
                                  "El proyecto se guardó correctamente.")
                
                self.show_all_projects() # Actualizamos listados de proyectos
            else:
                # Mostramos alerta de creación de proyecto correcta
                self.show_message("Error",
                                  "Aún no se ha realizado ningún análisis en este proyecto.")
                        
    @Slot()
    # Guardar resultados
    def delete_project(self):
        if self.ui.load_project_input.text() != "":
            
            response = self.show_question("Eliminar proyecto",
                                          f"¿Estás seguro que deseas eliminar el proyecto {self.ui.load_project_input.text()}?")
            
            if response == QMessageBox.Yes:
                project_name = self.ui.load_project_input.text()
                if db.delete_project(project_name):
                    self.show_message("Correcto", f"El proyecto: {project_name} ha sido eliminado correctamente.")
                    self.show_all_projects() # Actualizamos listados de proyectos
                    
                else:
                    self.show_message("Error", f"El proyecto: {project_name} no existe.")
        
        elif self.selected_project != "":
            response = self.show_question("Eliminar proyecto",
                                          f"¿Estás seguro que deseas eliminar el proyecto {self.selected_project}?")
                        
            if response == QMessageBox.Yes:
                if db.delete_project(self.selected_project):
                    self.show_message("Correcto", f"El proyecto: {self.selected_project} ha sido eliminado correctamente.")
                    self.show_all_projects() # Actualizamos listados de proyectos
                    
                else:
                    self.show_message("Error", f"El proyecto: {self.selected_project} no existe.")
        else:
            self.show_message("Error", "Primero debes seleccionar un proyecto")
            
    # Carga un proyecto individual
    def load_project(self, project_name):
        # Trae la informacion del proyecto de la base de datos
        project_info = db.load_project(project_name)
        
        if project_info is not None:
            # Actualiza textos en pantalla con la información del proyecto cargado
            self.ui.audio_name.setText(f"Analizando el audio: {os.path.basename(project_info[1])}")
            self.ui.comboBox.setCurrentIndex(project_info[3])
            font = QFont()
            font.setPointSize(12)
            self.ui.textEdit.setFont(font)
            self.ui.textEdit.setHtml(project_info[4])
            self.hide_show_window_texts(start = True, enable_result_texts = True)
            self.ui.file_path = project_info[1]
            
            # Finalmente, redirige al usuario a la ventana principal
            self.ui.tabWidget.setCurrentIndex(0)
            
        else:
            self.show_message("Error", f"El proyecto {project_name} no existe.")
            
        
    def load_project_cases(self):
        if self.ui.load_project_input.text() != "":
            # Simplemente cargamos proyecto desde el input
            self.load_project(self.ui.load_project_input.text())
            
        elif self.selected_project != "":
            # Simplemente cargamos proyecto desde el listado
            self.load_project(self.selected_project)
        
        else:
            self.show_message("Error", "Primero debes seleccionar un proyecto")
    
    # Carga proyectos: considera todos los casos posibles de cargado
    @Slot()
    def load_projects(self):
        # Validamos si se han realizado cambios en el proyecto actual
        if self.any_changes:
            # Sí se han realizado cambios, preguntar si desea guardarlos primero
                
            response = self.show_question("Guardar proyecto",
                                          "Ya tienes un proyecto cargado, ¿deseas guardar cambios antes de cargar otro?")
            
            if response == QMessageBox.Yes: # Desea guardar proyecto actual
                # Redirigimos al usuario a la ventana de guardar proyecto
                self.ui.tabWidget.setCurrentIndex(1)
                
            else: # No desea guardar proyecto actual
                self.load_project_cases()
                    
        else: # No existe ningun proyecto cargado, simplemente cargar proyecto de acuerdo a los casos posibles
            self.load_project_cases()
                









