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
    .main .block-container { padding: 1rem 2rem; max-width: 100%; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #004481 0%, #002855 100%); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { font-weight: 600; font-size: 0.85rem; letter-spacing: 0.3px; }
    .main-header {
        background: linear-gradient(135deg, #004481 0%, #0066b2 50%, #1a8fe3 100%);
        padding: 1.5rem 2rem; border-radius: 12px; color: white;
        margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,68,129,0.3);
    }
    .main-header h1 { margin: 0; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.5px; }
    .main-header p { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.9rem; }
    .kpi-card {
        background: #ffffff; border-radius: 12px; padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-left: 4px solid #004481;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
    .kpi-card .kpi-value { font-size: 2rem; font-weight: 800; color: #004481; line-height: 1.1; }
    .kpi-card .kpi-label { font-size: 0.78rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.2rem; }
    .kpi-card .kpi-sub { font-size: 0.75rem; color: #999; margin-top: 0.3rem; }
    .kpi-green { border-left-color: #00a651; } .kpi-green .kpi-value { color: #00a651; }
    .kpi-orange { border-left-color: #ff9500; } .kpi-orange .kpi-value { color: #ff9500; }
    .kpi-red { border-left-color: #e63946; } .kpi-red .kpi-value { color: #e63946; }
    .kpi-purple { border-left-color: #7b2d8e; } .kpi-purple .kpi-value { color: #7b2d8e; }
    .kpi-cyan { border-left-color: #0097a7; } .kpi-cyan .kpi-value { color: #0097a7; }
    .section-header {
        background: linear-gradient(90deg, #f0f6ff, #ffffff); padding: 0.8rem 1.2rem;
        border-radius: 8px; border-left: 4px solid #004481; margin: 1.5rem 0 1rem;
        font-size: 1.1rem; font-weight: 700; color: #002855;
    }
    .login-box {
        max-width: 420px; margin: 8vh auto; background: white; border-radius: 16px;
        padding: 2.5rem; box-shadow: 0 8px 30px rgba(0,68,129,0.15); text-align: center;
    }
    .login-box h2 { color: #002855; margin: 0.5rem 0 0.3rem; font-size: 1.5rem; }
    .login-box p { color: #666; margin: 0 0 1.5rem; font-size: 0.9rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background: #f0f4f8; border-radius: 8px 8px 0 0; padding: 8px 20px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: #004481 !important; color: white !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SISTEMA DE AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════
USUARIOS = {
    "admin": {"password": "Conservacion2025!", "nombre": "Administrador", "rol": "admin"},
    "isabel": {"password": "BBVA_NE2025", "nombre": "Isabel", "rol": "admin"},
    "supervisor": {"password": "Super2025", "nombre": "Supervisor", "rol": "supervisor"},
    "consulta": {"password": "Consulta2025", "nombre": "Consulta", "rol": "consulta"},
}


def login_screen():
    st.markdown("""
    <style>[data-testid="stSidebar"] { display: none; }</style>
    <div style="position:fixed;top:0;left:0;right:0;bottom:0;
        background:linear-gradient(135deg,#001d3d 0%,#003566 30%,#004481 60%,#0066b2 100%);z-index:-1;"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-box">
        <div style="font-size:3rem;margin-bottom:0.5rem;">🏗️</div>
        <h2>BBVA Conservación NE</h2>
        <p>Centro de Análisis · Región Noreste</p>
    </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1.5, 1, 1.5])
    with col_center:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            if submit:
                usuario_lower = usuario.strip().lower()
                if usuario_lower in USUARIOS and USUARIOS[usuario_lower]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user = usuario_lower
                    st.session_state.user_name = USUARIOS[usuario_lower]["nombre"]
                    st.session_state.user_rol = USUARIOS[usuario_lower]["rol"]
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
    st.stop()


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE PROCESAMIENTO
# ══════════════════════════════════════════════════════════════
@st.cache_data
def process_data(uploaded_file):
    df_bp = pd.read_excel(uploaded_file, sheet_name=0)
    df_sup = pd.read_excel(uploaded_file, sheet_name=1)

    # Limpiar Sheet2
    df_sup.columns = df_sup.columns.str.strip()
    df_sup['CR'] = pd.to_numeric(df_sup['CR'], errors='coerce')
    df_sup = df_sup.dropna(subset=['CR'])
    df_sup = df_sup.drop_duplicates(subset='CR', keep='first')

    # Limpiar Sheet1
    df_bp.columns = df_bp.columns.str.strip()
    col_rename = {c: 'Proveedor' for c in df_bp.columns if 'Proveedor' in c}
    df_bp = df_bp.rename(columns=col_rename)

    # Extraer CR del Centro de coste
    df_bp['CR_num'] = pd.to_numeric(
        df_bp['Centro de coste'].astype(str).str.replace('MX11', '', regex=False).str.replace('MX', '', regex=False),
        errors='coerce'
    )

    # Vincular
    df = df_bp.merge(
        df_sup[['CR', 'SUCURSAL', 'TIPO DE BANCA', 'BCA SEGMENTADA', 'DZ', 'SUPERVISOR']],
        left_on='CR_num', right_on='CR', how='left', suffixes=('', '_cat')
    )

    df['Supervisor_Asignado'] = df['SUPERVISOR'].fillna('Sin asignar')
    df['Zona'] = df['DZ'].fillna('Sin zona')
    df['Tipo_Banca'] = df.get('TIPO DE BANCA', pd.Series(dtype=str)).fillna('Sin clasificar')
    df['Sucursal_Cat'] = df.get('SUCURSAL', pd.Series(dtype=str)).fillna(df.get('Denominación', ''))

    # Tipo de orden
    if 'Tipo de orden' not in df.columns or df['Tipo de orden'].isna().all():
        df['Tipo de orden'] = df['Orden'].astype(str).apply(
            lambda x: 'Correctivo' if x.startswith('4') else ('Preventivo' if x.startswith('5') else 'Otro'))
    else:
        mask = df['Tipo de orden'].astype(str).str.startswith('=')
        if mask.any():
            df.loc[mask, 'Tipo de orden'] = df.loc[mask, 'Orden'].astype(str).apply(
                lambda x: 'Correctivo' if x.startswith('4') else ('Preventivo' if x.startswith('5') else 'Otro'))

    estatus_map = {'VISA': 'Visado', 'AUTO': 'Autorizado', 'ATEN': 'En Atención',
                   'REAL': 'Realizado', 'PRES': 'Presupuestado', 'ENVI': 'Enviado', 'NAUT': 'No Autorizado'}
    df['Estatus_Desc'] = df['Estatus de Usuario'].map(estatus_map).fillna(df['Estatus de Usuario'])

    for col in ['Fecha de creación', 'Fecha de atención', 'Fecha de realización']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    df['Mes_Creacion'] = df['Fecha de creación'].dt.to_period('M').astype(str)
    df['Mes_Nombre'] = df['Fecha de creación'].dt.strftime('%b %Y')
    df['Dias_Atencion'] = (df['Fecha de atención'] - df['Fecha de creación']).dt.days
    df['Dias_Realizacion'] = (df['Fecha de realización'] - df['Fecha de creación']).dt.days
    df['Especialidad'] = df.get('Denominación de la ubicación técnica', pd.Series(dtype=str)).fillna('Sin clasificar')

    return df, df_sup


def kpi_card(label, value, sub="", color_class=""):
    return f'<div class="kpi-card {color_class}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'

def format_currency(val):
    if val >= 1_000_000: return f"${val/1_000_000:,.1f}M"
    if val >= 1_000: return f"${val/1_000:,.1f}K"
    return f"${val:,.0f}"

BBVA_COLORS = ['#004481','#0066b2','#1a8fe3','#5bbad5','#00a651','#7b2d8e','#ff9500','#e63946','#0097a7','#f4a261','#2a9d8f','#e76f51']


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏗️ BBVA Conservación")
    st.markdown("**Región Noreste**")
    st.markdown(f"👤 *{st.session_state.get('user_name', '')}*")
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Cargar archivo BP (.xlsx)", type=['xlsx', 'xls'],
                                     help="Sube el archivo diario de SAP")
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Header
st.markdown("""
<div class="main-header">
    <h1>🏗️ BBVA Conservación NE — Centro de Análisis</h1>
    <p>Plataforma integral de análisis de órdenes de mantenimiento · Región Noreste</p>
</div>""", unsafe_allow_html=True)

if not uploaded_file:
    st.info("👈 **Carga el archivo BP del día** en la barra lateral para comenzar el análisis.")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("#### 📊 Dashboard General\nVista ejecutiva con KPIs, gráficos de estatus, distribución por tipo de orden e importes.")
    with c2: st.markdown("#### 🏢 Análisis por Proveedor\nRendimiento individual: órdenes, importes, tiempos y especialidades.")
    with c3: st.markdown("#### 👷 Análisis por Supervisor\nCarga de trabajo, zonas, distribución de órdenes y eficiencia.")
    st.stop()

# Procesar datos
df, df_cat = process_data(uploaded_file)

# Filtros
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Filtros")
    sel_tipo = st.selectbox("Tipo de Orden", ['Todos'] + sorted(df['Tipo de orden'].dropna().unique().tolist()))
    sel_estatus = st.selectbox("Estatus", ['Todos'] + sorted(df['Estatus_Desc'].dropna().unique().tolist()))
    sel_supervisor = st.selectbox("Supervisor", ['Todos'] + sorted(df['Supervisor_Asignado'].dropna().unique().tolist()))
    sel_zona = st.selectbox("Zona (DZ)", ['Todas'] + sorted(df['Zona'].dropna().unique().tolist()))
    sel_proveedor = st.selectbox("Proveedor", ['Todos'] + sorted(df['Proveedor'].dropna().unique().tolist()))
    st.markdown("**Rango de Fechas**")
    fmin, fmax = df['Fecha de creación'].min(), df['Fecha de creación'].max()
    fecha_range = None
    if pd.notna(fmin) and pd.notna(fmax):
        fecha_range = st.date_input("Periodo", value=(fmin.date(), fmax.date()), min_value=fmin.date(), max_value=fmax.date())
    sel_banca = st.selectbox("Tipo de Banca", ['Todas'] + sorted(df['Tipo_Banca'].dropna().unique().tolist()))

# Aplicar filtros
dff = df.copy()
if sel_tipo != 'Todos': dff = dff[dff['Tipo de orden'] == sel_tipo]
if sel_estatus != 'Todos': dff = dff[dff['Estatus_Desc'] == sel_estatus]
if sel_supervisor != 'Todos': dff = dff[dff['Supervisor_Asignado'] == sel_supervisor]
if sel_zona != 'Todas': dff = dff[dff['Zona'] == sel_zona]
if sel_proveedor != 'Todos': dff = dff[dff['Proveedor'] == sel_proveedor]
if sel_banca != 'Todas': dff = dff[dff['Tipo_Banca'] == sel_banca]
if fecha_range and len(fecha_range) == 2:
    dff = dff[(dff['Fecha de creación'].dt.date >= fecha_range[0]) & (dff['Fecha de creación'].dt.date <= fecha_range[1])]

total_ordenes = len(dff)

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard General", "🏢 Análisis por Proveedor", "👷 Análisis por Supervisor", "📋 Detalle de Datos"])

# ── TAB 1: DASHBOARD GENERAL ──
with tab1:
    if total_ordenes == 0:
        st.warning("No hay datos con los filtros seleccionados.")
    else:
        imp_total = dff['Importe'].sum()
        imp_iva = dff['Importe IVA'].sum()
        n_corr = (dff['Tipo de orden'] == 'Correctivo').sum()
        n_prev = (dff['Tipo de orden'] == 'Preventivo').sum()
        n_prov = dff['Proveedor'].nunique()
        n_suc = dff['Denominación'].nunique()
        prom = imp_total / total_ordenes

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.markdown(kpi_card("Total Órdenes", f"{total_ordenes:,}", f"De {len(df):,} cargadas"), True)
        c2.markdown(kpi_card("Importe Total", format_currency(imp_total), f"IVA: {format_currency(imp_iva)}", "kpi-green"), True)
        c3.markdown(kpi_card("Correctivas", f"{n_corr:,}", f"{n_corr/total_ordenes*100:.1f}%", "kpi-orange"), True)
        c4.markdown(kpi_card("Preventivas", f"{n_prev:,}", f"{n_prev/total_ordenes*100:.1f}%", "kpi-cyan"), True)
        c5.markdown(kpi_card("Proveedores", f"{n_prov}", "activos", "kpi-purple"), True)
        c6.markdown(kpi_card("Sucursales", f"{n_suc}", f"Prom. ${prom:,.0f}/orden", "kpi-red"), True)
        st.markdown("")

        cl, cr = st.columns(2)
        with cl:
            st.markdown('<div class="section-header">📈 Distribución por Estatus</div>', True)
            ed = dff['Estatus_Desc'].value_counts().reset_index(); ed.columns = ['Estatus','Cantidad']
            fig = px.pie(ed, names='Estatus', values='Cantidad', color_discrete_sequence=BBVA_COLORS, hole=0.45)
            fig.update_traces(textposition='outside', textinfo='label+value+percent')
            fig.update_layout(height=380, margin=dict(t=20,b=20,l=20,r=20), legend=dict(orientation='h',y=-0.15))
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            st.markdown('<div class="section-header">🔧 Correctivo vs Preventivo</div>', True)
            td = dff['Tipo de orden'].value_counts().reset_index(); td.columns = ['Tipo','Cantidad']
            fig = px.bar(td, x='Tipo', y='Cantidad', color='Tipo', color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'}, text='Cantidad')
            fig.update_traces(textposition='outside', textfont_size=14)
            fig.update_layout(height=380, margin=dict(t=20,b=20), showlegend=False, yaxis_title="Cantidad", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="section-header">🗺️ Órdenes por Zona</div>', True)
            zd = dff.groupby('Zona').agg(Ordenes=('Orden','count'), Importe=('Importe','sum')).sort_values('Ordenes', ascending=True).reset_index()
            fig = px.bar(zd, y='Zona', x='Ordenes', orientation='h', color='Importe', color_continuous_scale='Blues', text='Ordenes')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=500, margin=dict(t=20,b=20,l=10), xaxis_title="Cantidad", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with cb:
            st.markdown('<div class="section-header">🏢 Top 15 Proveedores</div>', True)
            pd2 = dff.groupby('Proveedor').agg(Ordenes=('Orden','count'), Importe=('Importe','sum')).sort_values('Ordenes', ascending=True).tail(15).reset_index()
            fig = px.bar(pd2, y='Proveedor', x='Ordenes', orientation='h', color='Importe', color_continuous_scale='Oranges', text='Ordenes')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=500, margin=dict(t=20,b=20,l=10), xaxis_title="Cantidad", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        cc, cd = st.columns(2)
        with cc:
            st.markdown('<div class="section-header">📅 Evolución Mensual</div>', True)
            md = dff.groupby(['Mes_Creacion','Tipo de orden']).size().reset_index(name='Cantidad').sort_values('Mes_Creacion')
            fig = px.bar(md, x='Mes_Creacion', y='Cantidad', color='Tipo de orden', barmode='group',
                        color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'}, text='Cantidad')
            fig.update_traces(textposition='outside', textfont_size=10)
            fig.update_layout(height=420, margin=dict(t=20,b=20), xaxis_title="Mes", yaxis_title="Cantidad", legend=dict(orientation='h',y=1.05))
            st.plotly_chart(fig, use_container_width=True)
        with cd:
            st.markdown('<div class="section-header">🔩 Top 15 Especialidades</div>', True)
            ed2 = dff['Especialidad'].value_counts().head(15).reset_index(); ed2.columns = ['Especialidad','Cantidad']
            fig = px.bar(ed2, x='Cantidad', y='Especialidad', orientation='h', color='Cantidad', color_continuous_scale='Teal', text='Cantidad')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=420, margin=dict(t=20,b=20,l=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">💰 Análisis de Importes</div>', True)
        ce, cf = st.columns(2)
        with ce:
            iz = dff.groupby(['Zona','Tipo de orden'])['Importe'].sum().reset_index()
            fig = px.bar(iz, x='Zona', y='Importe', color='Tipo de orden', barmode='stack',
                        color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'}, text_auto='.2s')
            fig.update_layout(height=400, margin=dict(t=20,b=20), xaxis_tickangle=-45, legend=dict(orientation='h',y=1.05))
            st.plotly_chart(fig, use_container_width=True)
        with cf:
            ip = dff.groupby('Proveedor').agg(Importe_Total=('Importe','sum'), Ordenes=('Orden','count'), Promedio=('Importe','mean')).sort_values('Importe_Total', ascending=False).head(10).reset_index()
            fig = px.bar(ip, x='Proveedor', y='Importe_Total', color='Promedio', color_continuous_scale='Reds', text_auto='.2s')
            fig.update_layout(height=400, margin=dict(t=20,b=20), xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)


# ── TAB 2: PROVEEDOR ──
with tab2:
    st.markdown('<div class="section-header">🏢 Análisis Detallado por Proveedor</div>', True)
    prov_list = sorted(dff['Proveedor'].dropna().unique().tolist())
    if not prov_list:
        st.warning("No hay proveedores con los filtros actuales.")
    else:
        sel_pv = st.selectbox("Selecciona un proveedor:", prov_list, key='pv')
        dpv = dff[dff['Proveedor'] == sel_pv]
        if len(dpv) == 0:
            st.warning("Sin datos para este proveedor.")
        else:
            pt = len(dpv); pi = dpv['Importe'].sum(); pii = dpv['Importe IVA'].sum()
            pc = (dpv['Tipo de orden']=='Correctivo').sum(); pp = (dpv['Tipo de orden']=='Preventivo').sum()
            ps = dpv['Denominación'].nunique(); pda = dpv['Dias_Atencion'].mean()
            c1,c2,c3,c4,c5,c6 = st.columns(6)
            c1.markdown(kpi_card("Órdenes", f"{pt:,}", f"{pt/total_ordenes*100:.1f}%" if total_ordenes else ""), True)
            c2.markdown(kpi_card("Importe", format_currency(pi), f"IVA: {format_currency(pii)}", "kpi-green"), True)
            c3.markdown(kpi_card("Correctivas", f"{pc:,}", f"{pc/pt*100:.1f}%", "kpi-orange"), True)
            c4.markdown(kpi_card("Preventivas", f"{pp:,}", f"{pp/pt*100:.1f}%", "kpi-cyan"), True)
            c5.markdown(kpi_card("Sucursales", f"{ps}", "atendidas", "kpi-purple"), True)
            c6.markdown(kpi_card("T. Atención", f"{pda:.1f} días" if pd.notna(pda) else "N/D", "promedio", "kpi-red"), True)
            st.markdown("")

            cp1, cp2 = st.columns(2)
            with cp1:
                st.markdown('<div class="section-header">📊 Estatus</div>', True)
                pe = dpv['Estatus_Desc'].value_counts().reset_index(); pe.columns = ['Estatus','Cantidad']
                fig = px.pie(pe, names='Estatus', values='Cantidad', hole=0.45, color_discrete_sequence=BBVA_COLORS)
                fig.update_traces(textposition='outside', textinfo='label+value+percent')
                fig.update_layout(height=350, margin=dict(t=20,b=20), legend=dict(orientation='h',y=-0.15))
                st.plotly_chart(fig, use_container_width=True)
            with cp2:
                st.markdown('<div class="section-header">🗺️ Zonas</div>', True)
                pz = dpv['Zona'].value_counts().reset_index(); pz.columns = ['Zona','Cantidad']
                fig = px.bar(pz, x='Zona', y='Cantidad', color='Cantidad', color_continuous_scale='Blues', text='Cantidad')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(t=20,b=20), xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            cp3, cp4 = st.columns(2)
            with cp3:
                st.markdown('<div class="section-header">🔩 Especialidades</div>', True)
                pes = dpv['Especialidad'].value_counts().head(10).reset_index(); pes.columns = ['Especialidad','Cantidad']
                fig = px.bar(pes, y='Especialidad', x='Cantidad', orientation='h', color='Cantidad', color_continuous_scale='Teal', text='Cantidad')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(t=20,b=20,l=10), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with cp4:
                st.markdown('<div class="section-header">📅 Evolución Mensual</div>', True)
                pm = dpv.groupby(['Mes_Creacion','Tipo de orden']).size().reset_index(name='Cantidad').sort_values('Mes_Creacion')
                fig = px.line(pm, x='Mes_Creacion', y='Cantidad', color='Tipo de orden', markers=True,
                             color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'})
                fig.update_layout(height=350, margin=dict(t=20,b=20), legend=dict(orientation='h',y=1.05))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">👷 Supervisores Asociados</div>', True)
            psu = dpv.groupby('Supervisor_Asignado').agg(Ordenes=('Orden','count'), Importe=('Importe','sum'), Sucursales=('Denominación','nunique')).sort_values('Ordenes', ascending=False).reset_index()
            st.dataframe(psu.rename(columns={'Supervisor_Asignado':'Supervisor'}), use_container_width=True, hide_index=True,
                        column_config={"Importe": st.column_config.NumberColumn(format="$%,.2f")})

        st.markdown('<div class="section-header">⚖️ Comparativa General de Proveedores</div>', True)
        cpv = dff.groupby('Proveedor').agg(
            Total_Ordenes=('Orden','count'), Importe_Total=('Importe','sum'), Importe_IVA=('Importe IVA','sum'),
            Importe_Promedio=('Importe','mean'),
            Correctivas=('Tipo de orden', lambda x: (x=='Correctivo').sum()),
            Preventivas=('Tipo de orden', lambda x: (x=='Preventivo').sum()),
            Sucursales=('Denominación','nunique'), Zonas=('Zona','nunique'), Dias_Atencion_Prom=('Dias_Atencion','mean')
        ).sort_values('Total_Ordenes', ascending=False).reset_index()
        cpv['% Correctivas'] = (cpv['Correctivas']/cpv['Total_Ordenes']*100).round(1)
        cpv['% Preventivas'] = (cpv['Preventivas']/cpv['Total_Ordenes']*100).round(1)
        st.dataframe(cpv, use_container_width=True, hide_index=True, column_config={
            "Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f"),
            "Importe_IVA": st.column_config.NumberColumn("Importe IVA", format="$%,.2f"),
            "Importe_Promedio": st.column_config.NumberColumn("Prom.", format="$%,.2f"),
            "Dias_Atencion_Prom": st.column_config.NumberColumn("Días Atención", format="%.1f"),
            "% Correctivas": st.column_config.NumberColumn(format="%.1f%%"),
            "% Preventivas": st.column_config.NumberColumn(format="%.1f%%"),
        })


# ── TAB 3: SUPERVISOR ──
with tab3:
    st.markdown('<div class="section-header">👷 Análisis Detallado por Supervisor</div>', True)
    sup_list = sorted(dff['Supervisor_Asignado'].dropna().unique().tolist())
    if not sup_list:
        st.warning("No hay supervisores con los filtros actuales.")
    else:
        sel_sv = st.selectbox("Selecciona un supervisor:", sup_list, key='sv')
        dsv = dff[dff['Supervisor_Asignado'] == sel_sv]
        if len(dsv) == 0:
            st.warning("Sin datos para este supervisor.")
        else:
            st2 = len(dsv); si = dsv['Importe'].sum(); sii = dsv['Importe IVA'].sum()
            sc = (dsv['Tipo de orden']=='Correctivo').sum(); sp = (dsv['Tipo de orden']=='Preventivo').sum()
            spv = dsv['Proveedor'].nunique(); ssu = dsv['Denominación'].nunique()
            szl = dsv['Zona'].unique(); sda = dsv['Dias_Atencion'].mean()

            c1,c2,c3,c4,c5,c6 = st.columns(6)
            c1.markdown(kpi_card("Órdenes", f"{st2:,}", f"{st2/total_ordenes*100:.1f}%" if total_ordenes else ""), True)
            c2.markdown(kpi_card("Importe", format_currency(si), f"IVA: {format_currency(sii)}", "kpi-green"), True)
            c3.markdown(kpi_card("Correctivas", f"{sc:,}", f"{sc/st2*100:.1f}%", "kpi-orange"), True)
            c4.markdown(kpi_card("Preventivas", f"{sp:,}", f"{sp/st2*100:.1f}%", "kpi-cyan"), True)
            c5.markdown(kpi_card("Proveedores", f"{spv}", "asignados", "kpi-purple"), True)
            c6.markdown(kpi_card("Sucursales", f"{ssu}", f"en {len(szl)} zona(s)", "kpi-red"), True)
            st.markdown("")
            st.info(f"🗺️ **Zona(s):** {', '.join(szl)}")

            cs1, cs2 = st.columns(2)
            with cs1:
                st.markdown('<div class="section-header">📊 Estatus</div>', True)
                se = dsv['Estatus_Desc'].value_counts().reset_index(); se.columns = ['Estatus','Cantidad']
                fig = px.pie(se, names='Estatus', values='Cantidad', hole=0.45, color_discrete_sequence=BBVA_COLORS)
                fig.update_traces(textposition='outside', textinfo='label+value+percent')
                fig.update_layout(height=350, margin=dict(t=20,b=20), legend=dict(orientation='h',y=-0.15))
                st.plotly_chart(fig, use_container_width=True)
            with cs2:
                st.markdown('<div class="section-header">🏢 Top 10 Proveedores</div>', True)
                svp = dsv.groupby('Proveedor').agg(Ordenes=('Orden','count'), Importe=('Importe','sum')).sort_values('Ordenes', ascending=True).tail(10).reset_index()
                fig = px.bar(svp, y='Proveedor', x='Ordenes', orientation='h', color='Importe', color_continuous_scale='Oranges', text='Ordenes')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(t=20,b=20,l=10))
                st.plotly_chart(fig, use_container_width=True)

            cs3, cs4 = st.columns(2)
            with cs3:
                st.markdown('<div class="section-header">🔩 Especialidades</div>', True)
                ses = dsv['Especialidad'].value_counts().head(10).reset_index(); ses.columns = ['Especialidad','Cantidad']
                fig = px.bar(ses, y='Especialidad', x='Cantidad', orientation='h', color='Cantidad', color_continuous_scale='Teal', text='Cantidad')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(t=20,b=20,l=10), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with cs4:
                st.markdown('<div class="section-header">📅 Evolución Mensual</div>', True)
                sm = dsv.groupby(['Mes_Creacion','Tipo de orden']).size().reset_index(name='Cantidad').sort_values('Mes_Creacion')
                fig = px.line(sm, x='Mes_Creacion', y='Cantidad', color='Tipo de orden', markers=True,
                             color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'})
                fig.update_layout(height=350, margin=dict(t=20,b=20), legend=dict(orientation='h',y=1.05))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">💰 Importes por Mes</div>', True)
            cs5, cs6 = st.columns(2)
            with cs5:
                sim = dsv.groupby(['Mes_Creacion','Tipo de orden'])['Importe'].sum().reset_index().sort_values('Mes_Creacion')
                fig = px.bar(sim, x='Mes_Creacion', y='Importe', color='Tipo de orden', barmode='group',
                            color_discrete_map={'Correctivo':'#e63946','Preventivo':'#0097a7'}, text_auto='.2s')
                fig.update_layout(height=380, margin=dict(t=20,b=20), legend=dict(orientation='h',y=1.05))
                st.plotly_chart(fig, use_container_width=True)
            with cs6:
                ssc = dsv.groupby('Denominación').agg(Ordenes=('Orden','count'), Importe=('Importe','sum')).sort_values('Ordenes', ascending=True).tail(10).reset_index()
                fig = px.bar(ssc, y='Denominación', x='Ordenes', orientation='h', color='Importe', color_continuous_scale='Blues', text='Ordenes')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=380, margin=dict(t=20,b=20,l=10), xaxis_title="Órdenes", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">📋 Sucursales Asignadas</div>', True)
            ssd = dsv.groupby(['Denominación','Centro de coste','Zona']).agg(
                Total_Ordenes=('Orden','count'),
                Correctivas=('Tipo de orden', lambda x: (x=='Correctivo').sum()),
                Preventivas=('Tipo de orden', lambda x: (x=='Preventivo').sum()),
                Importe_Total=('Importe','sum')
            ).sort_values('Total_Ordenes', ascending=False).reset_index()
            st.dataframe(ssd.rename(columns={'Denominación':'Sucursal'}), use_container_width=True, hide_index=True,
                        column_config={"Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f")})

        # Comparativa supervisores
        st.markdown('<div class="section-header">⚖️ Comparativa General de Supervisores</div>', True)
        csv2 = dff.groupby('Supervisor_Asignado').agg(
            Total_Ordenes=('Orden','count'), Importe_Total=('Importe','sum'), Importe_IVA=('Importe IVA','sum'),
            Importe_Promedio=('Importe','mean'),
            Correctivas=('Tipo de orden', lambda x: (x=='Correctivo').sum()),
            Preventivas=('Tipo de orden', lambda x: (x=='Preventivo').sum()),
            Proveedores=('Proveedor','nunique'), Sucursales=('Denominación','nunique'),
            Zonas=('Zona','nunique'), Dias_Atencion_Prom=('Dias_Atencion','mean')
        ).sort_values('Total_Ordenes', ascending=False).reset_index()
        csv2['% Correctivas'] = (csv2['Correctivas']/csv2['Total_Ordenes']*100).round(1)
        csv2['% Preventivas'] = (csv2['Preventivas']/csv2['Total_Ordenes']*100).round(1)
        st.dataframe(csv2.rename(columns={'Supervisor_Asignado':'Supervisor'}), use_container_width=True, hide_index=True, column_config={
            "Importe_Total": st.column_config.NumberColumn("Importe Total", format="$%,.2f"),
            "Importe_IVA": st.column_config.NumberColumn("Importe IVA", format="$%,.2f"),
            "Importe_Promedio": st.column_config.NumberColumn("Prom.", format="$%,.2f"),
            "Dias_Atencion_Prom": st.column_config.NumberColumn("Días Atención", format="%.1f"),
            "% Correctivas": st.column_config.NumberColumn(format="%.1f%%"),
            "% Preventivas": st.column_config.NumberColumn(format="%.1f%%"),
        })

        st.markdown("")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<div class="section-header">📊 Carga de Trabajo</div>', True)
            fig = px.bar(csv2.sort_values('Total_Ordenes', ascending=True), y='Supervisor_Asignado', x='Total_Ordenes',
                        orientation='h', color='Importe_Total', color_continuous_scale='Blues', text='Total_Ordenes')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=450, margin=dict(t=20,b=20,l=10), yaxis_title="", xaxis_title="Total Órdenes")
            st.plotly_chart(fig, use_container_width=True)
        with cc2:
            st.markdown('<div class="section-header">🔧 Correctivas vs Preventivas</div>', True)
            cm = csv2.melt(id_vars='Supervisor_Asignado', value_vars=['Correctivas','Preventivas'], var_name='Tipo', value_name='Cantidad')
            fig = px.bar(cm, y='Supervisor_Asignado', x='Cantidad', color='Tipo', orientation='h', barmode='group',
                        color_discrete_map={'Correctivas':'#e63946','Preventivas':'#0097a7'}, text='Cantidad')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=450, margin=dict(t=20,b=20,l=10), yaxis_title="", legend=dict(orientation='h',y=1.05))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">🗺️ Mapa de Calor: Supervisor × Zona</div>', True)
        hd = dff.groupby(['Supervisor_Asignado','Zona']).size().reset_index(name='Ordenes')
        hp = hd.pivot_table(index='Supervisor_Asignado', columns='Zona', values='Ordenes', fill_value=0)
        fig = px.imshow(hp, text_auto=True, color_continuous_scale='Blues', aspect='auto')
        fig.update_layout(height=400, margin=dict(t=20,b=20), xaxis_title="Zona", yaxis_title="Supervisor")
        st.plotly_chart(fig, use_container_width=True)


# ── TAB 4: DETALLE ──
with tab4:
    st.markdown('<div class="section-header">📋 Base de Datos (Filtrada)</div>', True)
    st.markdown(f"**{len(dff):,} registros** de {len(df):,} totales")

    cols_show = ['Orden','Tipo de orden','Proveedor','Supervisor_Asignado','Centro de coste','Denominación',
                 'Zona','Tipo_Banca','Texto breve de la orden','Estatus_Desc','Importe','Importe IVA',
                 'Fecha de creación','Fecha de atención','Fecha de realización','Especialidad','Texto de avería','Grupo códigos']
    cols_ok = [c for c in cols_show if c in dff.columns]

    search = st.text_input("🔍 Buscar:", key='ts')
    dd = dff[cols_ok].copy()
    if search:
        mask = dd.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        dd = dd[mask]
        st.markdown(f"*{len(dd)} resultados*")

    st.dataframe(dd.rename(columns={'Supervisor_Asignado':'Supervisor','Estatus_Desc':'Estatus','Tipo_Banca':'Tipo Banca'}),
                 use_container_width=True, hide_index=True, height=600, column_config={
                     "Importe": st.column_config.NumberColumn(format="$%,.2f"),
                     "Importe IVA": st.column_config.NumberColumn(format="$%,.2f"),
                     "Fecha de creación": st.column_config.DateColumn(format="DD/MM/YYYY"),
                     "Fecha de atención": st.column_config.DateColumn(format="DD/MM/YYYY"),
                     "Fecha de realización": st.column_config.DateColumn(format="DD/MM/YYYY"),
                 })

    st.markdown("")
    cdl1, cdl2, _ = st.columns([1,1,2])
    with cdl1:
        st.download_button("📥 Descargar CSV", dd.to_csv(index=False).encode('utf-8-sig'),
                          f"BP_filtrado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
    with cdl2:
        with st.expander("📊 Resumen Estadístico"):
            st.write(dff[['Importe','Importe IVA','Dias_Atencion']].describe().round(2))

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;font-size:0.75rem;">BBVA Conservación NE · Centro de Análisis · Dirección de Administración y Operaciones</div>', True)
