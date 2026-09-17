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
# IMPORTANTE:
# SOLO SE UTILIZA LA HOJA AGOSTO 2026
# ============================================================

def cargar_cuadrillas():

    df = pd.read_excel(
        ARCHIVO_CUADRILLAS,
        sheet_name="AGOSTO 2026"
    )

    df.columns = df.columns.astype(str).str.strip()

    # Fechas
    if "FECHA DE SUSPENSION" in df.columns:
        df["FECHA DE SUSPENSION"] = pd.to_datetime(
            df["FECHA DE SUSPENSION"],
            errors="coerce"
        )

    if "FECHA DE EJECUCION 1" in df.columns:
        df["FECHA DE EJECUCION 1"] = pd.to_datetime(
            df["FECHA DE EJECUCION 1"],
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
# CARGAR SUSPENSIONES
# SOLO HOJA Hoja1
# ============================================================

def cargar_suspensiones():

    df = pd.read_excel(
        ARCHIVO_SUSPENSIONES,
        sheet_name="Hoja1"
    )

    df.columns = df.columns.astype(str).str.strip()

    if "Fecha" in df.columns:

        df["Fecha"] = pd.to_datetime(
            df["Fecha"],
            errors="coerce"
        )

    if "Estado" in df.columns:

        df["Estado"] = (
            df["Estado"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if "ALIADO" in df.columns:

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

    # Fechas
    if "Fecha" in df.columns:

        df["Fecha"] = pd.to_datetime(
            df["Fecha"],
            errors="coerce"
        )

    if "Fecha Orden Original" in df.columns:

        df["Fecha Orden Original"] = pd.to_datetime(
            df["Fecha Orden Original"],
            errors="coerce"
        )

    # Textos
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

    # --------------------------------------------------------
    # CTA COMPLETO
    # --------------------------------------------------------

    df["CTA_COMPLETO_SI"] = (
        df["CTA COMPLETO"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("SI")
    )

    # --------------------------------------------------------
    # RESULTADO NORMALIZADO
    # --------------------------------------------------------

    df["RESULTADO_NORMALIZADO"] = (
        df["RESULTADO"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # MDM FIBRA
    # --------------------------------------------------------

    df["MDM_FIBRA"] = (
        df["Service Items name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# OBTENER COMPLETADAS
#
# LAS 17.785 PROVIENEN DE SUSPENSIONES
# Estado = COMPLETADO
# ============================================================

def obtener_completadas(
    suspensiones,
    mes,
    anio
):

    df = suspensiones.copy()

    # Filtrar año
    df = df[
        df["Fecha"].dt.year == anio
    ]

    # Filtrar mes
    df = df[
        df["Fecha"].dt.month == mes
    ]

    # Estado COMPLETADO
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
# OBTENER SOLUCIONADAS
#
# IMPORTANTE:
#
# SOLUCIONADAS NO ES CTA COMPLETO = SI
#
# SOLUCIONADAS =
# RESULTADO = SOLUCIONADA
#
# Esperado: 183
# ============================================================

def obtener_solucionadas(cuadrillas):

    return cuadrillas[
        cuadrillas["RESULTADO_NORMALIZADO"]
        == "SOLUCIONADA"
    ].copy()


# ============================================================
# OBTENER COMPLETADAS DE LAS SOLUCIONADAS
#
# De las 183 SOLUCIONADAS:
#
# CTA COMPLETO = SI
#
# Esperado: 158
# ============================================================

def obtener_completadas_de_solucionadas(
    solucionadas
):

    return solucionadas[
        solucionadas["CTA_COMPLETO_SI"]
    ].copy()


# ============================================================
# CRUCE COMPLETADAS CONTRA CUADRILLAS
# ============================================================

def cruzar_completadas(
    cuadrillas,
    completadas
):

    izquierda = completadas.copy()

    derecha = cuadrillas.copy()

    # Orden de suspensiones
    izquierda["ORDEN"] = (
        izquierda["orden"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Orden de cuadrillas
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
# GARANTIAS
#
# CRUCE:
#
# CUADRILLAS Service Items name
#             ↓
# GARANTIAS MAESTRA
#
# Ventana:
# FECHA EJECUCION + 60 DIAS
# ============================================================

def buscar_garantias(
    cuadrillas,
    garantias
):

    base = cuadrillas.copy()

    gar = garantias.copy()

    # --------------------------------------------------------
    # Solo registros con fecha de ejecución
    # --------------------------------------------------------

    base = base[
        base["FECHA DE EJECUCION 1"].notna()
    ].copy()

    # --------------------------------------------------------
    # Inicio garantía
    # --------------------------------------------------------

    base["FECHA_INICIO_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
    )

    # --------------------------------------------------------
    # Fin garantía
    # --------------------------------------------------------

    base["FECHA_FIN_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
        + pd.Timedelta(days=60)
    )

    # --------------------------------------------------------
    # Normalizar MDM
    # --------------------------------------------------------

    base["MDM_FIBRA"] = (
        base["MDM_FIBRA"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Normalizar MAESTRA
    # --------------------------------------------------------

    gar["MAESTRA"] = (
        gar["MAESTRA"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Cruce
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Validar ventana de 60 días
    # --------------------------------------------------------

    resultado["TIENE_GARANTIA"] = (
        resultado["Fecha"].notna()
        &
        (
            resultado["Fecha"]
            >=
            resultado["FECHA_INICIO_GARANTIA"]
        )
        &
        (
            resultado["Fecha"]
            <=
            resultado["FECHA_FIN_GARANTIA"]
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

    # Universo
    total_completadas = len(
        completadas
    )

    # Solucionadas
    solucionadas = obtener_solucionadas(
        cuadrillas
    )

    total_solucionadas = len(
        solucionadas
    )

    # Completadas de solucionadas
    completadas_solucionadas = (
        obtener_completadas_de_solucionadas(
            solucionadas
        )
    )

    total_completadas_solucionadas = len(
        completadas_solucionadas
    )

    # Porcentaje
    if total_completadas > 0:

        porcentaje = (
            total_completadas_solucionadas
            /
            total_completadas
        ) * 100

    else:

        porcentaje = 0

    return {

        "completadas": total_completadas,

        "solucionadas": total_solucionadas,

        "completadas_de_solucionadas":
            total_completadas_solucionadas,

        "porcentaje_solucion":
            porcentaje

    }
