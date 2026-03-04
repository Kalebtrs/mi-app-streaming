import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta

# 1. Configuración de página
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS: Diseño, espacios y colores de alerta
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00DBDE 0%, #FC00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
    
    /* Espacio solicitado entre Día de Corte y Botón */
    .stForm > div:last-child { padding-top: 60px !important; }

    /* Estilo para las alertas de pago */
    .alerta-pago {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 6px solid;
    }
    .hoy { background-color: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; color: #ff4b4b; }
    .manana { background-color: rgba(255, 215, 0, 0.15); border-color: #ffd700; color: #e6c300; }
    
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #FF0080, #FF8C00, #40E0D0) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Streaming Control</h1>", unsafe_allow_html=True)

# 3. Conexión y Datos
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# --- SECCIÓN REGISTRO ---
with st.expander("Nuevo Cliente", expanded=False):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Escribe el nombre...")
        servicios = st.multiselect("Plataformas y Combos", options=list(PRECIOS.keys()))
        dias = [str(i) for i in range(1, 32)]
        dia = st.selectbox("Día de Corte", options=dias, index=None, placeholder="Selecciona dia de corte")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and servicios and dia:
                total = sum(PRECIOS.get(s, 0) for s in servicios)
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(servicios)],
                    "Dia": [int(dia)],
                    "Total a Pagar": [total]
                })
                df_act = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Hoja 1", data=df_act)
                st.rerun()

# --- GESTIONAR ---
with st.expander("Gestionar"):
    if not df.empty:
        borrar = st.selectbox("Seleccionar para eliminar", df["Nombre"].unique())
        if st.button("ELIMINAR CLIENTE", type="primary"):
            df_new = df[df["Nombre"] != borrar]
            conn.update(worksheet="Hoja 1", data=df_new)
            st.rerun()

# --- SECCIÓN DE COBROS (HOY Y MAÑANA) ---
st.write("---")
if not df.empty:
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    
    # Cálculos de fechas
    hoy_dt = datetime.now()
    dia_hoy = hoy_dt.day
    dia_manana = (hoy_dt + timedelta(days=1)).day

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pagos Hoy")
        hoy_pago = df[df['Dia'] == dia_hoy]
        if not hoy_pago.empty:
            for _, r in hoy_pago.iterrows():
                st.markdown(f'<div class="alerta-pago hoy"><strong>{r["Nombre"]}</strong><br>${r["Total a Pagar"]}</div>', unsafe_allow_html=True)
        else:
            st.write("Ninguno")

    with col2:
        st.subheader("Pagos Mañana")
        manana_pago = df[df['Dia'] == dia_manana]
        if not manana_pago.empty:
            for _, r in manana_pago.iterrows():
                st.markdown(f'<div class="alerta-pago manana"><strong>{r["Nombre"]}</strong><br>${r["Total a Pagar"]}</div>', unsafe_allow_html=True)
        else:
            st.write("Ninguno")

# --- LISTA COMPLETA ---
st.write("---")
if not df.empty:
    st.write("### Lista de Clientes")
    st.dataframe(df[["Nombre", "Plataformas", "Dia", "Total a Pagar"]], use_container_width=True, hide_index=True)
    
    total_m = pd.to_numeric(df["Total a Pagar"]).sum()
    st.metric(label="Recaudación Mensual", value=f"${total_m:,.0f}")
else:
    st.write("No hay clientes registrados")
