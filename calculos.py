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
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_texto(serie):
    """
    Convierte una columna a texto limpio y en mayúsculas.
    """

    return (
        serie
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )


def normalizar_columnas(df):
    """
    Limpia los nombres de columnas.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# CUADRILLAS
# SOLO AGOSTO 2026
# ============================================================

def cargar_cuadrillas():

    if not ARCHIVO_CUADRILLAS.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_CUADRILLAS}"
        )

    df = pd.read_excel(
        ARCHIVO_CUADRILLAS,
        sheet_name="AGOSTO 2026"
    )

    df = normalizar_columnas(df)

    # --------------------------------------------------------
    # Fechas
    # --------------------------------------------------------

    for columna in [
        "FECHA DE SUSPENSION",
        "FECHA DE EJECUCION 1"
    ]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Columnas de texto
    # --------------------------------------------------------

    columnas_texto = [
        "MES",
        "ORDEN DE TRABAJO",
        "Service Items name",
        "Item Code",
        "NUMERO DE CUENTA",
        "NOMBRE DEL CLIENTE",
        "DIRECCION",
        "PROVEEDOR SUSPENDIO",
        "COMENTARIO",
        "NODO",
        "RESULTADO",
        "CODIGO",
        "OBSERVACIONES",
        "CABLE BAJA FRICCION",
        "CABLE INDOOR",
        "TENSORES",
        "TECNICO",
        "TIPO VEHICULO",
        "CTA COMPLETO"
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

def preparar_cuadrillas(df):

    df = df.copy()

    # --------------------------------------------------------
    # Validación de columnas necesarias
    # --------------------------------------------------------

    columnas_necesarias = [
        "ORDEN DE TRABAJO",
        "RESULTADO",
        "CTA COMPLETO"
    ]

    faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas obligatorias en CUADRILLAS: "
            + ", ".join(faltantes)
        )

    # --------------------------------------------------------
    # CTA COMPLETO
    # --------------------------------------------------------

    df["CTA_COMPLETO_SI"] = (
        normalizar_texto(
            df["CTA COMPLETO"]
        )
        == "SI"
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    df["RESULTADO_NORMALIZADO"] = normalizar_texto(
        df["RESULTADO"]
    )

    # --------------------------------------------------------
    # MDM-FIBRA
    #
    # IMPORTANTE:
    # El MDM-FIBRA está en ORDEN DE TRABAJO
    # --------------------------------------------------------

    df["MDM_FIBRA"] = normalizar_texto(
        df["ORDEN DE TRABAJO"]
    )

    return df


# ============================================================
# SUSPENSIONES
# SOLO Hoja1
# ============================================================

def cargar_suspensiones():

    if not ARCHIVO_SUSPENSIONES.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_SUSPENSIONES}"
        )

    df = pd.read_excel(
        ARCHIVO_SUSPENSIONES,
        sheet_name="Hoja1"
    )

    df = normalizar_columnas(df)

    # --------------------------------------------------------
    # Fecha
    # --------------------------------------------------------

    if "Fecha" in df.columns:

        df["Fecha"] = pd.to_datetime(
            df["Fecha"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

    for columna in [
        "orden",
        "Estado",
        "Zona de trabajo",
        "ALIADO",
        "Razón de Suspensión",
        "TECNICO",
        "DIRECCION"
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
# SOLO Hoja1
# ============================================================

def cargar_garantias():

    if not ARCHIVO_GARANTIAS.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_GARANTIAS}"
        )

    df = pd.read_excel(
        ARCHIVO_GARANTIAS,
        sheet_name="Hoja1"
    )

    df = normalizar_columnas(df)

    # --------------------------------------------------------
    # Fechas
    # --------------------------------------------------------

    for columna in [
        "Fecha",
        "Fecha Orden Original"
    ]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

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
# COMPLETADAS DE SUSPENSIONES
#
# Estas son las que forman el UNIVERSO.
#
# AGOSTO 2026
# Estado = Completado
# ============================================================

def obtener_completadas(
    suspensiones,
    mes,
    anio
):

    df = suspensiones.copy()

    if "Fecha" not in df.columns:
        return df.iloc[0:0].copy()

    # --------------------------------------------------------
    # Fecha válida
    # --------------------------------------------------------

    df = df[
        df["Fecha"].notna()
    ].copy()

    # --------------------------------------------------------
    # Año
    # --------------------------------------------------------

    df = df[
        df["Fecha"].dt.year == anio
    ]

    # --------------------------------------------------------
    # Mes
    # --------------------------------------------------------

    df = df[
        df["Fecha"].dt.month == mes
    ]

    # --------------------------------------------------------
    # Estado
    # --------------------------------------------------------

    if "Estado" in df.columns:

        df = df[
            normalizar_texto(df["Estado"])
            == "COMPLETADO"
        ]

    return df


# ============================================================
# SOLUCIONADAS
#
# RESULTADO = SOLUCIONADA
#
# NO depende de CTA COMPLETO
# ============================================================

def obtener_solucionadas(cuadrillas):

    if cuadrillas.empty:
        return cuadrillas.copy()

    return cuadrillas[
        cuadrillas[
            "RESULTADO_NORMALIZADO"
        ] == "SOLUCIONADA"
    ].copy()


# ============================================================
# COMPLETADAS DE LAS SOLUCIONADAS
#
# De las SOLUCIONADAS:
# CTA COMPLETO = SI
#
# Ejemplo:
#
# 183 solucionadas
# 158 completadas
# ============================================================

def obtener_completadas_de_solucionadas(
    solucionadas
):

    if solucionadas.empty:
        return solucionadas.copy()

    return solucionadas[
        solucionadas[
            "CTA_COMPLETO_SI"
        ]
    ].copy()


# ============================================================
# CRUCE DE COMPLETADAS
#
# Sirve para relacionar:
#
# SUSPENSIONES
#       +
# CUADRILLAS
#
# por ORDEN DE TRABAJO
# ============================================================

def cruzar_completadas(
    cuadrillas,
    completadas
):

    izquierda = completadas.copy()
    derecha = cuadrillas.copy()

    # --------------------------------------------------------
    # ORDEN desde SUSPENSIONES
    # --------------------------------------------------------

    if "orden" in izquierda.columns:

        izquierda["ORDEN"] = normalizar_texto(
            izquierda["orden"]
        )

    else:

        izquierda["ORDEN"] = ""

    # --------------------------------------------------------
    # ORDEN desde CUADRILLAS
    # --------------------------------------------------------

    if "ORDEN DE TRABAJO" in derecha.columns:

        derecha["ORDEN"] = normalizar_texto(
            derecha["ORDEN DE TRABAJO"]
        )

    else:

        derecha["ORDEN"] = ""

    # --------------------------------------------------------
    # Cruce
    # --------------------------------------------------------

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
# REGLA:
#
# MDM-FIBRA de CUADRILLAS
#       =
# MAESTRA de GARANTIAS
#
# Y la garantía debe estar dentro de los
# 60 días posteriores a la ejecución.
#
# IMPORTANTE:
# NO se limita al mes de agosto.
# ============================================================

def buscar_garantias(
    cuadrillas,
    garantias
):

    base = cuadrillas.copy()
    gar = garantias.copy()

    # --------------------------------------------------------
    # Si no existen registros
    # --------------------------------------------------------

    if base.empty:

        base["TIENE_GARANTIA"] = False

        return base

    # --------------------------------------------------------
    # MDM-FIBRA
    # --------------------------------------------------------

    if "MDM_FIBRA" not in base.columns:

        base["MDM_FIBRA"] = normalizar_texto(
            base["ORDEN DE TRABAJO"]
        )

    else:

        base["MDM_FIBRA"] = normalizar_texto(
            base["MDM_FIBRA"]
        )

    # --------------------------------------------------------
    # Fecha de ejecución
    # --------------------------------------------------------

    if "FECHA DE EJECUCION 1" in base.columns:

        base["FECHA DE EJECUCION 1"] = pd.to_datetime(
            base["FECHA DE EJECUCION 1"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Ventana de garantía
    # --------------------------------------------------------

    base["FECHA_INICIO_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
    )

    base["FECHA_FIN_GARANTIA"] = (
        base["FECHA DE EJECUCION 1"]
        + pd.Timedelta(days=60)
    )

    # --------------------------------------------------------
    # Garantías
    # --------------------------------------------------------

    if "MAESTRA" in gar.columns:

        gar["MAESTRA"] = normalizar_texto(
            gar["MAESTRA"]
        )

    else:

        gar["MAESTRA"] = ""

    # --------------------------------------------------------
    # Fecha de garantía
    # --------------------------------------------------------

    if "Fecha" in gar.columns:

        gar["Fecha"] = pd.to_datetime(
            gar["Fecha"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # PQR
    # --------------------------------------------------------

    if "MAESTAR PQR" in gar.columns:

        gar["MAESTAR PQR"] = (
            gar["MAESTAR PQR"]
            .fillna("")
            .astype(str)
            .str.strip()
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
    # Determinar garantía
    #
    # Mismo MDM-FIBRA
    # +
    # Fecha dentro de 60 días
    # --------------------------------------------------------

    resultado["TIENE_GARANTIA"] = (
        resultado["MAESTRA"].notna()
        &
        (
            resultado["MAESTRA"]
            .astype(str)
            .str.strip()
            != ""
        )
        &
        resultado["Fecha"].notna()
        &
        resultado["FECHA_INICIO_GARANTIA"].notna()
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

    # --------------------------------------------------------
    # UNIVERSO
    # --------------------------------------------------------

    total_completadas = len(
        completadas
    )

    # --------------------------------------------------------
    # SOLUCIONADAS
    # --------------------------------------------------------

    solucionadas = obtener_solucionadas(
        cuadrillas
    )

    total_solucionadas = len(
        solucionadas
    )

    # --------------------------------------------------------
    # COMPLETADAS DENTRO DE LAS SOLUCIONADAS
    # --------------------------------------------------------

    completadas_solucionadas = (
        obtener_completadas_de_solucionadas(
            solucionadas
        )
    )

    total_completadas_solucionadas = len(
        completadas_solucionadas
    )

    # --------------------------------------------------------
    # PORCENTAJE
    #
    # 158 / 17785 * 100
    # ========================================================
    # Resultado esperado aproximadamente:
    #
    # 0.89 %
    # --------------------------------------------------------

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
