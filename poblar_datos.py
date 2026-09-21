"""
Script para poblar la base de datos con equipos y estadios de ejemplo.
Ejecuta: python poblar_datos.py
"""
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://usuario:password@cluster0.mongodb.net/copa_mundial_fifa?retryWrites=true&w=majority")

client = MongoClient(MONGO_URI)
db = client["copa_mundial_fifa"]

equipos = [
    {"nombre_equipo": "Argentina", "pais": "Argentina", "entrenador": "Lionel Scaloni", "grupo": "A"},
    {"nombre_equipo": "Brasil", "pais": "Brasil", "entrenador": "Dorival Júnior", "grupo": "A"},
    {"nombre_equipo": "Francia", "pais": "Francia", "entrenador": "Didier Deschamps", "grupo": "B"},
    {"nombre_equipo": "Alemania", "pais": "Alemania", "entrenador": "Julian Nagelsmann", "grupo": "B"},
    {"nombre_equipo": "España", "pais": "España", "entrenador": "Luis de la Fuente", "grupo": "C"},
    {"nombre_equipo": "México", "pais": "México", "entrenador": "Javier Aguirre", "grupo": "C"},
]

estadios = [
    {"nombre": "Estadio Azteca", "ciudad": "Ciudad de México", "pais": "México", "capacidad": 87000},
    {"nombre": "MetLife Stadium", "ciudad": "Nueva Jersey", "pais": "EE.UU.", "capacidad": 82500},
]

if db["equipos"].count_documents({}) == 0:
    db["equipos"].insert_many(equipos)
    print(f"Se insertaron {len(equipos)} equipos.")
else:
    print("Ya existen equipos, no se insertó nada.")

if db["estadios"].count_documents({}) == 0:
    db["estadios"].insert_many(estadios)
    print(f"Se insertaron {len(estadios)} estadios.")
else:
    print("Ya existen estadios, no se insertó nada.")

print("Listo. Ahora visita /setup-admin en tu navegador para crear el usuario administrador.")
