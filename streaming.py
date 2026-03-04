import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. FORZAR CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Spin Streaming", page_icon="💜", layout="centered")

# 2. CSS AGRESIVO (PARA QUE SE VEA COMO TU IMAGEN DE SPIN)
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    header, footer, .stDeployButton {visibility: hidden !important;}
    
    /* Fondo gris claro */
    [data-testid="stAppViewContainer"] {
        background-color: #F7F7F9 !important;
    }

    /* Banner Morado Superior (Estilo Spin) */
    .header-spin {
        background-color: #6221E5 !important;
        color: white !important;
        padding: 60px 20px 40px 20px !important;
        margin: -80px -500px 30px -500px !important;
        text-align: center !important;
        border-radius: 0 0 50px 50px !important;
        box-shadow: 0 4px 15px rgba(98, 33, 229, 0.3) !important;
    }

    /* Iconos Circulares */
    .icon-row {
        display: flex !important;
        justify-content: space-around !important;
        margin: 20px 0 !important;
    }
    .circle-bg {
        width: 60px;
        height: 60px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        font-size: 26px;
        margin: 0 auto 5px auto;
    }

    /* Tarjetas de Clientes */
    .client-card {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
        border: 1px solid #F0F0F0 !important;
    }

    /* Botón Morado de la App */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 55px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
    
    <div class="header-spin">
        <h1 style="margin:0; font-family: sans-serif; font-size: 26px;">¡Qué gusto verte!</h1>
        <p style="margin:0; opacity:0.8; font-size: 14px;">Gestor de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# 4. HOY QUIERO... (ICONOS COMO LA IMAGEN)
st.markdown("<b style='color:#333; font-size:18px;'>Hoy quiero...</b>", unsafe_allow_html=True)
st.markdown("""
    <div class="icon-row">
        <div><div class="circle-bg">🎬</div><center><small>Netflix</small></center></div>
        <div><div class="circle-bg">🏰</div><center><small>Disney</small></center></div>
        <div><div class="circle-bg">🐉</div><center><small>HBO</small></center></div>
        <div><div class="circle-bg">⚽</div><center><small>Vix</small></center></div>
    </div>
""", unsafe_allow_html=True)

# 5. FORMULARIO DE REGISTRO
with st.container():
    with st.form("nuevo_pago", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL TITULAR")
        servicios = st.multiselect("PLATAFORMAS", ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo 1", "Combo 2"])
        c1, c2 = st.columns(2)
        dia = c1.number_input("DÍA PAGO", 1, 31, 4)
        monto = c2.number_input("MONTO $", 0, 2000, 70)
        
        if st.form_submit_button("REGISTRAR EN MI CUENTA"):
            if nombre:
                new_row = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(servicios), "Total": monto, "Dia": int(dia)}])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.rerun()

# 6. MIS MOVIMIENTOS
st.markdown("<br><b style='color:#333; font-size:18px;'>Mis movimientos</b>", unsafe_allow_html=True)
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-card">
            <div>
                <b style="color:#333; font-size:15px;">{fila['Nombre']}</b><br>
                <small style="color:#999;">{fila['Plataformas']} • Día {fila['Dia']}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:18px;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Eliminar {i}", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
