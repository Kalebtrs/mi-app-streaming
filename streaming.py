import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. ESTO DEBE SER LA PRIMERA LÍNEA DE CÓDIGO
st.set_page_config(page_title="Spin Streaming", page_icon="💜", layout="centered")

# 2. INYECCIÓN FORZADA DE DISEÑO (ESTILO SPIN)
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    header, footer, .stDeployButton {visibility: hidden !important;}
    
    /* Fondo Gris Claro */
    .stApp {
        background-color: #F7F7F9 !important;
    }

    /* Banner Morado Superior (Cubre todo el ancho) */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 50px 20px 30px 20px;
        margin: -100px -500px 30px -500px;
        text-align: center;
        border-radius: 0 0 45px 45px;
        box-shadow: 0 4px 15px rgba(98, 33, 229, 0.2);
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
        margin: 0 auto 5px auto;
    }

    /* Tarjetas de Clientes */
    .movimiento-card {
        background-color: white !important;
        border-radius: 22px !important;
        padding: 20px !important;
        margin-bottom: 12px !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        border: 1px solid #F0F0F0 !important;
    }

    /* Botón Morado Redondeado */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        height: 52px !important;
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
df = conn.read(ttl=0).dropna(how="all")

# 4. SECCIÓN "HOY QUIERO..." (ICONOS)
st.markdown("<b style='color:#1A1A1A; font-size:18px;'>Hoy quiero...</b>", unsafe_allow_html=True)
st.markdown("""
    <div class="icon-container">
        <div><div class="circle-icon">🎬</div><center><small>Netflix</small></center></div>
        <div><div class="circle-icon">🏰</div><center><small>Disney</small></center></div>
        <div><div class="circle-icon">🐉</div><center><small>HBO</small></center></div>
        <div><div class="circle-icon">⚽</div><center><small>Vix</small></center></div>
    </div>
""", unsafe_allow_html=True)

# 5. REGISTRO (FORMULARIO)
with st.container():
    with st.form("registro_pago", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Ej. Yolanda")
        servicios = st.multiselect("PLATAFORMAS", ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo"])
        col1, col2 = st.columns(2)
        dia = col1.number_input("DÍA PAGO", 1, 31, datetime.now().day)
        monto = col2.number_input("MONTO $", 0, 1500, 70)
        
        if st.form_submit_button("REGISTRAR MOVIMIENTO"):
            if nombre and servicios:
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(servicios),
                    "Total": monto,
                    "Dia": int(dia)
                }])
                df_final = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(data=df_final)
                st.rerun()

# 6. LISTA DE MOVIMIENTOS
st.markdown("<br><b style='color:#1A1A1A; font-size:18px;'>Mis movimientos</b>", unsafe_allow_html=True)
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="movimiento-card">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#999;">{fila['Plataformas']} • Día {fila['Dia']}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:18px;">
                ${fila['Total']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Botón para eliminar
        if st.button(f"Borrar {fila['Nombre']}", key=f"btn_{i}"):
            df_final = df.drop(i)
            conn.update(data=df_final)
            st.rerun()
