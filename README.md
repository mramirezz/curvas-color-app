# Curvas de Color - SN Tipo Ibc

Aplicación Streamlit para visualizar y comparar curvas de color generadas a partir de curvas de luz reales y extendidas (PCA) de supernovas tipo Ibc.

## 📁 Estructura esperada del repositorio

```
curvas_color_app/
├── streamlit_app.py         # Código principal de la app
├── requirements.txt         # Requisitos de Python
├── utils.py                 # Funciones: data_curvas, maximo_lc
├── data/
│   ├── real/                # Archivos .dat reales
│   └── pca/                 # Archivos .dat extendidos
```

## ▶ Cómo ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## ☁ Cómo desplegar en Streamlit Cloud

1. Sube el contenido del directorio a un repositorio de GitHub
2. Conéctalo desde https://streamlit.io/cloud
3. Asegúrate de que `streamlit_app.py` y `requirements.txt` estén en la raíz del repo
4. Asegúrate de que los archivos `.dat` estén en `data/real/` y `data/pca/`

## 🛠 Dependencias

- streamlit
- pandas
- numpy
- plotly

## ⚠ Notas

- Solo se grafican curvas de color válidas (orden azul - rojo)
