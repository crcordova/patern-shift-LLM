from typing import List, Literal
from collections import Counter

Turno = Literal["Morning", "Day", "Night", "Free"]

def validar_semana(dias: List[Turno], semana_idx: int) -> List[str]:
    errores = []

    if len(dias) != 7:
        errores.append(f"Semana {semana_idx}: debe tener exactamente 7 días.")
        return errores

    # 1. Exactamente 5 turnos activos y 2 días "Free"
    cantidad_free = dias.count("Free")
    cantidad_activos = 7 - cantidad_free
    if cantidad_activos != 5:
        errores.append(f"Semana {semana_idx}: debe tener exactamente 5 turnos activos, tiene {cantidad_activos}.")
    if cantidad_free != 2:
        errores.append(f"Semana {semana_idx}: debe tener exactamente 2 días libres, tiene {cantidad_free}.")


    # 2. Solo 2 tipos de turnos activos distintos más 'Free'
    tipos_unicos = set(t for t in dias if t != "Free")
    if len(tipos_unicos) > 2:
        errores.append(f"Semana {semana_idx}: más de 2 tipos de turnos activos ({tipos_unicos}).")

    # 3 y 4. Turnos 'Night' en bloques válidos seguidos de 'Free'
    i = 0
    while i < len(dias):
        if dias[i] == "Night":
            bloque = 1
            while i + bloque < len(dias) and dias[i + bloque] == "Night":
                bloque += 1
            if bloque not in (2, 3):
                errores.append(f"Semana {semana_idx}: bloque de 'Night' inválido de longitud {bloque} en posición {i}.")
            fin_bloque = i + bloque
            if fin_bloque >= len(dias) or dias[fin_bloque] != "Free":
                errores.append(f"Semana {semana_idx}: bloque de 'Night' en posición {i} no seguido por 'Free'.")
            i = fin_bloque + 1
        else:
            i += 1

    return errores

def validar_turnos(semanas: List[List[Turno]]) -> List[str]:
    todos_errores = []
    for idx, semana in enumerate(semanas, start=1):
        errores = validar_semana(semana, idx)
        todos_errores.extend(errores)
    return todos_errores


def validar_turnos(semanas: List[List[Turno]]) -> List[str]:
    todos_errores = []
    for idx, semana in enumerate(semanas, start=1):
        errores = validar_semana(semana, idx)
        todos_errores.extend(errores)
    return todos_errores