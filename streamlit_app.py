import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from glob import glob
from utils import data_curvas, maximo_lc

# Constante para cortar en fase
FASE_MAX = 50

# Rutas relativas
path_real = "data/real"

# Orden físico de filtros conocidos en astronomía
orden_filtros = ['U', 'B', 'V', 'R', 'I', 'g', 'r', 'i', 'z']
orden_dict = {f: i for i, f in enumerate(orden_filtros)}

def nombre_base(nombre_archivo):
    return os.path.basename(nombre_archivo).split('_')[0]

def calcular_curvas_color(FILTROS, filtros):
    curvas_color = {}
    n = len(filtros)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            f1, f2 = filtros[i].strip(), filtros[j].strip()
            if f1 not in orden_dict or f2 not in orden_dict:
                continue
            if orden_dict[f1] >= orden_dict[f2]:
                continue
            t1, m1 = FILTROS[i][0], FILTROS[i][1]
            t2, m2 = FILTROS[j][0], FILTROS[j][1]
            tiempos_comunes = np.intersect1d(t1, t2)
            if len(tiempos_comunes) == 0:
                continue
            m1_interp = np.interp(tiempos_comunes, t1, m1)
            m2_interp = np.interp(tiempos_comunes, t2, m2)
            color = m1_interp - m2_interp
            curvas_color[f"{f1}-{f2}"] = (tiempos_comunes, color)
    return curvas_color

# ---------------- Streamlit UI ------------------
st.set_page_config(layout="wide")
st.title("Curvas de Color - SN Tipo Ibc")

st.markdown("""
Esta aplicación permite visualizar curvas de color generadas a partir de curvas de luz reales y extendidas (por PCA) de supernovas tipo Ibc.

**Tipos de datos disponibles:**
- **Curvas PCA**: Curvas de color generadas a partir de fotometría extendida usando análisis de componentes principales (PCA)
- **Curvas Sintéticas Mangleadas**: Curvas de color generadas a partir de fotometría sintética derivada de espectros

- Selecciona un **color** (ej: B‒V, g‒r) en el desplegable para mostrar sus curvas.
- Las **curvas reales** se muestran en gris (baja opacidad), ocultas por defecto.
- Las **curvas reales dentro de una curva extendida** se muestran en azul.
- Los **puntos extrapolados** (que sólo están en la curva PCA) se muestran en rojo con símbolo `x`.
- Puedes activar o desactivar curvas específicas desde la **leyenda**.
- Puedes seleccionar el tipo de datos a visualizar: **PCA** o **Sintéticas Mangleadas**.
- Las curvas de color de las mangleadas sinteticas se muestran en rojo `x` al seleccionar el tipo de datos "Sintéticas Mangleadas".
""")

# Selector de tipo de datos
tipo_datos = st.radio(
    "Selecciona el tipo de datos:",
    ["PCA", "Sintéticas Mangleadas"],
    index=1
)

# Determinar la ruta según la selección
if tipo_datos == "PCA":
    path_pca = "data/pca"
else:
    path_pca = "data/sintetica_mangleada"

# Reinicializar las listas para cada ejecución
trazas = []
colores_disponibles = set()

# Cargar curvas reales
archivos_real = glob(os.path.join(path_real, '*.dat'))
for archivo_real in archivos_real:
    nombre_sn = nombre_base(archivo_real)
    if nombre_sn == "SN1999dn":
        continue
    FILTROS_real, filtros_real = data_curvas(archivo_real)
    try:
        tmax = float(maximo_lc("Ibc", nombre_sn))
        for k in range(len(FILTROS_real)):
            FILTROS_real[k][0] = FILTROS_real[k][0] - tmax
    except:
        continue
    curvas_real = calcular_curvas_color(FILTROS_real, filtros_real)
    for color_name in curvas_real:
        t_real, col_real = curvas_real[color_name]
        mask = t_real <= FASE_MAX
        colores_disponibles.add(color_name)
        trazas.append(go.Scatter(
            x=t_real[mask],
            y=col_real[mask],
            mode='markers',
            marker=dict(color='gray', symbol='circle', opacity=0.5),
            name=f"{nombre_sn} {color_name} (real)",
            legendgroup=f"real_{color_name}",
            visible='legendonly'
        ))

# Cargar curvas PCA
archivos_pca = glob(os.path.join(path_pca, '*.dat'))
for archivo_pca in archivos_pca:
    nombre_sn = nombre_base(archivo_pca)
    if nombre_sn == "SN1999dn":
        continue
    path_real_file = os.path.join(path_real, f"{nombre_sn}_photometry.dat")
    FILTROS_pca, filtros_pca = data_curvas(archivo_pca)
    try:
        tmax = 0  # maximo_lc("Ibc", nombre_sn) si lo necesitas
        for k in range(len(FILTROS_pca)):
            FILTROS_pca[k][0] = FILTROS_pca[k][0] - tmax
    except:
        continue
    curvas_pca = calcular_curvas_color(FILTROS_pca, filtros_pca)
    if os.path.exists(path_real_file):
        FILTROS_real, filtros_real = data_curvas(path_real_file)
        if nombre_sn != "SN1999dn":
            for k in range(len(FILTROS_real)):
                FILTROS_real[k][0] = FILTROS_real[k][0] - tmax
        curvas_real = calcular_curvas_color(FILTROS_real, filtros_real)
    else:
        curvas_real = {}
    for color_name in curvas_pca:
        t_pca, col_pca = curvas_pca[color_name]
        colores_disponibles.add(color_name)
        t_real, col_real = curvas_real.get(color_name, ([], []))
        fases_reales = set(np.round(t_real, 3))
        fases_pca = np.round(t_pca, 3)
        mask_real = np.array([fase in fases_reales for fase in fases_pca])
        mask_ext = ~mask_real

        # Aplicar filtro de fase
        mask_real_filtro = mask_real & (t_pca <= FASE_MAX)
        mask_ext_filtro = mask_ext & (t_pca <= FASE_MAX)

        trazas.append(go.Scatter(
            x=t_pca[mask_real_filtro],
            y=col_pca[mask_real_filtro],
            mode='markers',
            marker=dict(color='blue', symbol='circle'),
            name=f"{nombre_sn} {color_name} (real en extendida)",
            legendgroup=f"{nombre_sn}_{color_name}",
            visible=True
        ))
        trazas.append(go.Scatter(
            x=t_pca[mask_ext_filtro],
            y=col_pca[mask_ext_filtro],
            mode='markers',
            marker=dict(color='red', symbol='x'),
            name=f"{nombre_sn} {color_name} (extendida)",
            legendgroup=f"{nombre_sn}_{color_name}",
            visible=True
        ))

# Interfaz de selección de color
if colores_disponibles:
    desplegable = st.selectbox("Selecciona un color a visualizar:", sorted(colores_disponibles))
    
    # Mostrar gráfico
    fig = go.Figure()
    for trace in trazas:
        if desplegable in trace.name:
            fig.add_trace(trace)

    fig.update_layout(
        title=f"Curvas de color: {desplegable}",
        xaxis_title="Fase (días desde máximo)",
        yaxis_title="Magnitud de color",
        width=1200,
        height=600,
        template="plotly_white",
        legend_title="Click para activar/desactivar curvas"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"No se encontraron datos de curvas de color.")