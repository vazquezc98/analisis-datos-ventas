# -*- coding: utf-8 -*-
"""Genera datos sintéticos de ventas para la tienda y los exporta a ventas.csv."""

import random
import csv
from datetime import date, timedelta

random.seed(42)

# Catálogo: producto -> (categoria, precio_base)
catalogo = {
    "Laptop": ("Electrónica", 1200.0),
    "Smartphone": ("Electrónica", 800.0),
    "Auriculares": ("Electrónica", 120.0),
    "Camisa": ("Ropa", 35.0),
    "Pantalón": ("Ropa", 50.0),
    "Chaqueta": ("Ropa", 90.0),
    "Arroz 5kg": ("Alimentos", 12.0),
    "Aceite 1L": ("Alimentos", 6.5),
    "Café 500g": ("Alimentos", 8.0),
    "Lámpara": ("Hogar", 45.0),
    "Silla": ("Hogar", 75.0),
    "Mesa": ("Hogar", 200.0),
    "Pelota": ("Deportes", 25.0),
    "Raqueta": ("Deportes", 60.0),
    "Zapatillas": ("Deportes", 110.0),
}

productos = list(catalogo.keys())
clientes = [f"Cliente_{i:03d}" for i in range(1, 51)]

inicio = date(2025, 1, 1)
fin = date(2025, 12, 31)
rango_dias = (fin - inicio).days

filas = []
for _ in range(500):
    producto = random.choice(productos)
    categoria, precio_base = catalogo[producto]
    # Variación de precio ±10 %
    precio = round(precio_base * random.uniform(0.9, 1.1), 2)
    cantidad = random.randint(1, 10)
    fecha = inicio + timedelta(days=random.randint(0, rango_dias))
    cliente = random.choice(clientes)
    filas.append([fecha.isoformat(), producto, categoria, precio, cantidad, cliente])

# Mezclar para que no estén ordenadas
random.shuffle(filas)

ruta = "/home/cvazquez/cesar/opencode/analisis-datos-proyectos/ventas.csv"
with open(ruta, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["fecha", "producto", "categoria", "precio", "cantidad", "cliente"])
    writer.writerows(filas)

print(f"Generadas {len(filas)} filas en {ruta}")
