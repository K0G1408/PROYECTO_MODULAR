import sqlite3

def make_database():
    # Definimos la conexión a la base de datos (se crea si no existe)
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()

    # Creamos la tabla para guardar resultados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_path TEXT NOT NULL,
            project_name TEXT NOT NULL,
            selected_speaker INTEGER NOT NULL,
            analysis_result TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def new_project(audio_path, project_name, selected_speaker, analysis_result):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO results (audio_path, project_name, selected_speaker, analysis_result)
        VALUES (?, ?, ?, ?)
    ''', (audio_path, project_name, selected_speaker, analysis_result, ))
    
    conn.commit()
    conn.close()
    
def check_project_name_exists(project_name):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    # Verificamos si el proyecto existe
    cursor.execute('SELECT project_name FROM results WHERE project_name = ?', (project_name,))
    
    result = cursor.fetchone()  # fetchone obtiene la primera fila de resultados
    conn.close()
    
    # Si result no es None, significa que existe el proyecto con ese nombre
    return result is not None

def load_all_projects():
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT project_name FROM results')
    projects = [row[0] for row in cursor.fetchall()] # Obtenemos una lista con los nombres de proyecto
    
    conn.close()
    
    return projects
    
def load_project(project_name):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM results WHERE project_name = ?', (project_name, ))
    project = cursor.fetchone()
    
    conn.close()
    return project

def delete_project(project_name):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    # Intentamos eliminar el proyecto con tal ID
    cursor.execute('DELETE FROM results WHERE project_name = ?', (project_name, ))
    
    # Verificamos que el proyecto fue eliminado
    if cursor.rowcount > 0:
        # Guardar los cambios
        conn.commit()
        deleted = True
        
    else:
        deleted = False
    
    
    conn.close()
    
    return deleted

def replace_project(audio_path, project_name, selected_speaker, analysis_result):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE results
        SET audio_path = ?, project_name = ?, selected_speaker = ?, analysis_result = ?
        WHERE project_name = ?
    ''', (audio_path, project_name, selected_speaker, analysis_result, project_name))
    
    conn.commit()
    conn.close()
    


    











