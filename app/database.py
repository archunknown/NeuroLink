import sqlite3
from pathlib import Path

# Obtener la ruta de la base de datos en la raíz del proyecto
DB_PATH = Path(__file__).parent.parent / 'neuro.db'

def connect_db():
    """Conectar a la base de datos SQLite"""
    conn = sqlite3.connect(str(DB_PATH))
    return conn

def create_patient_table():
    """Crear la tabla de pacientes si no existe"""
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT UNIQUE NOT NULL,
        nombres TEXT NOT NULL,
        apellido_paterno TEXT NOT NULL,
        apellido_materno TEXT NOT NULL,
        edad INTEGER NOT NULL,
        sintomas TEXT NOT NULL,
        urgencia TEXT NOT NULL,
        direccion TEXT,
        distrito TEXT,
        provincia TEXT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def insert_patient(dni, nombres, apellido_paterno, apellido_materno, age, symptoms, urgency, direccion, distrito, provincia):
    """Insertar un nuevo paciente en la base de datos"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO pacientes (dni, nombres, apellido_paterno, apellido_materno, edad, sintomas, urgencia, direccion, distrito, provincia) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dni, nombres, apellido_paterno, apellido_materno, int(age), symptoms, urgency, direccion, distrito, provincia))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al insertar paciente: {e}")
        return False

def get_all_patients():
    """Obtener todos los pacientes ordenados por fecha descendente"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT id, dni, nombres, apellido_paterno, apellido_materno, edad, sintomas, urgencia, fecha, direccion, distrito, provincia FROM pacientes ORDER BY fecha DESC")
        patients = c.fetchall()
        conn.close()
        return patients
    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        return []

def get_patient_by_id(patient_id):
    """Obtener un paciente específico por ID"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT id, dni, nombres, apellido_paterno, apellido_materno, edad, sintomas, urgencia, fecha, direccion, distrito, provincia FROM pacientes WHERE id = ?", (patient_id,))
        patient = c.fetchone()
        conn.close()
        return patient
    except Exception as e:
        print(f"Error al obtener paciente: {e}")
        return None

def update_patient_urgency(patient_id, urgency):
    """Actualizar la urgencia de un paciente"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("UPDATE pacientes SET urgencia = ? WHERE id = ?", (urgency, patient_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar paciente: {e}")
        return False


def delete_patient(patient_id):
    """Eliminar un paciente de la base de datos"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("DELETE FROM pacientes WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al eliminar paciente: {e}")
        return False

def get_patient_by_dni(dni):
    """Obtener un paciente específico por DNI"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM pacientes WHERE dni = ?", (dni,))
        patient = c.fetchone()
        conn.close()
        return patient
    except Exception as e:
        print(f"Error al obtener paciente por DNI: {e}")
        return None

def get_all_patients_as_dicts():
    """Obtener todos los pacientes como una lista de diccionarios."""
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, dni, nombres, apellido_paterno, apellido_materno, edad, sintomas, urgencia, fecha, direccion, distrito, provincia FROM pacientes ORDER BY fecha DESC")
        patients = [dict(row) for row in c.fetchall()]
        conn.close()
        return patients
    except Exception as e:
        print(f"Error al obtener pacientes como dicts: {e}")
        return []

def execute_query(sql_query, params=()):
    """Ejecuta una consulta SQL de solo lectura y devuelve los resultados."""
    if not sql_query.strip().lower().startswith('select'):
        print(f"Error de seguridad: Se intentó ejecutar una consulta no permitida: {sql_query}")
        return None, None
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute(sql_query, params)
        headers = [description[0] for description in c.description] if c.description else []
        rows = c.fetchall()
        conn.close()
        return headers, rows
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None, None