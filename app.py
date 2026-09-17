import streamlit as st
import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="QUIEBRES",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "DATA"

ARCHIVO_CUADRILLAS = DATA_DIR / "CUADRILLAS.xlsx"
ARCHIVO_SUSPENSIONES = DATA_DIR / "SUSPENSIONES.xlsx"
ARCHIVO_GARANTIAS = DATA_DIR / "GARANTIAS 2 MESES.xlsx"


# ============================================================
# FUNCIONES
# ============================================================

def cargar_excel(ruta):
    """
    Carga todas las hojas de un archivo Excel.
    """
    if not ruta.exists():
        st.error(f"No se encontró el archivo: {ruta}")
        return {}

    try:
        return pd.read_excel(
            ruta,
            sheet_name=None
        )
    except Exception as e:
        st.error(f"Error leyendo {ruta.name}: {e}")
        return {}


def mostrar_archivo(nombre, ruta):
    """
    Muestra las hojas y columnas de un Excel.
    """

    st.subheader(nombre)

    hojas = cargar_excel(ruta)

    if not hojas:
        return

    st.write("Hojas encontradas:")

    for nombre_hoja, df in hojas.items():

        st.markdown(f"### 📄 Hoja: `{nombre_hoja}`")

        st.write(
            f"Filas: **{len(df):,}** | "
            f"Columnas: **{len(df.columns)}**"
        )

        st.write("Columnas:")

        st.code(
            "\n".join(str(col) for col in df.columns)
        )

        with st.expander("Ver primeras 5 filas"):
            st.dataframe(
                df.head(5),
                use_container_width=True
            )


# ============================================================
# ENCABEZADO
# ============================================================

st.title("📊 QUIEBRES")

st.markdown(
    """
    ### Diagnóstico de archivos

    Esta pantalla verifica que los archivos de datos estén
    correctamente conectados al dashboard.
    """
)

st.divider()


# ============================================================
# ARCHIVOS
# ============================================================

mostrar_archivo(
    "1️⃣ CUADRILLAS",
    ARCHIVO_CUADRILLAS
)

st.divider()

mostrar_archivo(
    "2️⃣ SUSPENSIONES",
    ARCHIVO_SUSPENSIONES
)

st.divider()

mostrar_archivo(
    "3️⃣ GARANTIAS 2 MESES",
    ARCHIVO_GARANTIAS
)


# ============================================================
# PIE
# ============================================================

st.divider()

st.success(
    "Diagnóstico terminado. "
    "Cuando las columnas sean verificadas, construiremos "
    "el dashboard definitivo de QUIEBRES."
)
