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
# CUADRILLAS
# SOLO AGOSTO 2026
# ============================================================

def cargar_cuadrillas():

    df = pd.read_excel(
        ARCHIVO_CUADRILLAS,
        sheet_name="AGOSTO 2026"
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # Fechas
    for columna in [
        "FECHA DE SUSPENSION",
        "FECHA DE EJECUCION 1"
    ]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    # Textos
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
# SUSPENSIONES
# SOLO HOJA Hoja1
# ============================================================

def cargar_suspensiones():

    df = pd.read_excel(
        ARCHIVO_SUSPENSIONES,
        sheet_name="Hoja1"
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    if "Fecha" in df.columns:

        df["Fecha"] = pd.to_datetime(
            df["Fecha"],
            errors="coerce"
        )

    for columna in [
        "Estado",
        "ALIADO"
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
# GARANTIAS
# SOLO HOJA Hoja1
# ============================================================

def cargar_garantias():

    df = pd.read_excel(
        ARCHIVO_GARANTIAS,
        sheet_name="Hoja1"
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    for columna in [
        "Fecha",
        "Fecha Orden Original"
    ]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    columnas_texto = [
        "FIBRA+FECHA",
        "PQR+FECHA",
        "MAESTRA",
        "MAESTAR PQR",
        "Garantia",
        "Orden Original"
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
# PREPARAR CUADRILLAS
# ============================================================

def preparar_cuadrillas():

    df = cargar_cuadrillas()

    # CTA COMPLETO = SI
    df["CTA_COMPLETO_SI"] = (
        df["CTA COMPLETO"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("SI")
    )

    # RESULTADO NORMALIZADO
    df["RESULTADO_NORMALIZADO"] = (
        df["RESULTADO"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # MDM FIBRA
    df["MDM_FIBRA"] = (
        df["Service Items name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# COMPLETADAS DE SUSPENSIONES
# ============================================================

def obtener_completadas(
    suspensiones,
    mes,
    anio
):

    df = suspensiones.copy()

    df = df[
        df["Fecha"].dt.year == anio
    ]

    df = df[
        df["Fecha"].dt.month == mes
    ]

    df = df[
        df["Estado"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        == "COMPLETADO"
    ]

    return df


# ============================================================
# SOLUCIONADAS
#
# RESULTADO = SOLUCIONADA
#
# IMPORTANTE:
# NO se usa CTA COMPLETO para determinar solucionadas
# ============================================================

def obtener_solucionadas(cuadrillas):

    return cuadrillas[
        cuadrillas[
            "RESULTADO_NORMALIZADO"
        ] == "SOLUCIONADA"
    ].copy()


# ============================================================
# COMPLETADAS DE LAS SOLUCIONADAS
#
# CTA COMPLETO = SI
# ============================================================

def obtener_completadas_de_solucionadas(
    solucionadas
):

    return solucionadas[
        solucionadas[
            "CTA_COMPLETO_SI"
        ]
    ].copy()


# ============================================================
# CRUCE DE COMPLETADAS
# ============================================================

def cruzar_completadas(
    cuadrillas,
    completadas
):

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
        suffixes=(
            "_SUSP",
            "_CUAD"
        )
    )

    return resultado


# ============================================================
# GARANTIAS 60 DIAS
# ============================================================

def buscar_garantias(
    cuadrillas,
    garantias
):

    base = cuadrillas.copy()
    gar = garantias.copy()

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

    base["MDM_FIBRA"] = (
        base["MDM_FIBRA"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    gar["MAESTRA"] = (
        gar["MAESTRA"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    resultado = base.merge(
        gar,
        left_on="MDM_FIBRA",
        right_on="MAESTRA",
        how="left",
        suffixes=(
            "",
            "_GAR"
        )
    )

    resultado["TIENE_GARANTIA"] = (
        resultado["Fecha"].notna()
        &
        (
            resultado["Fecha"]
            >=
            resultado[
                "FECHA_INICIO_GARANTIA"
            ]
        )
        &
        (
            resultado["Fecha"]
            <=
            resultado[
                "FECHA_FIN_GARANTIA"
            ]
        )
    )

    return resultado


# ============================================================
# RESUMEN
# ============================================================

def generar_resumen(
    cuadrillas,
    completadas
):

    total_completadas = len(
        completadas
    )

    solucionadas = obtener_solucionadas(
        cuadrillas
    )

    total_solucionadas = len(
        solucionadas
    )

    completadas_solucionadas = (
        obtener_completadas_de_solucionadas(
            solucionadas
        )
    )

    total_completadas_solucionadas = len(
        completadas_solucionadas
    )

    if total_completadas > 0:

        porcentaje = (
            total_completadas_solucionadas
            /
            total_completadas
        ) * 100

    else:

        porcentaje = 0

    return {

        "completadas":
            total_completadas,

        "solucionadas":
            total_solucionadas,

        "completadas_de_solucionadas":
            total_completadas_solucionadas,

        "porcentaje_solucion":
            porcentaje
    }
