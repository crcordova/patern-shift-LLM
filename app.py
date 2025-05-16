import instructor
import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from validator import validar_turnos
import json

load_dotenv()

Turno = Literal["Morning", "Day", "Night", "Free"]

class Semana(BaseModel):
    dias: List[Turno] = Field(..., min_items=7, max_items=7)

class Turnos(BaseModel):
    semanas: List[Semana]

client = openai.OpenAI(
    # api_key=os.environ["GROQ_API_KEY"],
    # base_url="https://api.groq.com/openai/v1"
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

client = instructor.from_openai(client, mode=instructor.Mode.JSON)

prompt_inicial = """
            Quiero que generes un patrón de turnos válido para personal de una sala de urgencia.

            Los turnos posibles son: "Morning", "Day", "Night", "Free".
            Cada semana tiene 7 días, y cada persona debe trabajar 5 días por semana (es decir, 2 días deben ser "Free").

            Además debes seguir estar restricciones:
            - Máximo 5 días de trabajo por semana, es decir 5 turnos asignados por semana más los dos Free
            - En una semana solo se pueden usar dos tipos de turnos diferentes más "Free".
            - Los turnos "Night" deben estar agrupados en pares o tríos, nunca van solos. Después de un bloque de turnos "Night" debe haber un día "Free".
            - No puede haber más de 6 días consecutivos sin un free, esto aplica para las dos semanas(es decir, si la primera semana es ["Free","Morning", "Free", "Das", "Day", "Day", "Day"] el Free de la siguiente semana debe estar a más tarde el 3er día)
            - En un semana no puede tener más de 3 noches, máximo 3 no 4

            Devuelve los turnos en formato JSON como un objeto con la clave `semanas`, cuyo valor es una lista de semanas. 
            Cada semana debe ser un objeto con una lista de 7 valores en la clave `dias`. 
            Ejemplo de formato esperado:

            {
            "semanas": [
                {"dias": ["Morning", "Morning", "Free", "Day", "Day", "Day", "Free"]},
                {"dias": ["Night", "Night", "Free", "Morning", "Morning", "Free", "Free"]}
            ]
            }

            Genera turnos para 2 semanas.
            """
MAX_INTENTOS= 5
for intento in range(1, MAX_INTENTOS + 1):
    print(f"\n🧠 Intento {intento} generando turnos...")

    output = client.chat.completions.create(
        model="deepseek-coder-v2:16b",  
        response_model=Turnos,
        messages=[
            {
                "role": "user", 
                "content": prompt_inicial
            }
            ]
        )
    # 2. Validación
    semanas_raw = [semana.dias for semana in output.semanas]
    errores = validar_turnos(semanas_raw)

    if not errores:
        print("✅ Turnos válidos encontrados.")
        data_dict = output.model_dump()  
        with open("turnos_validos.json", "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
        print("Turnos guardados")
        break

    # 3. Si hay errores, prepara el feedback
    feedback = "\n".join(errores)
    print(f"❌ Errores encontrados:\n{feedback}")
    prompt_inicial = f"""
        Tuviste algunos errores al generar los turnos. Aquí están los detalles:

        {feedback}

        Por favor genera nuevamente el patrón completo para todas las semanas, asegurándote de cumplir con las restricciones anteriores y corregir estos errores.
        Formato esperado:
        {{
        "semanas": [
            {{"dias": ["Morning", "Morning", "Free", "Day", "Day", "Day", "Free"]}},
            ...
        # ]
        }}"""
else:
    print("❌ No se logró generar un patrón válido después de varios intentos.")
