import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spin Streaming", page_icon="💜", layout="centered")

# CSS AGRESIVO PARA FORZAR EL DISEÑO DE SPIN
st.markdown("""
    <style>
    /* 1. Fondo y Ocultar Headers */
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    .block-container { padding-top: 0rem !important; }

    /* 2. Banner Morado Superior Curvo */
    .header-spin {
        background-color: #6221E5 !important;
        color: white !important;
        padding: 60px 20px 40px 20px !important;
        margin: -20px -500px 30px -500px !important;
        text-align: center !important;
        border-radius: 0 0 50px 50px !important;
        box-shadow: 0 4px 15px rgba(98, 33, 229, 0.3) !important;
    }

    /* 3. Iconos Circulares (Hoy quiero...) */
    .icon-row {
        display: flex !important;
        justify-content: space-around !important;
        margin: 20px 0 !important;
    }
    .circle-wrap { text-align: center; width: 75px; }
    .circle-bg {
        width: 60px;
        height: 60px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        font-size: 26px;
        margin: 0 auto 8px auto;
    }

    /* 4. Tarjetas de Clientes Estilo Banco */
    .movimiento-item {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        border: 1px solid #F0F0F0 !important;
    }

    /* 5. Botón Morado de Spin */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 52px !important;
        width: 100% !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    </style>

    <div class="header-spin">
        <h1 style="margin:0; font-family:sans-serif;">¡Qué gusto verte!</h1>
        <p style="margin:0; opacity:0.8;">Gestor de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# SECCIÓN VISUAL
st.markdown("<b style='color:#333; font-size:18px;'>Hoy quiero...</b>", unsafe_allow_html=True)
st.markdown("""
    <div class="icon-row">
        <div class="circle-wrap"><div class="circle-bg">🎬</div><small>Netflix</small></div>
        <div class="circle-wrap"><div class="circle-bg">🏰</div><small>Disney</small></div>
        <div class="circle-wrap"><div class="circle-bg">🐉</div><small>HBO</small></div>
        <div class="circle-wrap"><div class="circle-bg">⚽</div><small>Vix</small></div>
    </div>
""", unsafe_allow_html=True)

# FORMULARIO
with st.form("registro"):
    nombre = st.text_input("NOMBRE DEL TITULAR")
    servicios = st.multiselect("PLATAFORMAS", ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo"])
    c1, c2 = st.columns(2)
    dia = c1.number_input("DÍA COBRO", 1, 31, 4)
    monto = c2.number_input("MONTO $", 0, 1500, 70)
    
    if st.form_submit_button("REGISTRAR MOVIMIENTO"):
        if nombre:
            new_row = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(servicios), "Total": monto, "Dia": int(dia)}])
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=df)
            st.rerun()

# LISTA DE MOVIMIENTOS
st.markdown("<br><b style='color:#333; font-size:18px;'>Mis movimientos</b>", unsafe_allow_html=True)
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="movimiento-item">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#999;">{fila['Plataformas']} • Día {fila['Dia']}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:18px;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Borrar {i}", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
            
