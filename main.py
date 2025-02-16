from PySide2.QtWidgets import QApplication, QMainWindow
import mainwindow, sys

app = QApplication()
window = mainwindow.MainWindow()
window.show()

sys.exit(app.exec_())
