import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

# 2. DISEÑO AJUSTADO AL ANCHO DE LOS PANELES
st.markdown("""
    <style>
    /* Fondo general */
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    /* Contenedor principal para limitar el ancho de lo morado */
    .main-container {
        max-width: 100%;
        margin: auto;
    }

    /* Banner Morado ajustado al tamaño de los inputs */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 15px;
        margin: 10px 0px 20px 0px;
        text-align: center;
        border-radius: 15px; /* Bordes redondeados como los paneles */
        box-shadow: 0 4px 10px rgba(98, 33, 229, 0.2);
    }
    
    .header-spin h1 { margin: 0; font-size: 20px; font-family: sans-serif; }

    /* Tarjetas de Clientes */
    .client-box {
        background-color: white;
        padding: 12px 18px;
        border-radius: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #EEE;
    }
    
    /* Botón Guardar */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 4. CUERPO DE LA APP
st.markdown('<div class="header-spin"><h1>Gestor de Clientes</h1></div>', unsafe_allow_html=True)

with st.container():
    with st.form("registro_cliente", clear_on_submit=True):
        # Nombre
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
        
        # Panel de plataformas con el texto solicitado
        plataformas = st.multiselect("SELECCIONA LA PLATAFORMA", 
                                    ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"])
        
        # Día de corte con el texto solicitado
        dia = st.number_input("DIA DE CORTE", 1, 31, datetime.now().day)
        
        if st.form_submit_button("GUARDAR CLIENTE"):
            if nombre and plataformas:
                new_row = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas),
                    "Dia": int(dia)
                }])
                df_actualizado = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df_actualizado)
                st.rerun()

# 5. LISTADO
st.markdown("### Clientes Registrados")
if not df.empty:
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    
    for i, fila in df.iterrows():
        # Alerta visual si toca pagar hoy
        border_color = "#6221E5" if fila['Dia'] == hoy else "#EEE"
        bg_color = "#FFF1F1" if fila['Dia'] == hoy else "white"
        
        st.markdown(f"""
        <div class="client-box" style="border-color: {border_color}; background-color: {bg_color};">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#888;">{fila['Plataformas']}</small>
            </div>
            <div style="text-align: right;">
                <span style="color:#6221E5; font-weight:bold;">Día {int(fila['Dia'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Eliminar", key=f"del_{i}"):
            df_final = df.drop(i)
            conn.update(data=df_final)
            st.rerun()
