import os
import json
import requests
from dotenv import load_dotenv
from .database import get_all_patients_as_dicts

load_dotenv()

def get_conversational_answer(user_query: str) -> str:
    """
    Obtiene una respuesta en lenguaje natural a una pregunta, basándose en 
    el contenido completo de la base de datos.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: La clave de API no está configurada."

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

    --- DATOS DE PACIENTES (JSON) ---
    {data_str}
    --- FIN DE LOS DATOS ---
    """

    # 3. Llamar a la API
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "alibaba/tongyi-deepresearch-30b-a3b:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ]
            },
            timeout=30  # Aumentado a 30s por si el prompt es grande
        )
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No se pudo generar una respuesta.").strip()

    except requests.exceptions.RequestException as e:
        return f"Hubo un problema de conexión con la API: {e}"
    except Exception as e:
        return f"Ocurrió un error inesperado al contactar a la IA: {e}"
