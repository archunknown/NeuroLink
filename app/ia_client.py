import os
import json
import requests
# Borra o comenta la importación y la llamada a load_dotenv
# from dotenv import load_dotenv  
from .database import get_all_patients_as_dicts

# load_dotenv()  <-- BORRAR ESTO

def get_conversational_answer(user_query: str) -> str:
    """
    Obtiene una respuesta en lenguaje natural a una pregunta, basándose en 
    el contenido completo de la base de datos.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: La clave de API de Gemini no está configurada."

    # 1. Obtener todos los datos de la base de datos
    patients_data = get_all_patients_as_dicts()
    if not patients_data:
        return "No hay datos de pacientes en la base de datos para analizar."

    # 2. Preparar el contexto para la IA
    try:
        data_str = json.dumps(patients_data, indent=2, ensure_ascii=False)
    except TypeError as e:
        return f"Error al procesar los datos de los pacientes: {e}"

    system_prompt = f"""
    Eres un asistente de clínica amigable y servicial.
    Tu tarea es responder a la pregunta de un usuario basándote únicamente en los datos de pacientes que te proporciono en formato JSON.
    Analiza los datos para encontrar la respuesta correcta.
    Responde de forma amable, en español y en una sola frase o párrafo corto.
    Si la pregunta no se puede responder con los datos proporcionados, indica amablemente que no tienes esa información.
    No inventes información.
    Aunque el usuario escriba con mala ortografía, debes entender su intención.
    Si te preguntan por tu desarrollador, creador, etc. Diras que es Adrian Tasayco.

    --- DATOS DE PACIENTES (JSON) ---
    {data_str}
    --- FIN DE LOS DATOS ---
    """

    # 3. Llamar a la API de Google Gemini
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nPregunta del usuario: {user_query}"}]
            }]
        }

        response = requests.post(
            url=url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Error en la API de Gemini ({response.status_code}): {response.text}"

        data = response.json()
        
        # Extraer la respuesta del JSON de Gemini
        try:
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            return answer.strip()
        except (KeyError, IndexError):
            return "La IA no devolvió una respuesta válida."

    except requests.exceptions.RequestException as e:
        return f"Hubo un problema de conexión con la API: {e}"
    except Exception as e:
        return f"Ocurrió un error inesperado al contactar a la IA: {e}"
