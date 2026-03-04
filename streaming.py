import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Smart Streaming", page_icon="⚡", layout="centered")

# 2. INYECCIÓN DE ESTILO SMART HOME (Inspirado en image_f349e3)
st.markdown("""
    <style>
    /* Fondo principal azul vibrante */
    .stApp {
        background: linear-gradient(180deg, #4D76FD 0%, #3B59F5 100%);
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* Contenedor tipo Tarjeta Blanca (Como en image_f349e3) */
    .main-card {
        background-color: white;
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        margin-top: -50px;
    }

    /* Títulos estilo Dispositivos */
    .smart-title {
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 32px;
        text-align: center;
        padding: 40px 0px;
        letter-spacing: 2px;
    }

    /* Botones estilo Smart App */
    .stButton>button {
        background-color: #4D76FD !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
        height: 50px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2D4ED3 !important;
        transform: scale(1.02);
    }

    /* Estilo para los inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 12px !important;
        border: 1px solid #E0E7FF !important;
        background-color: #F8FAFF !important;
    }

    /* Tarjetas de Clientes (Grid estilo image_f349e3) */
    .client-item {
        background-color: #F0F4FF;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 6px solid #4D76FD;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ESTILO SMART ---
st.markdown('<div class="smart-title">DEVICES</div>', unsafe_allow_html=True)

# --- LÓGICA DE CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# --- CUERPO DE LA APP (TARJETA BLANCA) ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Registro
st.subheader("Add New Device")
with st.form("registro", clear_on_submit=True):
    nombre = st.text_input("NAME")
    servicios = st.multiselect("PLATFORMS", ["Netflix", "Disney", "HBO", "Prime", "Vix"])
    col1, col2 = st.columns(2)
    with col1:
        dia = st.number_input("BILLING DAY", 1, 31, 4)
    with col2:
        monto = st.number_input("PRICE $", 0, 1000, 70)
    
    if st.form_submit_button("CONNECT DEVICE"):
        if nombre:
            new_data = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(servicios), "Total": monto, "Dia": int(dia)}])
            df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=df)
            st.rerun()

# Alertas
hoy = datetime.now().day
st.markdown(f"### Billing Today (Day {hoy})")
deudores = df[df['Dia'].astype(int) == hoy] if not df.empty else pd.DataFrame()

if not deudores.empty:
    for _, fila in deudores.iterrows():
        st.error(f"⚠️ PAGO PENDIENTE: {fila['Nombre']} (${fila['Total']})")
else:
    st.info("No devices pending today")

# Lista de Clientes
st.markdown("### Connected Devices")
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-item">
            <span style="color:#4D76FD; font-weight:bold;">{fila['Nombre']}</span><br>
            <small style="color:#666;">{fila['Plataformas']} | <b>${fila['Total']}</b></small>
        </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
