import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from calculos import (
    cargar_cuadrillas,
    cargar_suspensiones,
    cargar_garantias,
    preparar_cuadrillas,
    obtener_completadas,
    obtener_solucionadas,
    obtener_completadas_de_solucionadas,
    buscar_garantias,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="QUIEBRES",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       FONDO GENERAL
       ===================================================== */

    .stApp {
        background:
            linear-gradient(
                135deg,
                rgba(8, 18, 35, 0.97),
                rgba(12, 35, 58, 0.96)
            );
        background-attachment: fixed;
    }


    /* =====================================================
       CONTENEDOR PRINCIPAL
       ===================================================== */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* =====================================================
       TITULO
       ===================================================== */

    .titulo-principal {
        font-size: 42px;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: 2px;
    }

    .subtitulo {
        text-align: center;
        color: #b8c7d9;
        font-size: 17px;
        margin-bottom: 30px;
    }


    /* =====================================================
       TARJETAS KPI
       ===================================================== */

    .kpi-card {
        background: linear-gradient(
            145deg,
            rgba(255,255,255,0.12),
            rgba(255,255,255,0.05)
        );

        border: 1px solid rgba(255,255,255,0.16);

        border-radius: 18px;

        padding: 22px 20px;

        min-height: 145px;

        box-shadow:
            0 8px 25px rgba(0,0,0,0.30),
            inset 0 1px 0 rgba(255,255,255,0.08);

        backdrop-filter: blur(12px);

        margin-bottom: 15px;
    }


    .kpi-titulo {
        color: #b9c8d8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }


    .kpi-valor {
        color: white;
        font-size: 35px;
        font-weight: 800;
        line-height: 1.1;
    }


    .kpi-descripcion {
        color: #91a5bb;
        font-size: 13px;
        margin-top: 8px;
    }


    /* =====================================================
       TITULOS DE SECCIÓN
       ===================================================== */

    .seccion {
        color: white;
        font-size: 23px;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }


    /* =====================================================
       FILTROS
       ===================================================== */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #071525 0%,
            #0d2238 100%
        );
    }


    [data-testid="stSidebar"] * {
        color: white;
    }


    /* =====================================================
       MÉTRICAS NATIVAS
       ===================================================== */

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        padding: 15px;
        border-radius: 15px;
    }


    /* =====================================================
       TABLAS
       ===================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* =====================================================
       BOTONES
       ===================================================== */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.15);
    }


    /* =====================================================
       TEXTO
       ===================================================== */

    p, label {
        color: #dbe7f3;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="titulo-principal">QUIEBRES</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Dashboard Operativo · BFTEL</div>',
    unsafe_allow_html=True
)


# ============================================================
# CARGA DE INFORMACIÓN
# ============================================================

try:

    cuadrillas = cargar_cuadrillas()
    suspensiones = cargar_suspensiones()
    garantias = cargar_garantias()

except Exception as e:

    st.error("Error cargando los archivos de datos.")
    st.exception(e)
    st.stop()


# ============================================================
# PREPARAR CUADRILLAS
# ============================================================

cuadrillas = preparar_cuadrillas(cuadrillas)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ FILTROS")

st.sidebar.markdown("### Periodo")

periodo = st.sidebar.selectbox(
    "Seleccione el periodo",
    ["Agosto 2026"]
)


# ------------------------------------------------------------
# PROVEEDOR
# ------------------------------------------------------------

proveedores = ["TODOS"]

if "PROVEEDOR SUSPENDIO" in cuadrillas.columns:

    lista_proveedores = (
        cuadrillas["PROVEEDOR SUSPENDIO"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    lista_proveedores = sorted(
        [
            x for x in lista_proveedores.unique()
            if x and x.upper() != "NAN"
        ]
    )

    proveedores.extend(lista_proveedores)


proveedor_seleccionado = st.sidebar.selectbox(
    "Proveedor que suspendió",
    proveedores
)


# ------------------------------------------------------------
# TECNICO
# ------------------------------------------------------------

tecnicos = ["TODOS"]

if "TECNICO" in cuadrillas.columns:

    lista_tecnicos = (
        cuadrillas["TECNICO"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    lista_tecnicos = sorted(
        [
            x for x in lista_tecnicos.unique()
            if x and x.upper() != "NAN"
        ]
    )

    tecnicos.extend(lista_tecnicos)


tecnico_seleccionado = st.sidebar.selectbox(
    "Técnico",
    tecnicos
)


# ============================================================
# FILTRO DE CUADRILLAS
# ============================================================

cuad_filtradas = cuadrillas.copy()


if (
    proveedor_seleccionado != "TODOS"
    and "PROVEEDOR SUSPENDIO" in cuad_filtradas.columns
):

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas["PROVEEDOR SUSPENDIO"]
        .astype(str)
        .str.strip()
        == proveedor_seleccionado
    ]


if (
    tecnico_seleccionado != "TODOS"
    and "TECNICO" in cuad_filtradas.columns
):

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas["TECNICO"]
        .astype(str)
        .str.strip()
        == tecnico_seleccionado
    ]


# ============================================================
# COMPLETADAS DEL UNIVERSO
# ============================================================

completadas = obtener_completadas(
    suspensiones,
    mes=8,
    anio=2026
)


# ============================================================
# SOLUCIONADAS
# ============================================================

solucionadas = obtener_solucionadas(
    cuad_filtradas
)


# ============================================================
# COMPLETADAS DE LAS SOLUCIONADAS
# ============================================================

completadas_solucionadas = obtener_completadas_de_solucionadas(
    solucionadas
)


# ============================================================
# PORCENTAJE
# ============================================================

total_universo = len(completadas)

total_solucionadas = len(solucionadas)

total_completadas_solucionadas = len(
    completadas_solucionadas
)


if total_universo > 0:

    porcentaje_aporte = (
        total_completadas_solucionadas
        / total_universo
    ) * 100

else:

    porcentaje_aporte = 0


# ============================================================
# TARJETAS PRINCIPALES
# ============================================================

st.markdown(
    '<div class="seccion">📊 Indicadores principales</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-titulo">
                Órdenes completadas
            </div>

            <div class="kpi-valor">
                {total_universo:,}
            </div>

            <div class="kpi-descripcion">
                Universo mensual
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-titulo">
                Solucionadas
            </div>

            <div class="kpi-valor">
                {total_solucionadas:,}
            </div>

            <div class="kpi-descripcion">
                Órdenes solucionadas por cuadrillas
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-titulo">
                Completadas de solucionadas
            </div>

            <div class="kpi-valor">
                {total_completadas_solucionadas:,}
            </div>

            <div class="kpi-descripcion">
                CTA COMPLETO = SI
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-titulo">
                Aporte a completadas
            </div>

            <div class="kpi-valor">
                {porcentaje_aporte:.2f}%
            </div>

            <div class="kpi-descripcion">
                Sobre {total_universo:,} completadas
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# VALIDACIÓN
# ============================================================

st.markdown(
    '<div class="seccion">📌 Resumen de CUADRILLAS</div>',
    unsafe_allow_html=True
)


c1, c2, c3 = st.columns(3)


with c1:
    st.metric(
        "Registros CUADRILLAS",
        f"{len(cuad_filtradas):,}"
    )


with c2:
    st.metric(
        "Solucionadas",
        f"{len(solucionadas):,}"
    )


with c3:
    no_completadas = (
        len(solucionadas)
        - len(completadas_solucionadas)
    )

    st.metric(
        "No completadas",
        f"{no_completadas:,}"
    )


# ============================================================
# GRÁFICO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="seccion">📈 Completadas vs solucionadas</div>',
    unsafe_allow_html=True
)


df_comparacion = pd.DataFrame(
    {
        "Categoría": [
            "Completadas universo",
            "Solucionadas",
            "Completadas de solucionadas"
        ],
        "Cantidad": [
            total_universo,
            total_solucionadas,
            total_completadas_solucionadas
        ]
    }
)


fig_comparacion = px.bar(
    df_comparacion,
    x="Categoría",
    y="Cantidad",
    text="Cantidad",
    title=""
)


fig_comparacion.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis_title="",
    yaxis_title="Cantidad"
)


fig_comparacion.update_traces(
    textposition="outside"
)


st.plotly_chart(
    fig_comparacion,
    use_container_width=True
)


# ============================================================
# DISTRIBUCIÓN DE RESULTADOS
# ============================================================

st.markdown(
    '<div class="seccion">📊 Estados de las órdenes de CUADRILLAS</div>',
    unsafe_allow_html=True
)


if "RESULTADO_NORMALIZADO" in cuad_filtradas.columns:

    estados = (
        cuad_filtradas["RESULTADO_NORMALIZADO"]
        .replace("", "SIN RESULTADO")
        .fillna("SIN RESULTADO")
        .value_counts()
        .reset_index()
    )

    estados.columns = [
        "Estado",
        "Cantidad"
    ]


    fig_estados = px.pie(
        estados,
        names="Estado",
        values="Cantidad",
        hole=0.45
    )


    fig_estados.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=20, b=20)
    )


    st.plotly_chart(
        fig_estados,
        use_container_width=True
    )


# ============================================================
# PROVEEDORES
# ============================================================

st.markdown(
    '<div class="seccion">🏢 Órdenes por proveedor que suspendió</div>',
    unsafe_allow_html=True
)


if "PROVEEDOR SUSPENDIO" in cuad_filtradas.columns:

    proveedores_grafico = (
        cuad_filtradas[
            "PROVEEDOR SUSPENDIO"
        ]
        .fillna("SIN PROVEEDOR")
        .astype(str)
        .value_counts()
        .reset_index()
    )

    proveedores_grafico.columns = [
        "Proveedor",
        "Cantidad"
    ]


    fig_proveedores = px.bar(
        proveedores_grafico,
        x="Proveedor",
        y="Cantidad",
        text="Cantidad"
    )


    fig_proveedores.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=20, b=20)
    )


    fig_proveedores.update_traces(
        textposition="outside"
    )


    st.plotly_chart(
        fig_proveedores,
        use_container_width=True
    )


# ============================================================
# GARANTÍAS
# ============================================================

st.markdown(
    '<div class="seccion">🛡️ Análisis de garantías · 60 días</div>',
    unsafe_allow_html=True
)


try:

    datos_garantia = buscar_garantias(
        completadas_solucionadas,
        garantias
    )

except Exception as e:

    st.warning(
        f"No fue posible calcular las garantías: {e}"
    )

    datos_garantia = pd.DataFrame()


if not datos_garantia.empty:

    total_con_garantia = int(
        datos_garantia["TIENE_GARANTIA"]
        .fillna(False)
        .sum()
    )


    total_sin_garantia = (
        len(datos_garantia)
        - total_con_garantia
    )


    porcentaje_garantia = (
        total_con_garantia
        / len(datos_garantia)
        * 100
        if len(datos_garantia) > 0
        else 0
    )


    g1, g2, g3 = st.columns(3)


    with g1:

        st.metric(
            "Con garantía",
            f"{total_con_garantia:,}"
        )


    with g2:

        st.metric(
            "Sin garantía",
            f"{total_sin_garantia:,}"
        )


    with g3:

        st.metric(
            "% con garantía",
            f"{porcentaje_garantia:.2f}%"
        )


    columnas_garantia = [
        "MDM_FIBRA",
        "FECHA DE EJECUCION 1",
        "Fecha",
        "MAESTRA",
        "MAESTAR PQR",
        "Garantia",
        "Orden Original"
    ]


    columnas_disponibles = [
        c for c in columnas_garantia
        if c in datos_garantia.columns
    ]


    st.dataframe(
        datos_garantia[columnas_disponibles],
        width="stretch",
        hide_index=True
    )


# ============================================================
# DETALLE DE SOLUCIONADAS
# ============================================================

st.markdown(
    '<div class="seccion">🔎 Detalle de órdenes solucionadas</div>',
    unsafe_allow_html=True
)


if not solucionadas.empty:

    columnas_detalle = [
        "ORDEN DE TRABAJO",
        "Service Items name",
        "RESULTADO",
        "CTA COMPLETO",
        "PROVEEDOR SUSPENDIO",
        "TECNICO",
        "FECHA DE SUSPENSION",
        "FECHA DE EJECUCION 1"
    ]


    columnas_detalle = [
        c for c in columnas_detalle
        if c in solucionadas.columns
    ]


    st.dataframe(
        solucionadas[columnas_detalle],
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No existen órdenes solucionadas con los filtros seleccionados."
    )


# ============================================================
# PIE
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#71849a;
        padding:35px 0 10px 0;
        font-size:13px;
    ">
        QUIEBRES · BFTEL · Dashboard Operativo
    </div>
    """,
    unsafe_allow_html=True
)
