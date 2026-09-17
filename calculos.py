import pandas as pd
from pathlib import Path


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "DATA"

ARCHIVO_CUADRILLAS = DATA_DIR / "CUADRILLAS.xlsx"
ARCHIVO_SUSPENSIONES = DATA_DIR / "SUSPENSIONES.xlsx"
ARCHIVO_GARANTIAS = DATA_DIR / "GARANTIAS 2 MESES.xlsx"


# ============================================================
# CARGAR CUADRILLAS
# SOLO AGOSTO 2026
# ============================================================

def cargar_cuadrillas():

    df = pd.read_excel(
        ARCHIVO_CUADRILLAS,
        sheet_name="AGOSTO 2026"
    )

    df.columns = df.columns.astype(str).str.strip()

    # Convertir fechas
    df["FECHA DE SUSPENSION"] = pd.to_datetime(
        df["FECHA DE SUSPENSION"],
        errors="coerce"
    )

    df["FECHA DE EJECUCION 1"] = pd.to_datetime(
        df["FECHA DE EJECUCION 1"],
        errors="coerce"
    )

    # Limpiar textos importantes
    columnas_texto = [
        "Service Items name",
        "PROVEEDOR SUSPENDIO",
        "RESULTADO",
        "TECNICO",
        "CTA COMPLETO",
        "MES"
    ]

    for columna in columnas_texto:
        if columna in df.columns:
            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# CARGAR SUSPENSIONES
# SOLO HOJA Hoja1
# ============================================================

def cargar_suspensiones():

    df = pd.read_excel(
        ARCHIVO_SUSPENSIONES,
        sheet_name="Hoja1"
    )

    df.columns = df.columns.astype(str).str.strip()

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    df["Estado"] = (
        df["Estado"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["ALIADO"] = (
        df["ALIADO"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# CARGAR GARANTIAS
# SOLO HOJA Hoja1
# ============================================================

def cargar_garantias():

    df = pd.read_excel(
        ARCHIVO_GARANTIAS,
        sheet_name="Hoja1"
    )

    df.columns = df.columns.astype(str).str.strip()

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    df["Fecha Orden Original"] = pd.to_datetime(
        df["Fecha Orden Original"],
        errors="coerce"
    )

    # Limpiar identificadores
    for columna in [
        "FIBRA+FECHA",
        "PQR+FECHA",
        "MAESTRA",
        "MAESTAR PQR",
        "Garantia",
        "Orden Original"
    ]:

        if columna in df.columns:
            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# PREPARAR DATOS PRINCIPALES
# ============================================================

def preparar_cuadrillas():

    df = cargar_cuadrillas()

    # Normalizar CTA COMPLETO
    df["CTA_COMPLETO_SI"] = (
        df["CTA COMPLETO"]
        .str.upper()
        .eq("SI")
    )

    # Normalizar resultado
    df["RESULTADO_NORMALIZADO"] = (
        df["RESULTADO"]
        .str.upper()
        .str.strip()
    )

    # MDM
    df["MDM_FIBRA"] = (
        df["Service Items name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# COMPLETADAS DEL MES
# ============================================================

def obtener_completadas(suspensiones, mes, anio):

    df = suspensiones.copy()

    df = df[
        (df["Fecha"].dt.month == mes) &
        (df["Fecha"].dt.year == anio)
    ]

    df = df[
        df["Estado"].str.upper() == "COMPLETADO"
    ]

    return df


# ============================================================
# SOLUCIONADAS
# ============================================================

def obtener_solucionadas(cuadrillas):

    return cuadrillas[
        cuadrillas["CTA_COMPLETO_SI"]
    ].copy()


# ============================================================
# CRUCE DE COMPLETADAS CONTRA CUADRILLAS
# ============================================================

def cruzar_completadas(cuadrillas, completadas):

    izquierda = completadas.copy()
    derecha = cuadrillas.copy()

    izquierda["ORDEN"] = (
        izquierda["orden"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    derecha["ORDEN"] = (
        derecha["ORDEN DE TRABAJO"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    resultado = izquierda.merge(
        derecha,
        on="ORDEN",
        how="left",
        suffixes=("_SUSP", "_CUAD")
    )

    return resultado


# ============================================================
# GARANTIAS EN VENTANA DE 60 DIAS
# ============================================================

def buscar_garantias(cuadrillas, garantias):

    base = cuadrillas.copy()
    gar = garantias.copy()

    # Solo órdenes con fecha de ejecución
    base = base[
        base["FECHA DE EJECUCION 1"].notna()
    ].copy()

    base["FECHA_INICIO_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
    )

    base["FECHA_FIN_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
        + pd.Timedelta(days=60)
    )

    # Cruce por MDM
    base["MDM_FIBRA"] = (
        base["MDM_FIBRA"]
        .astype(str)
        .str.strip()
    )

    gar["MAESTRA"] = (
        gar["MAESTRA"]
        .astype(str)
        .str.strip()
    )

    resultado = base.merge(
        gar,
        left_on="MDM_FIBRA",
        right_on="MAESTRA",
        how="left",
        suffixes=("", "_GAR")
    )

    # Garantía dentro de los 60 días
    resultado["TIENE_GARANTIA"] = (
        resultado["Fecha"].notna()
        &
        (
            resultado["Fecha"]
            >= resultado["FECHA_INICIO_GARANTIA"]
        )
        &
        (
            resultado["Fecha"]
            <= resultado["FECHA_FIN_GARANTIA"]
        )
    )

    return resultado


# ============================================================
# RESUMEN GENERAL
# ============================================================

def generar_resumen(cuadrillas, completadas):

    total_completadas = len(completadas)

    total_solucionadas = int(
        cuadrillas["CTA_COMPLETO_SI"].sum()
    )

    if total_completadas > 0:
        porcentaje_solucion = (
            total_solucionadas /
            total_completadas
        ) * 100
    else:
        porcentaje_solucion = 0

    return {
        "completadas": total_completadas,
        "solucionadas": total_solucionadas,
        "porcentaje_solucion": porcentaje_solucion
    }
