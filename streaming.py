import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Spin Streaming", page_icon="💜", layout="centered")

# 2. INYECCIÓN DE DISEÑO MORADO (ESTILO SPIN)
st.markdown("""
    <style>
    /* Forzar fondo gris claro */
    .stApp { background-color: #F7F7F9 !important; }
    header, footer {visibility: hidden !important;}

    /* Banner Morado Curvo */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 50px 20px 30px 20px;
        margin: -100px -500px 30px -500px;
        text-align: center;
        border-radius: 0 0 45px 45px;
    }

    /* Iconos Circulares (Hoy quiero...) */
    .icon-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .circle-icon {
        width: 60px;
        height: 60px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        font-size: 25px;
        margin-bottom: 5px;
    }

    /* Tarjetas Blancas Redondeadas */
    div.stForm, .movimiento-card {
        background-color: white !important;
        border-radius: 25px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }

    /* Botón Morado Redondo */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 55px !important;
        width: 100% !important;
        border: none !important;
        font-weight: bold !important;
    }
    </style>
    
    <div class="header-spin">
        <h1 style="margin:0; font-size:24px;">¡Qué gusto verte!</h1>
        <p style="margin:0; opacity:0.8; font-size:14px;">Gestor de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0).dropna(how="all")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# 4. HOY QUIERO... (ICONOS)
st.markdown("<b style='color:#1A1A1A; font-size:18px;'>Hoy quiero...</b>", unsafe_allow_html=True)
st.markdown("""
    <div class="icon-container">
        <div><div class="circle-icon">🎬</div><center><small>Netflix</small></center></div>
        <div><div class="circle-icon">🏰</div><center><small>Disney</small></center></div>
        <div><div class="circle-icon">🐉</div><center><small>HBO</small></center></div>
        <div><div class="circle-icon">⚽</div><center><small>Vix</small></center></div>
    </div>
""", unsafe_allow_html=True)

# 5. REGISTRO
with st.form("registro_pago", clear_on_submit=True):
    nombre = st.text_input("NOMBRE DEL TITULAR")
    servicios = st.multiselect("PLATAFORMAS", ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo"])
    c1, c2 = st.columns(2)
    dia = c1.number_input("DÍA COBRO", 1, 31, datetime.now().day)
    monto = c2.number_input("MONTO $", 0, 1500, 70)
    
    if st.form_submit_button("REGISTRAR MOVIMIENTO"):
        if nombre:
            new_data = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(servicios), "Total": monto, "Dia": int(dia)}])
            df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=df)
            st.rerun()

# 6. MOVIMIENTOS
st.markdown("<br><b style='color:#1A1A1A; font-size:18px;'>Mis movimientos</b>", unsafe_allow_html=True)
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 20px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #EEE;">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#999;">{fila['Plataformas']} • Día {fila['Dia']}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:18px;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Eliminar", key=f"btn_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
