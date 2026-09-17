import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from calculos import (
    cargar_cuadrillas,
    cargar_suspensiones,
    preparar_cuadrillas,
    obtener_completadas,
    obtener_solucionadas,
    obtener_completadas_de_solucionadas,
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

    .stApp {
        background:
            linear-gradient(
                135deg,
                rgba(8, 18, 35, 0.97),
                rgba(12, 35, 58, 0.96)
            );
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

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

    .seccion {
        color: white;
        font-size: 23px;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

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

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        padding: 15px;
        border-radius: 15px;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.15);
    }

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
# TABLA COMPLETA DE CUADRILLAS
# ============================================================

st.markdown(
    '<div class="seccion">🔎 Detalle completo de CUADRILLAS</div>',
    unsafe_allow_html=True
)


# ============================================================
# FILTROS EXCLUSIVOS DE LA TABLA
# ============================================================

st.markdown(
    "#### 🔍 Filtros de la tabla",
    unsafe_allow_html=True
)


tabla_filtrada = cuad_filtradas.copy()


f1, f2, f3, f4, f5 = st.columns(5)


# ------------------------------------------------------------
# FILTRO RESULTADO
# ------------------------------------------------------------

if "RESULTADO" in tabla_filtrada.columns:

    opciones_resultado = ["TODOS"] + sorted(
        tabla_filtrada["RESULTADO"]
        .fillna("SIN RESULTADO")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    with f1:

        filtro_resultado = st.selectbox(
            "Resultado",
            opciones_resultado,
            key="tabla_resultado"
        )

    if filtro_resultado != "TODOS":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["RESULTADO"]
            .fillna("SIN RESULTADO")
            .astype(str)
            .str.strip()
            == filtro_resultado
        ]


# ------------------------------------------------------------
# FILTRO CTA COMPLETO
# ------------------------------------------------------------

if "CTA COMPLETO" in tabla_filtrada.columns:

    opciones_cta = ["TODOS"] + sorted(
        tabla_filtrada["CTA COMPLETO"]
        .fillna("SIN DATO")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    with f2:

        filtro_cta = st.selectbox(
            "CTA COMPLETO",
            opciones_cta,
            key="tabla_cta"
        )

    if filtro_cta != "TODOS":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["CTA COMPLETO"]
            .fillna("SIN DATO")
            .astype(str)
            .str.strip()
            == filtro_cta
        ]


# ------------------------------------------------------------
# FILTRO NODO
# ------------------------------------------------------------

if "NODO" in tabla_filtrada.columns:

    opciones_nodo = ["TODOS"] + sorted(
        tabla_filtrada["NODO"]
        .fillna("SIN NODO")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    with f3:

        filtro_nodo = st.selectbox(
            "Nodo",
            opciones_nodo,
            key="tabla_nodo"
        )

    if filtro_nodo != "TODOS":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["NODO"]
            .fillna("SIN NODO")
            .astype(str)
            .str.strip()
            == filtro_nodo
        ]


# ------------------------------------------------------------
# FILTRO TIPO VEHÍCULO
# ------------------------------------------------------------

if "TIPO VEHICULO" in tabla_filtrada.columns:

    opciones_vehiculo = ["TODOS"] + sorted(
        tabla_filtrada["TIPO VEHICULO"]
        .fillna("SIN DATO")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    with f4:

        filtro_vehiculo = st.selectbox(
            "Tipo vehículo",
            opciones_vehiculo,
            key="tabla_vehiculo"
        )

    if filtro_vehiculo != "TODOS":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["TIPO VEHICULO"]
            .fillna("SIN DATO")
            .astype(str)
            .str.strip()
            == filtro_vehiculo
        ]


# ------------------------------------------------------------
# FILTRO CÓDIGO
# ------------------------------------------------------------

if "CODIGO" in tabla_filtrada.columns:

    opciones_codigo = ["TODOS"] + sorted(
        tabla_filtrada["CODIGO"]
        .fillna("SIN CODIGO")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    with f5:

        filtro_codigo = st.selectbox(
            "Código",
            opciones_codigo,
            key="tabla_codigo"
        )

    if filtro_codigo != "TODOS":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["CODIGO"]
            .fillna("SIN CODIGO")
            .astype(str)
            .str.strip()
            == filtro_codigo
        ]


# ============================================================
# TODAS LAS COLUMNAS ORIGINALES
# ============================================================

columnas_auxiliares = [
    "CTA_COMPLETO_SI",
    "RESULTADO_NORMALIZADO",
    "MDM_FIBRA"
]


columnas_originales = [
    c for c in tabla_filtrada.columns
    if c not in columnas_auxiliares
]


tabla_final = tabla_filtrada[
    columnas_originales
].copy()


# ============================================================
# INFORMACIÓN DE LA TABLA
# ============================================================

st.markdown(
    f"""
    <div style="
        color:#b8c7d9;
        font-size:14px;
        margin:10px 0 10px 0;
    ">
        Registros mostrados:
        <strong style="color:white;">
            {len(tabla_final):,}
        </strong>

        &nbsp; | &nbsp;

        Columnas:
        <strong style="color:white;">
            {len(tabla_final.columns):,}
        </strong>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABLA
# ============================================================

st.dataframe(
    tabla_final,
    width="stretch",
    height=600,
    hide_index=True
)


# ============================================================
# DESCARGAR TABLA FILTRADA
# ============================================================

buffer_excel = BytesIO()


with pd.ExcelWriter(
    buffer_excel,
    engine="openpyxl"
) as writer:

    tabla_final.to_excel(
        writer,
        index=False,
        sheet_name="CUADRILLAS FILTRADAS"
    )


buffer_excel.seek(0)


st.download_button(
    label="📥 Descargar tabla filtrada en Excel",
    data=buffer_excel,
    file_name="CUADRILLAS_FILTRADAS_AGOSTO_2026.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    width="stretch"
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
