# -*- coding: utf-8 -*-
"""Analiza ventas.csv y genera gráficos de ventas por categoría, productos más vendidos y tendencia."""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Backend sin pantalla
import matplotlib.pyplot as plt
import seaborn as sns

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(CARPETA, "ventas.csv")

# ---------- Carga y preparación ----------
df = pd.read_csv(RUTA_CSV)
df["fecha"] = pd.to_datetime(df["fecha"])
df["ventas"] = df["precio"] * df["cantidad"]

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 120

# ---------- 1. Ventas totales por categoría ----------
ventas_cat = df.groupby("categoria", as_index=False)["ventas"].sum().sort_values("ventas", ascending=False)

fig, ax = plt.subplots(figsize=(9, 6))
sns.barplot(data=ventas_cat, x="categoria", y="ventas", hue="categoria", ax=ax, palette="viridis", legend=False)
ax.set_title("Ventas totales por categoría", fontsize=14, fontweight="bold")
ax.set_xlabel("Categoría")
ax.set_ylabel("Ventas ($)")
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=3, fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(CARPETA, "ventas_por_categoria.png"))
plt.close(fig)
print("Guardado: ventas_por_categoria.png")

# ---------- 2. Productos más vendidos (por cantidad) ----------
productos_top = (
    df.groupby("producto", as_index=False)["cantidad"]
    .sum()
    .sort_values("cantidad", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(9, 6))
sns.barplot(data=productos_top, x="cantidad", y="producto", hue="producto", ax=ax, palette="mako", legend=False)
ax.set_title("Top 10 productos más vendidos (unidades)", fontsize=14, fontweight="bold")
ax.set_xlabel("Cantidad vendida")
ax.set_ylabel("Producto")
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=3, fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(CARPETA, "productos_mas_vendidos.png"))
plt.close(fig)
print("Guardado: productos_mas_vendidos.png")

# ---------- 3. Tendencia de ventas (mensual) ----------
ventas_mes = df.set_index("fecha")["ventas"].resample("ME").sum()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ventas_mes.index, ventas_mes.values, marker="o", color="#2a9d8f", linewidth=2)
ax.fill_between(ventas_mes.index, ventas_mes.values, alpha=0.15, color="#2a9d8f")
ax.set_title("Tendencia de ventas mensuales", fontsize=14, fontweight="bold")
ax.set_xlabel("Mes")
ax.set_ylabel("Ventas ($)")
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
fig.savefig(os.path.join(CARPETA, "tendencia_ventas.png"))
plt.close(fig)
print("Guardado: tendencia_ventas.png")

# ---------- Resumen ----------
print("\n===== RESUMEN =====")
print(f"Filas analizadas: {len(df)}")
print(f"Ventas totales: ${df['ventas'].sum():,.2f}")
print(f"Ticket promedio: ${df['ventas'].mean():,.2f}")
print(f"Unidades vendidas: {df['cantidad'].sum():,.0f}")
print("\nVentas por categoría:")
print(ventas_cat.to_string(index=False))
print("\nTop 3 productos (unidades):")
print(productos_top.head(3).to_string(index=False))
