import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BBVA Conservación NE | Analytics",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# ESTILOS CSS PERSONALIZADOS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ---- General ---- */
    .main .block-container { padding: 1rem 2rem; max-width: 100%; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #004481 0%, #002855 100%); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { font-weight: 600; font-size: 0.85rem; letter-spacing: 0.3px; }
    
    /* ---- Header ---- */
    .main-header {
        background: linear-gradient(135deg, #004481 0%, #0066b2 50%, #1a8fe3 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,68,129,0.3);
    }
    .main-header h1 { margin: 0; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.5px; }
    .main-header p { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.9rem; }
    
    /* ---- KPI Cards ---- */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 4px solid #004481;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
    .kpi-card .kpi-value { font-size: 2rem; font-weight: 800; color: #004481; line-height: 1.1; }
    .kpi-card .kpi-label { font-size: 0.78rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.2rem; }
    .kpi-card .kpi-sub { font-size: 0.75rem; color: #999; margin-top: 0.3rem; }
    .kpi-green { border-left-color: #00a651; }
    .kpi-green .kpi-value { color: #00a651; }
    .kpi-orange { border-left-color: #ff9500; }
    .kpi-orange .kpi-value { color: #ff9500; }
    .kpi-red { border-left-color: #e63946; }
    .kpi-red .kpi-value { color: #e63946; }
    .kpi-purple { border-left-color: #7b2d8e; }
    .kpi-purple .kpi-value { color: #7b2d8e; }
    .kpi-cyan { border-left-color: #0097a7; }
    .kpi-cyan .kpi-value { color: #0097a7; }
    
    /* ---- Section Headers ---- */
    .section-header {
        background: linear-gradient(90deg, #f0f6ff, #ffffff);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #004481;
        margin: 1.5rem 0 1rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #002855;
    }
    
    /* ---- Tab styling ---- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f4f8;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #004481 !important;
        color: white !important;
    }
    
    /* ---- Tables ---- */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    
    /* ---- Hide Streamlit extras ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ---- Expander ---- */
    .streamlit-expanderHeader { font-weight: 600; color: #004481; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE PROCESAMIENTO DE DATOS
# ══════════════════════════════════════════════════════════════

@st.cache_data
def process_data(uploaded_file):
    """Procesa el archivo Excel y vincula supervisores."""
    # Leer ambas hojas
    df_bp = pd.read_excel(uploaded_file, sheet_name=0)  # Sheet1 - BP data
    df_sup = pd.read_excel(uploaded_file, sheet_name=1)  # Sheet2 - Supervisors
    
    # --- Limpiar Sheet2 ---
    df_sup.columns = df_sup.columns.str.strip()
    df_sup['CR'] = pd.to_numeric(df_sup['CR'], errors='coerce')
    # Eliminar duplicados de CR, mantener el primero
    df_sup = df_sup.drop_duplicates(subset='CR', keep='first')
    
    # --- Limpiar Sheet1 ---
    df_bp.columns = df_bp.columns.str.strip()
    
    # Renombrar columna Proveedor (tiene espacio extra)
    col_rename = {}
    for c in df_bp.columns:
        if 'Proveedor' in c:
            col_rename[c] = 'Proveedor'
    df_bp = df_bp.rename(columns=col_rename)
    
    # Extraer CR numérico del Centro de coste (MX11XXXXXX -> XXXXXX como int)
    df_bp['CR_num'] = (
        df_bp['Centro de coste']
        .astype(str)
        .str.replace('MX11', '', regex=False)
        .str.replace('MX', '', regex=False)
    )
    df_bp['CR_num'] = pd.to_numeric(df_bp['CR_num'], errors='coerce').astype('Int64')
    df_sup['CR'] = df_sup['CR'].astype('Int64')
    
    # --- Vincular con supervisores ---
    df = df_bp.merge(
        df_sup[['CR', 'SUCURSAL', 'TIPO DE BANCA', 'BCA SEGMENTADA', 'DZ', 'SUPERVISOR']],
        left_on='CR_num',
        right_on='CR',
        how='left',
        suffixes=('', '_cat')
    )
    
    # Rellenar columna Supervisor original con la del catálogo
    df['Supervisor_Asignado'] = df['SUPERVISOR'].fillna('Sin asignar')
    df['Zona'] = df['DZ'].fillna('Sin zona')
    df['Tipo_Banca'] = df['TIPO DE BANCA'].fillna('Sin clasificar')
    df['Sucursal_Cat'] = df['SUCURSAL'].fillna(df['Denominación'])
    
    # Resolver Tipo de orden (viene como fórmula en el Excel, pandas ya la resolvió)
    if df['Tipo de orden'].isna().all():
        df['Tipo de orden'] = df['Orden'].astype(str).apply(
            lambda x: 'Correctivo' if x.startswith('4') else ('Preventivo' if x.startswith('5') else 'Otro')
        )
    
    # Mapear estatus
    estatus_map = {
        'VISA': 'Visado',
        'AUTO': 'Autorizado',
        'ATEN': 'En Atención',
        'REAL': 'Realizado',
        'PRES': 'Presupuestado',
        'ENVI': 'Enviado',
        'NAUT': 'No Autorizado'
    }
    df['Estatus_Desc'] = df['Estatus de Usuario'].map(estatus_map).fillna(df['Estatus de Usuario'])
    
    # Fechas
    for col in ['Fecha de creación', 'Fecha de atención', 'Fecha de realización']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Mes/Año de creación
    df['Mes_Creacion'] = df['Fecha de creación'].dt.to_period('M').astype(str)
    df['Mes_Nombre'] = df['Fecha de creación'].dt.strftime('%b %Y')
    
    # Tiempo de atención (días)
    df['Dias_Atencion'] = (df['Fecha de atención'] - df['Fecha de creación']).dt.days
    df['Dias_Realizacion'] = (df['Fecha de realización'] - df['Fecha de creación']).dt.days
    
    # Grupo de especialidad
    df['Especialidad'] = df['Denominación de la ubicación técnica'].fillna('Sin clasificar')
    
    return df, df_sup


def kpi_card(label, value, sub="", color_class=""):
    """Genera HTML para tarjeta KPI."""
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def format_currency(val):
    """Formatea valor como moneda MXN."""
    if val >= 1_000_000:
        return f"${val/1_000_000:,.1f}M"
    elif val >= 1_000:
        return f"${val/1_000:,.1f}K"
    return f"${val:,.0f}"


BBVA_COLORS = ['#004481', '#0066b2', '#1a8fe3', '#5bbad5', '#00a651', '#7b2d8e',
               '#ff9500', '#e63946', '#0097a7', '#f4a261', '#2a9d8f', '#e76f51']

BBVA_SEQUENTIAL = px.colors.sequential.Blues


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏗️ BBVA Conservación")
    st.markdown("**Región Noreste**")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "📂 Cargar archivo BP (.xlsx)",
        type=['xlsx', 'xls'],
        help="Sube el archivo diario de SAP con las órdenes de mantenimiento"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")


# ══════════════════════════════════════════════════════════════
# PANTALLA PRINCIPAL
# ══════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="main-header">
    <h1>🏗️ BBVA Conservación NE — Centro de Análisis</h1>
    <p>Plataforma integral de análisis de órdenes de mantenimiento · Región Noreste</p>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.info("👈 **Carga el archivo BP del día** en la barra lateral para comenzar el análisis.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        #### 📊 Dashboard General
        Vista ejecutiva con KPIs, gráficos de estatus, 
        distribución por tipo de orden e importes.
        """)
    with col2:
        st.markdown("""
        #### 🏢 Análisis por Proveedor
        Rendimiento individual de cada proveedor: 
        órdenes, importes, tiempos y especialidades.
        """)
    with col3:
        st.markdown("""
        #### 👷 Análisis por Supervisor
        Carga de trabajo, zonas asignadas, distribución 
        de órdenes y eficiencia por supervisor.
        """)
    st.stop()

# ══════════════════════════════════════════════════════════════
# PROCESAMIENTO DE DATOS
# ══════════════════════════════════════════════════════════════
df, df_cat = process_data(uploaded_file)

# ══════════════════════════════════════════════════════════════
# FILTROS EN SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Filtros")
    
    # Tipo de orden
    tipos = ['Todos'] + sorted(df['Tipo de orden'].dropna().unique().tolist())
    sel_tipo = st.selectbox("Tipo de Orden", tipos)
    
    # Estatus
    estatus_opts = ['Todos'] + sorted(df['Estatus_Desc'].dropna().unique().tolist())
    sel_estatus = st.selectbox("Estatus", estatus_opts)
    
    # Supervisor
    supervisores = ['Todos'] + sorted(df['Supervisor_Asignado'].dropna().unique().tolist())
    sel_supervisor = st.selectbox("Supervisor", supervisores)
    
    # Zona
    zonas = ['Todas'] + sorted(df['Zona'].dropna().unique().tolist())
    sel_zona = st.selectbox("Zona (DZ)", zonas)
    
    # Proveedor
    proveedores = ['Todos'] + sorted(df['Proveedor'].dropna().unique().tolist())
    sel_proveedor = st.selectbox("Proveedor", proveedores)
    
    # Rango de fechas
    st.markdown("**Rango de Fechas**")
    fecha_min = df['Fecha de creación'].min()
    fecha_max = df['Fecha de creación'].max()
    if pd.notna(fecha_min) and pd.notna(fecha_max):
        fecha_range = st.date_input(
            "Periodo",
            value=(fecha_min.date(), fecha_max.date()),
            min_value=fecha_min.date(),
            max_value=fecha_max.date()
        )
    else:
        fecha_range = None
    
    # Tipo de banca
    bancas = ['Todas'] + sorted(df['Tipo_Banca'].dropna().unique().tolist())
    sel_banca = st.selectbox("Tipo de Banca", bancas)

# ══════════════════════════════════════════════════════════════
# APLICAR FILTROS
# ══════════════════════════════════════════════════════════════
df_filtered = df.copy()

if sel_tipo != 'Todos':
    df_filtered = df_filtered[df_filtered['Tipo de orden'] == sel_tipo]
if sel_estatus != 'Todos':
    df_filtered = df_filtered[df_filtered['Estatus_Desc'] == sel_estatus]
if sel_supervisor != 'Todos':
    df_filtered = df_filtered[df_filtered['Supervisor_Asignado'] == sel_supervisor]
if sel_zona != 'Todas':
    df_filtered = df_filtered[df_filtered['Zona'] == sel_zona]
if sel_proveedor != 'Todos':
    df_filtered = df_filtered[df_filtered['Proveedor'] == sel_proveedor]
if sel_banca != 'Todas':
    df_filtered = df_filtered[df_filtered['Tipo_Banca'] == sel_banca]
if fecha_range and len(fecha_range) == 2:
    df_filtered = df_filtered[
        (df_filtered['Fecha de creación'].dt.date >= fecha_range[0]) &
        (df_filtered['Fecha de creación'].dt.date <= fecha_range[1])
    ]

# ══════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard General",
    "🏢 Análisis por Proveedor",
    "👷 Análisis por Supervisor",
    "📋 Detalle de Datos"
])

# ══════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD GENERAL
# ══════════════════════════════════════════════════════════════
with tab1:
    total_ordenes = len(df_filtered)
    importe_total = df_filtered['Importe'].sum()
    importe_iva_total = df_filtered['Importe IVA'].sum()
    correctivas = len(df_filtered[df_filtered['Tipo de orden'] == 'Correctivo'])
    preventivas = len(df_filtered[df_filtered['Tipo de orden'] == 'Preventivo'])
    proveedores_activos = df_filtered['Proveedor'].nunique()
    sucursales_atendidas = df_filtered['Denominación'].nunique()
    promedio_orden = importe_total / total_ordenes if total_ordenes > 0 else 0
    
    # KPIs row 1
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kpi_card("Total Órdenes", f"{total_ordenes:,}", f"De {len(df):,} cargadas"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Importe Total", format_currency(importe_total), f"IVA: {format_currency(importe_iva_total)}", "kpi-green"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Correctivas", f"{correctivas:,}", f"{correctivas/total_ordenes*100:.1f}% del total" if total_ordenes else "", "kpi-orange"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Preventivas", f"{preventivas:,}", f"{preventivas/total_ordenes*100:.1f}% del total" if total_ordenes else "", "kpi-cyan"), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("Proveedores", f"{proveedores_activos}", "activos", "kpi-purple"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("Sucursales", f"{sucursales_atendidas}", f"Prom. ${promedio_orden:,.0f}/orden", "kpi-red"), unsafe_allow_html=True)
    
    st.markdown("")
    
    # Row 2: Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Distribución por Estatus
        st.markdown('<div class="section-header">📈 Distribución por Estatus</div>', unsafe_allow_html=True)
        estatus_counts = df_filtered['Estatus_Desc'].value_counts().reset_index()
        estatus_counts.columns = ['Estatus', 'Cantidad']
        fig_est = px.pie(
            estatus_counts, names='Estatus', values='Cantidad',
            color_discrete_sequence=BBVA_COLORS,
            hole=0.45
        )
        fig_est.update_traces(textposition='outside', textinfo='label+value+percent')
        fig_est.update_layout(
            height=380, margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation='h', y=-0.15),
            font=dict(size=12)
        )
        st.plotly_chart(fig_est, use_container_width=True)
    
    with col_right:
        # Tipo de Orden
        st.markdown('<div class="section-header">🔧 Correctivo vs Preventivo</div>', unsafe_allow_html=True)
        tipo_counts = df_filtered['Tipo de orden'].value_counts().reset_index()
        tipo_counts.columns = ['Tipo', 'Cantidad']
        fig_tipo = px.bar(
            tipo_counts, x='Tipo', y='Cantidad', color='Tipo',
            color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'},
            text='Cantidad'
        )
        fig_tipo.update_traces(textposition='outside', textfont_size=14)
        fig_tipo.update_layout(
            height=380, margin=dict(t=20, b=20),
            showlegend=False,
            yaxis_title="Cantidad de Órdenes",
            xaxis_title=""
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    # Row 3
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Órdenes por Zona
        st.markdown('<div class="section-header">🗺️ Órdenes por Zona</div>', unsafe_allow_html=True)
        zona_data = df_filtered.groupby('Zona').agg(
            Ordenes=('Orden', 'count'),
            Importe=('Importe', 'sum')
        ).sort_values('Ordenes', ascending=True).reset_index()
        
        fig_zona = px.bar(
            zona_data, y='Zona', x='Ordenes', orientation='h',
            color='Importe', color_continuous_scale='Blues',
            text='Ordenes'
        )
        fig_zona.update_traces(textposition='outside')
        fig_zona.update_layout(
            height=500, margin=dict(t=20, b=20, l=10),
            xaxis_title="Cantidad", yaxis_title="",
            coloraxis_colorbar_title="Importe"
        )
        st.plotly_chart(fig_zona, use_container_width=True)
    
    with col_b:
        # Top 15 Proveedores por volumen
        st.markdown('<div class="section-header">🏢 Top 15 Proveedores por Volumen</div>', unsafe_allow_html=True)
        prov_data = df_filtered.groupby('Proveedor').agg(
            Ordenes=('Orden', 'count'),
            Importe=('Importe', 'sum')
        ).sort_values('Ordenes', ascending=True).tail(15).reset_index()
        
        fig_prov = px.bar(
            prov_data, y='Proveedor', x='Ordenes', orientation='h',
            color='Importe', color_continuous_scale='Oranges',
            text='Ordenes'
        )
        fig_prov.update_traces(textposition='outside')
        fig_prov.update_layout(
            height=500, margin=dict(t=20, b=20, l=10),
            xaxis_title="Cantidad", yaxis_title="",
            coloraxis_colorbar_title="Importe"
        )
        st.plotly_chart(fig_prov, use_container_width=True)
    
    # Row 4: Temporal + Especialidades
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.markdown('<div class="section-header">📅 Evolución Mensual de Órdenes</div>', unsafe_allow_html=True)
        monthly = df_filtered.groupby(['Mes_Creacion', 'Tipo de orden']).size().reset_index(name='Cantidad')
        monthly = monthly.sort_values('Mes_Creacion')
        fig_monthly = px.bar(
            monthly, x='Mes_Creacion', y='Cantidad', color='Tipo de orden',
            barmode='group',
            color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'},
            text='Cantidad'
        )
        fig_monthly.update_traces(textposition='outside', textfont_size=10)
        fig_monthly.update_layout(
            height=420, margin=dict(t=20, b=20),
            xaxis_title="Mes", yaxis_title="Cantidad",
            legend=dict(orientation='h', y=1.05)
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col_d:
        st.markdown('<div class="section-header">🔩 Top 15 Especialidades</div>', unsafe_allow_html=True)
        esp_data = df_filtered['Especialidad'].value_counts().head(15).reset_index()
        esp_data.columns = ['Especialidad', 'Cantidad']
        fig_esp = px.bar(
            esp_data, x='Cantidad', y='Especialidad', orientation='h',
            color='Cantidad', color_continuous_scale='Teal',
            text='Cantidad'
        )
        fig_esp.update_traces(textposition='outside')
        fig_esp.update_layout(
            height=420, margin=dict(t=20, b=20, l=10),
            xaxis_title="Cantidad", yaxis_title="",
            showlegend=False
        )
        st.plotly_chart(fig_esp, use_container_width=True)
    
    # Row 5: Importe analysis
    st.markdown('<div class="section-header">💰 Análisis de Importes por Zona y Tipo</div>', unsafe_allow_html=True)
    col_e, col_f = st.columns(2)
    
    with col_e:
        imp_zona = df_filtered.groupby(['Zona', 'Tipo de orden'])['Importe'].sum().reset_index()
        fig_imp = px.bar(
            imp_zona, x='Zona', y='Importe', color='Tipo de orden',
            barmode='stack',
            color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'},
            text_auto='.2s'
        )
        fig_imp.update_layout(
            height=400, margin=dict(t=20, b=20),
            xaxis_title="", yaxis_title="Importe ($)",
            xaxis_tickangle=-45,
            legend=dict(orientation='h', y=1.05)
        )
        st.plotly_chart(fig_imp, use_container_width=True)
    
    with col_f:
        # Importe promedio por proveedor (top 10)
        imp_prov = df_filtered.groupby('Proveedor').agg(
            Importe_Total=('Importe', 'sum'),
            Ordenes=('Orden', 'count'),
            Promedio=('Importe', 'mean')
        ).sort_values('Importe_Total', ascending=False).head(10).reset_index()
        
        fig_imp_prov = px.bar(
            imp_prov, x='Proveedor', y='Importe_Total',
            color='Promedio', color_continuous_scale='Reds',
            text_auto='.2s'
        )
        fig_imp_prov.update_layout(
            height=400, margin=dict(t=20, b=20),
            xaxis_title="", yaxis_title="Importe Total ($)",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_imp_prov, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2: ANÁLISIS POR PROVEEDOR
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🏢 Análisis Detallado por Proveedor</div>', unsafe_allow_html=True)
    
    # Selector de proveedor específico
    prov_list = sorted(df_filtered['Proveedor'].dropna().unique().tolist())
    sel_prov_detail = st.selectbox("Selecciona un proveedor para análisis detallado:", prov_list, key='prov_detail')
    
    df_prov = df_filtered[df_filtered['Proveedor'] == sel_prov_detail]
    
    if len(df_prov) == 0:
        st.warning("No hay datos para el proveedor seleccionado con los filtros actuales.")
    else:
        # KPIs del proveedor
        p_total = len(df_prov)
        p_importe = df_prov['Importe'].sum()
        p_importe_iva = df_prov['Importe IVA'].sum()
        p_correctivas = len(df_prov[df_prov['Tipo de orden'] == 'Correctivo'])
        p_preventivas = len(df_prov[df_prov['Tipo de orden'] == 'Preventivo'])
        p_sucursales = df_prov['Denominación'].nunique()
        p_dias_prom = df_prov['Dias_Atencion'].mean()
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.markdown(kpi_card("Órdenes", f"{p_total:,}", f"{p_total/total_ordenes*100:.1f}% del total" if total_ordenes else ""), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Importe Total", format_currency(p_importe), f"IVA: {format_currency(p_importe_iva)}", "kpi-green"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Correctivas", f"{p_correctivas:,}", f"{p_correctivas/p_total*100:.1f}%" if p_total else "", "kpi-orange"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("Preventivas", f"{p_preventivas:,}", f"{p_preventivas/p_total*100:.1f}%" if p_total else "", "kpi-cyan"), unsafe_allow_html=True)
        with c5:
            st.markdown(kpi_card("Sucursales", f"{p_sucursales}", "atendidas", "kpi-purple"), unsafe_allow_html=True)
        with c6:
            dias_txt = f"{p_dias_prom:.1f} días" if pd.notna(p_dias_prom) else "N/D"
            st.markdown(kpi_card("T. Atención Prom.", dias_txt, "días promedio", "kpi-red"), unsafe_allow_html=True)
        
        st.markdown("")
        
        # Charts del proveedor
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown('<div class="section-header">📊 Estatus de Órdenes</div>', unsafe_allow_html=True)
            p_est = df_prov['Estatus_Desc'].value_counts().reset_index()
            p_est.columns = ['Estatus', 'Cantidad']
            fig_p1 = px.pie(p_est, names='Estatus', values='Cantidad', hole=0.45,
                           color_discrete_sequence=BBVA_COLORS)
            fig_p1.update_traces(textposition='outside', textinfo='label+value+percent')
            fig_p1.update_layout(height=350, margin=dict(t=20, b=20), legend=dict(orientation='h', y=-0.15))
            st.plotly_chart(fig_p1, use_container_width=True)
        
        with col_p2:
            st.markdown('<div class="section-header">🗺️ Distribución por Zona</div>', unsafe_allow_html=True)
            p_zona = df_prov['Zona'].value_counts().reset_index()
            p_zona.columns = ['Zona', 'Cantidad']
            fig_p2 = px.bar(p_zona, x='Zona', y='Cantidad', color='Cantidad',
                           color_continuous_scale='Blues', text='Cantidad')
            fig_p2.update_traces(textposition='outside')
            fig_p2.update_layout(height=350, margin=dict(t=20, b=20), xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_p2, use_container_width=True)
        
        col_p3, col_p4 = st.columns(2)
        
        with col_p3:
            st.markdown('<div class="section-header">🔩 Especialidades Atendidas</div>', unsafe_allow_html=True)
            p_esp = df_prov['Especialidad'].value_counts().head(10).reset_index()
            p_esp.columns = ['Especialidad', 'Cantidad']
            fig_p3 = px.bar(p_esp, y='Especialidad', x='Cantidad', orientation='h',
                           color='Cantidad', color_continuous_scale='Teal', text='Cantidad')
            fig_p3.update_traces(textposition='outside')
            fig_p3.update_layout(height=350, margin=dict(t=20, b=20, l=10), showlegend=False)
            st.plotly_chart(fig_p3, use_container_width=True)
        
        with col_p4:
            st.markdown('<div class="section-header">📅 Evolución Mensual</div>', unsafe_allow_html=True)
            p_month = df_prov.groupby(['Mes_Creacion', 'Tipo de orden']).size().reset_index(name='Cantidad')
            p_month = p_month.sort_values('Mes_Creacion')
            fig_p4 = px.line(p_month, x='Mes_Creacion', y='Cantidad', color='Tipo de orden',
                            markers=True,
                            color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'})
            fig_p4.update_layout(height=350, margin=dict(t=20, b=20),
                                legend=dict(orientation='h', y=1.05))
            st.plotly_chart(fig_p4, use_container_width=True)
        
        # Supervisores que trabajan con este proveedor
        st.markdown('<div class="section-header">👷 Supervisores Asociados</div>', unsafe_allow_html=True)
        p_sup = df_prov.groupby('Supervisor_Asignado').agg(
            Ordenes=('Orden', 'count'),
            Importe=('Importe', 'sum'),
            Sucursales=('Denominación', 'nunique')
        ).sort_values('Ordenes', ascending=False).reset_index()
        p_sup['Importe_Fmt'] = p_sup['Importe'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(
            p_sup.rename(columns={'Supervisor_Asignado': 'Supervisor'}),
            use_container_width=True, hide_index=True,
            column_config={
                "Importe": st.column_config.NumberColumn(format="$%,.2f"),
            }
        )
    
    # Comparativa de proveedores
    st.markdown('<div class="section-header">⚖️ Comparativa General de Proveedores</div>', unsafe_allow_html=True)
    
    comp_prov = df_filtered.groupby('Proveedor').agg(
        Total_Ordenes=('Orden', 'count'),
        Importe_Total=('Importe', 'sum'),
        Importe_IVA=('Importe IVA', 'sum'),
        Importe_Promedio=('Importe', 'mean'),
        Correctivas=('Tipo de orden', lambda x: (x == 'Correctivo').sum()),
        Preventivas=('Tipo de orden', lambda x: (x == 'Preventivo').sum()),
        Sucursales=('Denominación', 'nunique'),
        Zonas=('Zona', 'nunique'),
        Dias_Atencion_Prom=('Dias_Atencion', 'mean')
    ).sort_values('Total_Ordenes', ascending=False).reset_index()
    
    comp_prov['% Correctivas'] = (comp_prov['Correctivas'] / comp_prov['Total_Ordenes'] * 100).round(1)
    comp_prov['% Preventivas'] = (comp_prov['Preventivas'] / comp_prov['Total_Ordenes'] * 100).round(1)
    
    st.dataframe(
        comp_prov,
        use_container_width=True, hide_index=True,
        column_config={
            "Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f"),
            "Importe_IVA": st.column_config.NumberColumn("Importe IVA", format="$%,.2f"),
            "Importe_Promedio": st.column_config.NumberColumn("Importe Prom.", format="$%,.2f"),
            "Dias_Atencion_Prom": st.column_config.NumberColumn("Días Atención", format="%.1f"),
            "% Correctivas": st.column_config.NumberColumn(format="%.1f%%"),
            "% Preventivas": st.column_config.NumberColumn(format="%.1f%%"),
        }
    )


# ══════════════════════════════════════════════════════════════
# TAB 3: ANÁLISIS POR SUPERVISOR
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">👷 Análisis Detallado por Supervisor</div>', unsafe_allow_html=True)
    
    # Selector de supervisor
    sup_list = sorted(df_filtered['Supervisor_Asignado'].dropna().unique().tolist())
    sel_sup_detail = st.selectbox("Selecciona un supervisor para análisis detallado:", sup_list, key='sup_detail')
    
    df_sup_detail = df_filtered[df_filtered['Supervisor_Asignado'] == sel_sup_detail]
    
    if len(df_sup_detail) == 0:
        st.warning("No hay datos para el supervisor seleccionado con los filtros actuales.")
    else:
        # KPIs del supervisor
        s_total = len(df_sup_detail)
        s_importe = df_sup_detail['Importe'].sum()
        s_importe_iva = df_sup_detail['Importe IVA'].sum()
        s_correctivas = len(df_sup_detail[df_sup_detail['Tipo de orden'] == 'Correctivo'])
        s_preventivas = len(df_sup_detail[df_sup_detail['Tipo de orden'] == 'Preventivo'])
        s_proveedores = df_sup_detail['Proveedor'].nunique()
        s_sucursales = df_sup_detail['Denominación'].nunique()
        s_zonas_list = df_sup_detail['Zona'].unique()
        s_dias_prom = df_sup_detail['Dias_Atencion'].mean()
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.markdown(kpi_card("Órdenes", f"{s_total:,}", f"{s_total/total_ordenes*100:.1f}% del total" if total_ordenes else ""), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Importe Total", format_currency(s_importe), f"IVA: {format_currency(s_importe_iva)}", "kpi-green"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Correctivas", f"{s_correctivas:,}", f"{s_correctivas/s_total*100:.1f}%" if s_total else "", "kpi-orange"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("Preventivas", f"{s_preventivas:,}", f"{s_preventivas/s_total*100:.1f}%" if s_total else "", "kpi-cyan"), unsafe_allow_html=True)
        with c5:
            st.markdown(kpi_card("Proveedores", f"{s_proveedores}", "asignados", "kpi-purple"), unsafe_allow_html=True)
        with c6:
            st.markdown(kpi_card("Sucursales", f"{s_sucursales}", f"en {len(s_zonas_list)} zona(s)", "kpi-red"), unsafe_allow_html=True)
        
        st.markdown("")
        
        # Zonas del supervisor
        st.info(f"🗺️ **Zona(s) asignada(s):** {', '.join(s_zonas_list)}")
        
        # Charts del supervisor
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.markdown('<div class="section-header">📊 Estatus de Órdenes</div>', unsafe_allow_html=True)
            s_est = df_sup_detail['Estatus_Desc'].value_counts().reset_index()
            s_est.columns = ['Estatus', 'Cantidad']
            fig_s1 = px.pie(s_est, names='Estatus', values='Cantidad', hole=0.45,
                           color_discrete_sequence=BBVA_COLORS)
            fig_s1.update_traces(textposition='outside', textinfo='label+value+percent')
            fig_s1.update_layout(height=350, margin=dict(t=20, b=20), legend=dict(orientation='h', y=-0.15))
            st.plotly_chart(fig_s1, use_container_width=True)
        
        with col_s2:
            st.markdown('<div class="section-header">🏢 Top 10 Proveedores</div>', unsafe_allow_html=True)
            s_prov = df_sup_detail.groupby('Proveedor').agg(
                Ordenes=('Orden', 'count'),
                Importe=('Importe', 'sum')
            ).sort_values('Ordenes', ascending=True).tail(10).reset_index()
            fig_s2 = px.bar(s_prov, y='Proveedor', x='Ordenes', orientation='h',
                           color='Importe', color_continuous_scale='Oranges', text='Ordenes')
            fig_s2.update_traces(textposition='outside')
            fig_s2.update_layout(height=350, margin=dict(t=20, b=20, l=10))
            st.plotly_chart(fig_s2, use_container_width=True)
        
        col_s3, col_s4 = st.columns(2)
        
        with col_s3:
            st.markdown('<div class="section-header">🔩 Especialidades</div>', unsafe_allow_html=True)
            s_esp = df_sup_detail['Especialidad'].value_counts().head(10).reset_index()
            s_esp.columns = ['Especialidad', 'Cantidad']
            fig_s3 = px.bar(s_esp, y='Especialidad', x='Cantidad', orientation='h',
                           color='Cantidad', color_continuous_scale='Teal', text='Cantidad')
            fig_s3.update_traces(textposition='outside')
            fig_s3.update_layout(height=350, margin=dict(t=20, b=20, l=10), showlegend=False)
            st.plotly_chart(fig_s3, use_container_width=True)
        
        with col_s4:
            st.markdown('<div class="section-header">📅 Evolución Mensual</div>', unsafe_allow_html=True)
            s_month = df_sup_detail.groupby(['Mes_Creacion', 'Tipo de orden']).size().reset_index(name='Cantidad')
            s_month = s_month.sort_values('Mes_Creacion')
            fig_s4 = px.line(s_month, x='Mes_Creacion', y='Cantidad', color='Tipo de orden',
                            markers=True,
                            color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'})
            fig_s4.update_layout(height=350, margin=dict(t=20, b=20),
                                legend=dict(orientation='h', y=1.05))
            st.plotly_chart(fig_s4, use_container_width=True)
        
        # Importe por mes para el supervisor
        st.markdown('<div class="section-header">💰 Importes por Mes y Tipo de Orden</div>', unsafe_allow_html=True)
        col_s5, col_s6 = st.columns(2)
        
        with col_s5:
            s_imp_mes = df_sup_detail.groupby(['Mes_Creacion', 'Tipo de orden'])['Importe'].sum().reset_index()
            s_imp_mes = s_imp_mes.sort_values('Mes_Creacion')
            fig_s5 = px.bar(s_imp_mes, x='Mes_Creacion', y='Importe', color='Tipo de orden',
                           barmode='group',
                           color_discrete_map={'Correctivo': '#e63946', 'Preventivo': '#0097a7'},
                           text_auto='.2s')
            fig_s5.update_layout(height=380, margin=dict(t=20, b=20),
                                xaxis_title="Mes", yaxis_title="Importe ($)",
                                legend=dict(orientation='h', y=1.05))
            st.plotly_chart(fig_s5, use_container_width=True)
        
        with col_s6:
            # Sucursales con más órdenes
            s_suc = df_sup_detail.groupby('Denominación').agg(
                Ordenes=('Orden', 'count'),
                Importe=('Importe', 'sum')
            ).sort_values('Ordenes', ascending=True).tail(10).reset_index()
            fig_s6 = px.bar(s_suc, y='Denominación', x='Ordenes', orientation='h',
                           color='Importe', color_continuous_scale='Blues', text='Ordenes')
            fig_s6.update_traces(textposition='outside')
            fig_s6.update_layout(height=380, margin=dict(t=20, b=20, l=10),
                                xaxis_title="Órdenes", yaxis_title="")
            st.plotly_chart(fig_s6, use_container_width=True)
        
        # Tabla detalle de sucursales del supervisor
        st.markdown('<div class="section-header">📋 Detalle de Sucursales Asignadas</div>', unsafe_allow_html=True)
        s_suc_detail = df_sup_detail.groupby(['Denominación', 'Centro de coste', 'Zona']).agg(
            Total_Ordenes=('Orden', 'count'),
            Correctivas=('Tipo de orden', lambda x: (x == 'Correctivo').sum()),
            Preventivas=('Tipo de orden', lambda x: (x == 'Preventivo').sum()),
            Importe_Total=('Importe', 'sum'),
        ).sort_values('Total_Ordenes', ascending=False).reset_index()
        
        st.dataframe(
            s_suc_detail.rename(columns={'Denominación': 'Sucursal'}),
            use_container_width=True, hide_index=True,
            column_config={
                "Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f"),
            }
        )
    
    # ── Comparativa de todos los supervisores ──
    st.markdown('<div class="section-header">⚖️ Comparativa General de Supervisores</div>', unsafe_allow_html=True)
    
    comp_sup = df_filtered.groupby('Supervisor_Asignado').agg(
        Total_Ordenes=('Orden', 'count'),
        Importe_Total=('Importe', 'sum'),
        Importe_IVA=('Importe IVA', 'sum'),
        Importe_Promedio=('Importe', 'mean'),
        Correctivas=('Tipo de orden', lambda x: (x == 'Correctivo').sum()),
        Preventivas=('Tipo de orden', lambda x: (x == 'Preventivo').sum()),
        Proveedores=('Proveedor', 'nunique'),
        Sucursales=('Denominación', 'nunique'),
        Zonas=('Zona', 'nunique'),
        Dias_Atencion_Prom=('Dias_Atencion', 'mean')
    ).sort_values('Total_Ordenes', ascending=False).reset_index()
    
    comp_sup['% Correctivas'] = (comp_sup['Correctivas'] / comp_sup['Total_Ordenes'] * 100).round(1)
    comp_sup['% Preventivas'] = (comp_sup['Preventivas'] / comp_sup['Total_Ordenes'] * 100).round(1)
    
    st.dataframe(
        comp_sup.rename(columns={'Supervisor_Asignado': 'Supervisor'}),
        use_container_width=True, hide_index=True,
        column_config={
            "Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f"),
            "Importe_IVA": st.column_config.NumberColumn("Importe IVA", format="$%,.2f"),
            "Importe_Promedio": st.column_config.NumberColumn("Importe Prom.", format="$%,.2f"),
            "Dias_Atencion_Prom": st.column_config.NumberColumn("Días Atención", format="%.1f"),
            "% Correctivas": st.column_config.NumberColumn(format="%.1f%%"),
            "% Preventivas": st.column_config.NumberColumn(format="%.1f%%"),
        }
    )
    
    # Gráficos comparativos
    st.markdown("")
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        st.markdown('<div class="section-header">📊 Carga de Trabajo por Supervisor</div>', unsafe_allow_html=True)
        fig_comp1 = px.bar(
            comp_sup.sort_values('Total_Ordenes', ascending=True),
            y='Supervisor_Asignado', x='Total_Ordenes', orientation='h',
            color='Importe_Total', color_continuous_scale='Blues',
            text='Total_Ordenes'
        )
        fig_comp1.update_traces(textposition='outside')
        fig_comp1.update_layout(
            height=450, margin=dict(t=20, b=20, l=10),
            yaxis_title="", xaxis_title="Total de Órdenes",
            coloraxis_colorbar_title="Importe Total"
        )
        st.plotly_chart(fig_comp1, use_container_width=True)
    
    with col_comp2:
        st.markdown('<div class="section-header">🔧 Correctivas vs Preventivas por Supervisor</div>', unsafe_allow_html=True)
        comp_melt = comp_sup.melt(
            id_vars='Supervisor_Asignado',
            value_vars=['Correctivas', 'Preventivas'],
            var_name='Tipo', value_name='Cantidad'
        )
        fig_comp2 = px.bar(
            comp_melt.sort_values('Supervisor_Asignado'),
            y='Supervisor_Asignado', x='Cantidad', color='Tipo',
            orientation='h', barmode='group',
            color_discrete_map={'Correctivas': '#e63946', 'Preventivas': '#0097a7'},
            text='Cantidad'
        )
        fig_comp2.update_traces(textposition='outside')
        fig_comp2.update_layout(
            height=450, margin=dict(t=20, b=20, l=10),
            yaxis_title="", xaxis_title="Cantidad",
            legend=dict(orientation='h', y=1.05)
        )
        st.plotly_chart(fig_comp2, use_container_width=True)
    
    # Heatmap: Supervisor x Zona
    st.markdown('<div class="section-header">🗺️ Mapa de Calor: Supervisor × Zona</div>', unsafe_allow_html=True)
    heatmap_data = df_filtered.groupby(['Supervisor_Asignado', 'Zona']).size().reset_index(name='Ordenes')
    heatmap_pivot = heatmap_data.pivot_table(index='Supervisor_Asignado', columns='Zona', values='Ordenes', fill_value=0)
    
    fig_heat = px.imshow(
        heatmap_pivot, text_auto=True,
        color_continuous_scale='Blues',
        aspect='auto'
    )
    fig_heat.update_layout(
        height=400, margin=dict(t=20, b=20),
        xaxis_title="Zona", yaxis_title="Supervisor"
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4: DETALLE DE DATOS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📋 Base de Datos Completa (Filtrada)</div>', unsafe_allow_html=True)
    
    st.markdown(f"**{len(df_filtered):,} registros** mostrados de {len(df):,} totales")
    
    # Columnas a mostrar
    cols_display = [
        'Orden', 'Tipo de orden', 'Proveedor', 'Supervisor_Asignado',
        'Centro de coste', 'Denominación', 'Zona', 'Tipo_Banca',
        'Texto breve de la orden', 'Estatus_Desc', 'Importe', 'Importe IVA',
        'Fecha de creación', 'Fecha de atención', 'Fecha de realización',
        'Especialidad', 'Texto de avería', 'Grupo códigos'
    ]
    cols_available = [c for c in cols_display if c in df_filtered.columns]
    
    # Búsqueda en tabla
    search = st.text_input("🔍 Buscar en la tabla (orden, sucursal, proveedor, etc.):", key='table_search')
    
    df_display = df_filtered[cols_available].copy()
    
    if search:
        mask = df_display.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        df_display = df_display[mask]
        st.markdown(f"*{len(df_display)} resultados encontrados*")
    
    st.dataframe(
        df_display.rename(columns={
            'Supervisor_Asignado': 'Supervisor',
            'Estatus_Desc': 'Estatus',
            'Tipo_Banca': 'Tipo Banca'
        }),
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "Importe": st.column_config.NumberColumn(format="$%,.2f"),
            "Importe IVA": st.column_config.NumberColumn(format="$%,.2f"),
            "Fecha de creación": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Fecha de atención": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Fecha de realización": st.column_config.DateColumn(format="DD/MM/YYYY"),
        }
    )
    
    # Descargar datos filtrados
    st.markdown("")
    col_dl1, col_dl2, _ = st.columns([1, 1, 2])
    with col_dl1:
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Descargar CSV",
            csv,
            f"BP_filtrado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    with col_dl2:
        # Resumen estadístico
        with st.expander("📊 Resumen Estadístico"):
            st.write(df_filtered[['Importe', 'Importe IVA', 'Dias_Atencion']].describe().round(2))


# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    """<div style="text-align:center; color:#999; font-size:0.75rem; padding:0.5rem;">
    BBVA Conservación NE · Centro de Análisis · Desarrollado para la Dirección de Administración y Operaciones
    </div>""",
    unsafe_allow_html=True
)
