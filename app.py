import streamlit as st
import pandas as pd
import plotly.express as px

from calculos import (
    preparar_cuadrillas,
    cargar_suspensiones,
    cargar_garantias,
    obtener_completadas,
    obtener_solucionadas,
    obtener_completadas_de_solucionadas,
    buscar_garantias,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="QUIEBRES BFTEL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS - DISEÑO GENERAL
# ============================================================

st.markdown(
    """
    <style>

    /* -------------------------------------------------------
       FONDO GENERAL
    ------------------------------------------------------- */

    .stApp {
        background:
            linear-gradient(
                135deg,
                #f4f7fb 0%,
                #eef2f7 50%,
                #f8fafc 100%
            );
    }


    /* -------------------------------------------------------
       CONTENEDOR PRINCIPAL
    ------------------------------------------------------- */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* -------------------------------------------------------
       TITULO
    ------------------------------------------------------- */

    .titulo-dashboard {

        background:
            linear-gradient(
                135deg,
                #0f172a,
                #1e293b
            );

        padding: 28px 35px;

        border-radius: 20px;

        margin-bottom: 25px;

        box-shadow:
            0 10px 30px rgba(
                15,
                23,
                42,
                0.15
            );
    }


    .titulo-dashboard h1 {

        color: white;

        margin: 0;

        font-size: 34px;

        font-weight: 800;

        letter-spacing: 0.5px;
    }


    .titulo-dashboard p {

        color: #cbd5e1;

        margin:
            7px 0 0 0;

        font-size: 15px;
    }


    /* -------------------------------------------------------
       TARJETAS KPI
    ------------------------------------------------------- */

    .kpi-card {

        position: relative;

        background: rgba(
            255,
            255,
            255,
            0.96
        );

        border-radius: 18px;

        padding: 22px 24px;

        min-height: 145px;

        border:
            1px solid
            rgba(
                226,
                232,
                240,
                0.9
            );

        box-shadow:
            0 8px 25px
            rgba(
                15,
                23,
                42,
                0.08
            );

        overflow: hidden;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }


    .kpi-card:hover {

        transform:
            translateY(-3px);

        box-shadow:
            0 14px 35px
            rgba(
                15,
                23,
                42,
                0.13
            );
    }


    .kpi-card::before {

        content: "";

        position: absolute;

        left: 0;

        top: 0;

        bottom: 0;

        width: 5px;

        background:
            linear-gradient(
                180deg,
                #2563eb,
                #0ea5e9
            );
    }


    .kpi-title {

        font-size: 13px;

        color: #64748b;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 0.5px;

        margin-bottom: 10px;
    }


    .kpi-value {

        font-size: 34px;

        color: #0f172a;

        font-weight: 800;

        line-height: 1.1;
    }


    .kpi-description {

        margin-top: 9px;

        font-size: 12px;

        color: #94a3b8;
    }


    /* -------------------------------------------------------
       TARJETA COMPLETADAS
    ------------------------------------------------------- */

    .kpi-completadas::before {

        background:
            linear-gradient(
                180deg,
                #2563eb,
                #3b82f6
            );
    }


    /* -------------------------------------------------------
       TARJETA SOLUCIONADAS
    ------------------------------------------------------- */

    .kpi-solucionadas::before {

        background:
            linear-gradient(
                180deg,
                #16a34a,
                #22c55e
            );
    }


    /* -------------------------------------------------------
       TARJETA CTA
    ------------------------------------------------------- */

    .kpi-cta::before {

        background:
            linear-gradient(
                180deg,
                #f59e0b,
                #f97316
            );
    }


    /* -------------------------------------------------------
       TARJETA PORCENTAJE
    ------------------------------------------------------- */

    .kpi-porcentaje::before {

        background:
            linear-gradient(
                180deg,
                #7c3aed,
                #a855f7
            );
    }


    /* -------------------------------------------------------
       SECCIONES
    ------------------------------------------------------- */

    .section-title {

        background: white;

        padding:
            15px 20px;

        border-radius: 14px;

        border:
            1px solid
            #e2e8f0;

        box-shadow:
            0 4px 15px
            rgba(
                15,
                23,
                42,
                0.05
            );

        margin-top: 25px;

        margin-bottom: 15px;

        font-size: 18px;

        font-weight: 800;

        color: #0f172a;
    }


    /* -------------------------------------------------------
       FILTROS
    ------------------------------------------------------- */

    .filter-container {

        background: white;

        padding: 20px;

        border-radius: 16px;

        border:
            1px solid
            #e2e8f0;

        box-shadow:
            0 5px 18px
            rgba(
                15,
                23,
                42,
                0.06
            );

        margin-bottom: 20px;
    }


    /* -------------------------------------------------------
       METRICAS DE STREAMLIT
    ------------------------------------------------------- */

    [data-testid="stMetric"] {

        background: white;

        padding: 15px;

        border-radius: 12px;
    }


    /* -------------------------------------------------------
       DATAFRAME
    ------------------------------------------------------- */

    [data-testid="stDataFrame"] {

        border-radius: 14px;

        overflow: hidden;

        box-shadow:
            0 5px 18px
            rgba(
                15,
                23,
                42,
                0.06
            );
    }


    /* -------------------------------------------------------
       BOTONES
    ------------------------------------------------------- */

    .stButton > button {

        border-radius: 10px;

        font-weight: 700;
    }


    /* -------------------------------------------------------
       FOOTER
    ------------------------------------------------------- */

    .footer {

        margin-top: 35px;

        padding: 18px;

        text-align: center;

        color: #64748b;

        font-size: 12px;
    }


    /* -------------------------------------------------------
       RESPONSIVE
    ------------------------------------------------------- */

    @media (
        max-width: 768px
    ) {

        .titulo-dashboard h1 {

            font-size: 25px;
        }

        .kpi-value {

            font-size: 28px;
        }

        .kpi-card {

            margin-bottom: 12px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    """
    <div class="titulo-dashboard">

        <h1>📊 QUIEBRES</h1>

        <p>
            Dashboard operativo BFTEL ·
            Análisis de órdenes, solucionadas,
            completadas y garantías
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data
def cargar_datos():

    cuadrillas = preparar_cuadrillas()

    suspensiones = cargar_suspensiones()

    garantias = cargar_garantias()

    return (
        cuadrillas,
        suspensiones,
        garantias
    )


try:

    (
        cuadrillas,
        suspensiones,
        garantias
    ) = cargar_datos()

except Exception as e:

    st.error(
        "❌ Error cargando los archivos."
    )

    st.exception(e)

    st.stop()


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Filtros de análisis</div>',
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)


# ============================================================
# MES
# ============================================================

with col1:

    mes = st.selectbox(
        "MES ANALIZADO",
        ["Agosto 2026"]
    )


# ============================================================
# PROVEEDOR
# ============================================================

with col2:

    lista_aliados = sorted(
        [
            str(x).strip()
            for x in
            cuadrillas[
                "PROVEEDOR SUSPENDIO"
            ].dropna()
            if str(x).strip()
        ]
    )

    lista_aliados = list(
        dict.fromkeys(
            lista_aliados
        )
    )

    aliado = st.selectbox(
        "ALIADO / PROVEEDOR QUE SUSPENDIÓ",
        ["Todos"] + lista_aliados
    )


# ============================================================
# TECNICO
# ============================================================

with col3:

    lista_tecnicos = sorted(
        [
            str(x).strip()
            for x in
            cuadrillas[
                "TECNICO"
            ].dropna()
            if str(x).strip()
        ]
    )

    lista_tecnicos = list(
        dict.fromkeys(
            lista_tecnicos
        )
    )

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


total_completadas = len(
    completadas
)


# ============================================================
# FILTRAR CUADRILLAS
# ============================================================

cuad_filtradas = cuadrillas.copy()


if aliado != "Todos":

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas[
            "PROVEEDOR SUSPENDIO"
        ] == aliado
    ]


if tecnico != "Todos":

    cuad_filtradas = cuad_filtradas[
        cuad_filtradas[
            "TECNICO"
        ] == tecnico
    ]


# ============================================================
# SOLUCIONADAS
# ============================================================

solucionadas = obtener_solucionadas(
    cuad_filtradas
)


total_solucionadas = len(
    solucionadas
)


# ============================================================
# COMPLETADAS DE SOLUCIONADAS
# ============================================================

completadas_solucionadas = (
    obtener_completadas_de_solucionadas(
        solucionadas
    )
)


total_completadas_solucionadas = len(
    completadas_solucionadas
)


# ============================================================
# PORCENTAJE
# ============================================================

if total_completadas > 0:

    porcentaje_solucion = (
        total_completadas_solucionadas
        /
        total_completadas
    ) * 100

else:

    porcentaje_solucion = 0


# ============================================================
# INDICADORES
# ============================================================

st.markdown(
    '<div class="section-title">📌 Indicadores principales</div>',
    unsafe_allow_html=True
)


c1, c2, c3, c4 = st.columns(4)


# ============================================================
# TARJETA 1
# ============================================================

with c1:

    st.markdown(
        f"""
        <div class="kpi-card kpi-completadas">

            <div class="kpi-title">
                Completadas
            </div>

            <div class="kpi-value">
                {total_completadas:,}
            </div>

            <div class="kpi-description">
                Universo mensual
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TARJETA 2
# ============================================================

with c2:

    st.markdown(
        f"""
        <div class="kpi-card kpi-solucionadas">

            <div class="kpi-title">
                Solucionadas
            </div>

            <div class="kpi-value">
                {total_solucionadas:,}
            </div>

            <div class="kpi-description">
                Resultado SOLUCIONADA
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TARJETA 3
# ============================================================

with c3:

    st.markdown(
        f"""
        <div class="kpi-card kpi-cta">

            <div class="kpi-title">
                Completadas de solucionadas
            </div>

            <div class="kpi-value">
                {total_completadas_solucionadas:,}
            </div>

            <div class="kpi-description">
                CTA COMPLETO = SI
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TARJETA 4
# ============================================================

with c4:

    st.markdown(
        f"""
        <div class="kpi-card kpi-porcentaje">

            <div class="kpi-title">
                Aporte a completadas
            </div>

            <div class="kpi-value">
                {porcentaje_solucion:.2f}%
            </div>

            <div class="kpi-description">
                Sobre {total_completadas:,} completadas
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SEGUNDO BLOQUE
# ============================================================

st.markdown(
    '<div class="section-title">📊 Universo de CUADRILLAS</div>',
    unsafe_allow_html=True
)


q1, q2, q3 = st.columns(3)


q1.metric(
    "ÓRDENES CUADRILLAS",
    f"{len(cuad_filtradas):,}"
)


q2.metric(
    "SOLUCIONADAS",
    f"{total_solucionadas:,}"
)


q3.metric(
    "NO COMPLETADAS",
    f"{total_solucionadas - total_completadas_solucionadas:,}"
)


# ============================================================
# GRÁFICO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="section-title">📈 Completadas vs aporte de solucionadas</div>',
    unsafe_allow_html=True
)


df_resumen = pd.DataFrame(
    {
        "Tipo": [
            "Completadas",
            "Completadas de solucionadas"
        ],

        "Cantidad": [
            total_completadas,
            total_completadas_solucionadas
        ]
    }
)


fig_resumen = px.bar(
    df_resumen,
    x="Tipo",
    y="Cantidad",
    text="Cantidad",
    title=""
)


fig_resumen.update_traces(
    textposition="outside"
)


fig_resumen.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),
    font=dict(
        color="#334155"
    )
)


st.plotly_chart(
    fig_resumen,
    width="stretch"
)


# ============================================================
# RESULTADOS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Estados / Resultados de CUADRILLAS</div>',
    unsafe_allow_html=True
)


df_resultados = (
    cuad_filtradas[
        "RESULTADO_NORMALIZADO"
    ]
    .replace(
        "",
        "SIN RESULTADO"
    )
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
        hole=0.5
    )

    fig_resultados.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig_resultados,
        width="stretch"
    )


# ============================================================
# PROVEEDORES
# ============================================================

st.markdown(
    '<div class="section-title">🤝 Órdenes por proveedor que suspendió</div>',
    unsafe_allow_html=True
)


df_proveedores = (
    cuad_filtradas[
        "PROVEEDOR SUSPENDIO"
    ]
    .replace(
        "",
        "SIN PROVEEDOR"
    )
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
        text="Cantidad"
    )

    fig_proveedores.update_traces(
        textposition="outside"
    )

    fig_proveedores.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig_proveedores,
        width="stretch"
    )


# ============================================================
# GARANTIAS
# ============================================================

st.markdown(
    '<div class="section-title">🛠️ Garantías dentro de los 60 días</div>',
    unsafe_allow_html=True
)


datos_garantia = buscar_garantias(
    completadas_solucionadas,
    garantias
)


total_garantias = int(
    datos_garantia[
        "TIENE_GARANTIA"
    ].sum()
)


if total_completadas_solucionadas > 0:

    porcentaje_garantia = (
        total_garantias
        /
        total_completadas_solucionadas
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

garantias_encontradas = (
    datos_garantia[
        datos_garantia[
            "TIENE_GARANTIA"
        ]
    ]
    .copy()
)


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

st.markdown(
    '<div class="section-title">📋 Detalle de órdenes solucionadas</div>',
    unsafe_allow_html=True
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

st.markdown(
    """
    <div class="footer">

        QUIEBRES · Dashboard operativo BFTEL

    </div>
    """,
    unsafe_allow_html=True
)
