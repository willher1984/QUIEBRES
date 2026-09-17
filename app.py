import streamlit as st
import pandas as pd
import plotly.express as px

from calculos import (
    preparar_cuadrillas,
    cargar_suspensiones,
    cargar_garantias,
    obtener_completadas,
    obtener_solucionadas,
    buscar_garantias,
)


# ============================================================
# CONFIGURACION
# ============================================================

st.set_page_config(
    page_title="QUIEBRES",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1 {
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITULO
# ============================================================

st.title("📊 QUIEBRES")

st.caption(
    "Análisis operativo de órdenes, completadas, solucionadas y garantías"
)

st.divider()


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data
def cargar_datos():

    cuadrillas = preparar_cuadrillas()
    suspensiones = cargar_suspensiones()
    garantias = cargar_garantias()

    return cuadrillas, suspensiones, garantias


try:

    cuadrillas, suspensiones, garantias = cargar_datos()

except Exception as e:

    st.error("❌ Error cargando los archivos.")

    st.exception(e)

    st.stop()


# ============================================================
# FILTROS
# ============================================================

st.subheader("🔎 Filtros")

col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# MES
# ------------------------------------------------------------

with col1:

    mes = st.selectbox(
        "MES ANALIZADO",
        ["Agosto 2026"]
    )


# ------------------------------------------------------------
# ALIADO
# ------------------------------------------------------------

with col2:

    lista_aliados = sorted(
        [
            str(x).strip()
            for x in cuadrillas["PROVEEDOR SUSPENDIO"]
            .dropna()
            if str(x).strip()
        ]
    )

    lista_aliados = list(dict.fromkeys(lista_aliados))

    aliado = st.selectbox(
        "ALIADO / PROVEEDOR QUE SUSPENDIÓ",
        ["Todos"] + lista_aliados
    )


# ------------------------------------------------------------
# TECNICO
# ------------------------------------------------------------

with col3:

    lista_tecnicos = sorted(
        [
            str(x).strip()
            for x in cuadrillas["TECNICO"]
            .dropna()
            if str(x).strip()
        ]
    )

    lista_tecnicos = list(dict.fromkeys(lista_tecnicos))

    tecnico = st.selectbox(
        "TÉCNICO",
        ["Todos"] + lista_tecnicos
    )


# ============================================================
# COMPLETADAS
# ============================================================

completadas = obtener_completadas(
    suspensiones,
    mes=8,
    anio=2026
)


# ============================================================
# FILTRAR CUADRILLAS
# ============================================================

cuad_filtradas = cuadrillas.copy()


if aliado != "Todos":

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas["PROVEEDOR SUSPENDIO"]
        == aliado
    ]


if tecnico != "Todos":

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas["TECNICO"]
        == tecnico
    ]


# ============================================================
# SOLUCIONADAS
# ============================================================

solucionadas = obtener_solucionadas(
    cuad_filtradas
)


# ============================================================
# INDICADORES
# ============================================================

total_completadas = len(completadas)

total_solucionadas = len(solucionadas)


if total_completadas > 0:

    porcentaje_solucion = (
        total_solucionadas /
        total_completadas
    ) * 100

else:

    porcentaje_solucion = 0


st.subheader("📌 Indicadores principales")

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "COMPLETADAS",
    f"{total_completadas:,}"
)


c2.metric(
    "SOLUCIONADAS",
    f"{total_solucionadas:,}"
)


c3.metric(
    "% SOLUCIONADAS",
    f"{porcentaje_solucion:.2f}%"
)


c4.metric(
    "ÓRDENES CUADRILLAS",
    f"{len(cuad_filtradas):,}"
)


st.divider()


# ============================================================
# COMPLETADAS VS SOLUCIONADAS
# ============================================================

st.subheader(
    "📊 Completadas vs Solucionadas"
)


df_resumen = pd.DataFrame({

    "Tipo": [
        "Completadas",
        "Solucionadas"
    ],

    "Cantidad": [
        total_completadas,
        total_solucionadas
    ]

})


fig = px.bar(
    df_resumen,
    x="Tipo",
    y="Cantidad",
    text="Cantidad",
    title="Órdenes completadas y solucionadas"
)


fig.update_traces(
    textposition="outside"
)


st.plotly_chart(
    fig,
    width="stretch"
)


# ============================================================
# RESULTADOS
# ============================================================

st.subheader(
    "📊 Estados / Resultados"
)


df_resultados = (
    cuad_filtradas[
        "RESULTADO_NORMALIZADO"
    ]
    .replace("", "SIN RESULTADO")
    .value_counts()
    .reset_index()
)


df_resultados.columns = [
    "Resultado",
    "Cantidad"
]


if not df_resultados.empty:

    fig_resultados = px.pie(
        df_resultados,
        names="Resultado",
        values="Cantidad",
        hole=0.45,
        title="Distribución de resultados"
    )

    st.plotly_chart(
        fig_resultados,
        width="stretch"
    )


# ============================================================
# PROVEEDOR
# ============================================================

st.subheader(
    "🤝 Órdenes por proveedor que suspendió"
)


df_proveedores = (
    cuad_filtradas[
        "PROVEEDOR SUSPENDIO"
    ]
    .replace("", "SIN PROVEEDOR")
    .value_counts()
    .reset_index()
)


df_proveedores.columns = [
    "Proveedor",
    "Cantidad"
]


if not df_proveedores.empty:

    fig_proveedores = px.bar(
        df_proveedores,
        x="Proveedor",
        y="Cantidad",
        text="Cantidad",
        title="Órdenes por proveedor"
    )

    fig_proveedores.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_proveedores,
        width="stretch"
    )


# ============================================================
# GARANTIAS
# ============================================================

st.subheader(
    "🛠️ Garantías dentro de los 60 días"
)


datos_garantia = buscar_garantias(
    solucionadas,
    garantias
)


total_garantias = int(
    datos_garantia["TIENE_GARANTIA"].sum()
)


if total_solucionadas > 0:

    porcentaje_garantia = (
        total_garantias /
        total_solucionadas
    ) * 100

else:

    porcentaje_garantia = 0


g1, g2 = st.columns(2)


g1.metric(
    "SOLUCIONADAS CON GARANTÍA",
    f"{total_garantias:,}"
)


g2.metric(
    "% CON GARANTÍA",
    f"{porcentaje_garantia:.2f}%"
)


# ============================================================
# TABLA GARANTIAS
# ============================================================

garantias_encontradas = datos_garantia[
    datos_garantia["TIENE_GARANTIA"]
].copy()


if not garantias_encontradas.empty:

    columnas_garantia = [
        "MDM_FIBRA",
        "FECHA DE EJECUCION 1",
        "Fecha",
        "MAESTRA",
        "MAESTAR PQR",
        "Garantia",
        "Orden Original"
    ]

    columnas_garantia = [
        c
        for c in columnas_garantia
        if c in garantias_encontradas.columns
    ]

    st.dataframe(
        garantias_encontradas[
            columnas_garantia
        ],
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No se encontraron garantías dentro de los 60 días."
    )


# ============================================================
# TABLA PRINCIPAL
# ============================================================

st.subheader(
    "📋 Detalle de órdenes solucionadas"
)


columnas_principales = [
    "ORDEN DE TRABAJO",
    "Service Items name",
    "NUMERO DE CUENTA",
    "NOMBRE DEL CLIENTE",
    "DIRECCION",
    "PROVEEDOR SUSPENDIO",
    "RESULTADO",
    "FECHA DE SUSPENSION",
    "FECHA DE EJECUCION 1",
    "TECNICO",
    "CTA COMPLETO"
]


columnas_principales = [
    c
    for c in columnas_principales
    if c in solucionadas.columns
]


st.dataframe(
    solucionadas[
        columnas_principales
    ],
    width="stretch",
    hide_index=True
)


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "QUIEBRES | Dashboard operativo BFTEL"
)
