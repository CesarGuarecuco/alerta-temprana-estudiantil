"""Genera una base de estudiantes INVENTADA para la demostración.

Ningún dato corresponde a personas o instituciones reales. Las sedes,
carreras e identificadores son ficticios y se generan al azar con una
semilla fija para que el resultado sea reproducible.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
N_ESTUDIANTES = 1500
SEDES = ["Sede Norte", "Sede Centro", "Sede Sur", "Sede Costa"]
CARRERAS = [
    "Administración", "Contabilidad", "Enfermería (TENS)", "Informática",
    "Mecánica Automotriz", "Electricidad", "Educación Parvularia", "Turismo",
]


def generar(n: int = N_ESTUDIANTES, semilla: int = SEMILLA) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)

    sede = rng.choice(SEDES, n, p=[0.30, 0.35, 0.20, 0.15])
    carrera = rng.choice(CARRERAS, n)
    jornada = rng.choice(["Diurna", "Vespertina"], n, p=[0.6, 0.4])
    edad = np.clip(rng.normal(24, 6, n).round(), 17, 55).astype(int)
    edad = np.where(jornada == "Vespertina", edad + rng.integers(2, 8, n), edad)
    primera_generacion = rng.random(n) < 0.55
    trabaja = rng.random(n) < np.where(jornada == "Vespertina", 0.75, 0.30)
    gratuidad = rng.random(n) < 0.70

    # Indicadores académicos de las primeras 8 semanas del semestre
    asistencia = np.clip(rng.beta(8, 2, n) * 100 - trabaja * rng.uniform(0, 12, n), 20, 100).round(1)
    promedio = np.clip(rng.normal(4.9, 0.8, n) + (asistencia - 80) / 40, 1.0, 7.0).round(1)
    reprobadas = rng.poisson(np.clip((5.0 - promedio) * 0.9, 0.05, None))
    reprobadas = np.clip(reprobadas, 0, 6)
    cuotas_atrasadas = np.where(gratuidad, 0, rng.poisson(0.8, n))
    ingresos_plataforma = rng.poisson(np.clip(asistencia / 10, 1, None))
    tutorias = rng.poisson(0.6, n)

    # Probabilidad de abandono (modelo logístico inventado)
    z = (
        -2.9
        - 0.11 * (asistencia - 80)
        - 1.10 * (promedio - 4.8)
        + 0.70 * reprobadas
        + 0.60 * cuotas_atrasadas
        + 0.50 * trabaja
        + 0.35 * primera_generacion
        - 0.45 * tutorias
        - 0.06 * (ingresos_plataforma - 8)
        + 0.02 * (edad - 24)
    )
    prob = 1 / (1 + np.exp(-z))
    abandono = rng.random(n) < prob

    return pd.DataFrame({
        "id_estudiante": [f"EST-{i:05d}" for i in rng.permutation(np.arange(10001, 10001 + n))],
        "sede": sede,
        "carrera": carrera,
        "jornada": jornada,
        "edad": edad,
        "primera_generacion": primera_generacion.astype(int),
        "trabaja": trabaja.astype(int),
        "gratuidad": gratuidad.astype(int),
        "asistencia_pct": asistencia,
        "promedio_notas": promedio,
        "asignaturas_reprobadas": reprobadas,
        "cuotas_atrasadas": cuotas_atrasadas,
        "ingresos_plataforma_semana": ingresos_plataforma,
        "tutorias_asistidas": tutorias,
        "abandono": abandono.astype(int),
    })


if __name__ == "__main__":
    df = generar()
    salida = Path(__file__).parent / "datos" / "estudiantes_inventados.csv"
    salida.parent.mkdir(exist_ok=True)
    df.to_csv(salida, index=False)
    print(f"{len(df)} estudiantes inventados guardados en {salida}")
    print(f"Tasa de abandono: {df.abandono.mean():.1%}")
