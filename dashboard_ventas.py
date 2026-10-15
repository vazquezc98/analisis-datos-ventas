# -*- coding: utf-8 -*-
"""Genera un dashboard web interactivo (HTML) con Plotly + pandas a partir de ventas.csv."""

import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(CARPETA, "ventas.csv")
RUTA_HTML = os.path.join(CARPETA, "dashboard_cliente.html")

# ---------- Datos ----------
df = pd.read_csv(RUTA_CSV)
df["fecha"] = pd.to_datetime(df["fecha"])
df["ventas"] = (df["precio"] * df["cantidad"]).round(2)
df["fecha_str"] = df["fecha"].dt.strftime("%Y-%m-%d")

# KPIs
ventas_totales = df["ventas"].sum()
ticket_promedio = df["ventas"].mean()
unidades = df["cantidad"].sum()

# ---------- Figuras Plotly ----------
fig_cat = px.bar(
    df.groupby("categoria", as_index=False)["ventas"].sum().sort_values("ventas", ascending=False),
    x="categoria", y="ventas", color="categoria",
    title="Ventas totales por categoría",
    labels={"categoria": "Categoría", "ventas": "Ventas ($)"},
    text_auto=".2s",
)
fig_cat.update_layout(showlegend=False, height=420, margin=dict(l=20, r=20, t=50, b=20))

top_prod = (
    df.groupby("producto", as_index=False)["cantidad"].sum()
    .sort_values("cantidad", ascending=True).tail(10)
)
fig_prod = px.bar(
    top_prod, x="cantidad", y="producto", orientation="h", color="cantidad",
    color_continuous_scale="Teal", title="Top 10 productos más vendidos (unidades)",
    labels={"cantidad": "Unidades", "producto": "Producto"},
    text="cantidad",
)
fig_prod.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20), coloraxis_showscale=False)

ventas_mes = df.set_index("fecha")["ventas"].resample("ME").sum().reset_index()
fig_tend = px.line(
    ventas_mes, x="fecha", y="ventas", markers=True,
    title="Tendencia de ventas mensuales",
    labels={"fecha": "Mes", "ventas": "Ventas ($)"},
)
fig_tend.update_traces(line_color="#2a9d8f", fill="tozeroy", fillcolor="rgba(42,157,143,0.15)")
fig_tend.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20))

# HTML fragments (sin plotly.js, se carga por CDN)
cat_html = fig_cat.to_html(full_html=False, include_plotlyjs=False, div_id="grafico-categoria")
prod_html = fig_prod.to_html(full_html=False, include_plotlyjs=False, div_id="grafico-productos")
tend_html = fig_tend.to_html(full_html=False, include_plotlyjs=False, div_id="grafico-tendencia")

# Datos para la tabla (JSON)
cols_tabla = ["fecha_str", "producto", "categoria", "precio", "cantidad", "cliente", "ventas"]
tabla_records = df[cols_tabla].rename(columns={"fecha_str": "fecha"}).to_dict(orient="records")
tabla_json = json.dumps(tabla_records, ensure_ascii=False)

# Categorías para filtro
categorias = sorted(df["categoria"].unique().tolist())

plantilla = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard de Ventas</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ background:#f4f6f9; font-family: 'Segoe UI', sans-serif; }}
    .kpi-card {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
    .kpi-title {{ color:#6c757d; font-size:.9rem; margin:0; }}
    .kpi-value {{ font-size:1.8rem; font-weight:700; color:#2a9d8f; margin:4px 0 0; }}
    .chart-card {{ background:#fff; border-radius:12px; padding:12px; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
    .section-title {{ margin: 24px 0 12px; font-weight:600; color:#343a40; }}
    footer {{ text-align:center; color:#999; padding:20px; font-size:.85rem; }}
  </style>
</head>
<body>
<div class="container-fluid py-4 px-4">

  <h2 class="mb-1">📊 Dashboard de Ventas — Tienda</h2>
  <p class="text-muted mb-4">Análisis interactivo: KPIs, gráficos y tabla exploratoria</p>

  <!-- KPIs -->
  <div class="row g-3 mb-2">
    <div class="col-md-4">
      <div class="kpi-card">
        <p class="kpi-title">💰 Ventas totales</p>
        <p class="kpi-value">${ventas_totales:,.2f}</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="kpi-card">
        <p class="kpi-title">🧾 Ticket promedio</p>
        <p class="kpi-value">${ticket_promedio:,.2f}</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="kpi-card">
        <p class="kpi-title">📦 Unidades vendidas</p>
        <p class="kpi-value">{unidades:,.0f}</p>
      </div>
    </div>
  </div>

  <!-- Gráficos -->
  <h4 class="section-title">Gráficos interactivos</h4>
  <div class="row g-3">
    <div class="col-lg-6"><div class="chart-card">{cat_html}</div></div>
    <div class="col-lg-6"><div class="chart-card">{prod_html}</div></div>
    <div class="col-12"><div class="chart-card">{tend_html}</div></div>
  </div>

  <!-- Tabla -->
  <h4 class="section-title">Explorador de ventas</h4>
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="row g-2 mb-3 align-items-end">
        <div class="col-md-4">
          <label class="form-label mb-1">Filtrar por categoría</label>
          <select id="filtro-categoria" class="form-select">
            <option value="">Todas</option>
            {''.join(f'<option value="{c}">{c}</option>' for c in categorias)}
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label mb-1">Buscador (producto/cliente)</label>
          <input id="buscador" type="text" class="form-control" placeholder="Escribe para buscar…">
        </div>
        <div class="col-md-4">
          <label class="form-label mb-1">Registros por página</label>
          <select id="page-len" class="form-select">
            <option value="10">10</option>
            <option value="25" selected>25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
      <table id="tabla-ventas" class="table table-striped table-hover" style="width:100%">
        <thead>
          <tr>
            <th>Fecha</th><th>Producto</th><th>Categoría</th>
            <th>Precio</th><th>Cantidad</th><th>Cliente</th><th>Ventas</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <footer>Generado con Python · Plotly · pandas · DataTables</footer>
</div>

<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>
<script>
  const datos = {tabla_json};
  let tabla = null;

  function renderTabla() {{
    if (tabla) tabla.destroy();
    tabla = $('#tabla-ventas').DataTable({{
      data: datos,
      columns: [
        {{ data: 'fecha' }},
        {{ data: 'producto' }},
        {{ data: 'categoria' }},
        {{ data: 'precio', render: d => '$' + Number(d).toFixed(2) }},
        {{ data: 'cantidad' }},
        {{ data: 'cliente' }},
        {{ data: 'ventas', render: d => '$' + Number(d).toFixed(2) }}
      ],
      pageLength: 25,
      lengthChange: false,
      language: {{
        search: "Buscar:",
        lengthMenu: "Mostrar _MENU_",
        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
        paginate: {{ first:"Primero", last:"Último", next:"Siguiente", previous:"Anterior" }},
        zeroRecords: "Sin resultados",
        emptyTable: "Sin datos"
      }},
      dom: 'rtip'
    }});
  }}

  $(document).ready(function() {{
    renderTabla();

    // Buscador externo
    $('#buscador').on('keyup change', function() {{
      tabla.search(this.value).draw();
    }});

    // Filtro por categoría (columna índice 2)
    $('#filtro-categoria').on('change', function() {{
      const val = this.value;
      tabla.column(2).search(val ? '^' + val + '$' : '', true, false).draw();
    }});

    // Registros por página
    $('#page-len').on('change', function() {{
      tabla.page.len(parseInt(this.value)).draw();
    }});
  }});
</script>
</body>
</html>
"""

with open(RUTA_HTML, "w", encoding="utf-8") as f:
    f.write(plantilla)

print(f"Dashboard generado: {RUTA_HTML}")
print(f"KPIs: ventas_totales=${ventas_totales:,.2f} | ticket_promedio=${ticket_promedio:,.2f} | unidades={unidades:,.0f}")
