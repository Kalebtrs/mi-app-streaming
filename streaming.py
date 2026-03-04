import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

# 2. DISEÑO AJUSTADO AL ANCHO DE LOS PANELES
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    /* Banner Morado del tamaño de los paneles */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 20px;
        margin: 10px 0px 20px 0px;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(98, 33, 229, 0.2);
    }
    
    .header-spin h1 { margin: 0; font-size: 24px; font-family: sans-serif; font-weight: bold; }
    .header-spin p { margin: 5px 0 0 0; opacity: 0.9; font-size: 14px; }

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
        height: 48px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        margin-top: 10px;
    }
    </style>
    
    <div class="header-spin">
        <h1>¡Qué gusto verte!</h1>
        <p>Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 4. FORMULARIO DE REGISTRO
with st.container():
    with st.form("registro_cliente", clear_on_submit=True):
        # Nombre
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
        
        # Selección de plataforma
        plataformas = st.multiselect("SELECCIONA LA PLATAFORMA", 
                                    ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"])
        
        # Día de corte
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

# 5. LISTADO DE CLIENTES
st.markdown("### Clientes Registrados")
if not df.empty:
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    
    for i, fila in df.iterrows():
        # Color especial si toca pagar hoy
        border_color = "#6221E5" if fila['Dia'] == hoy else "#EEE"
        
        st.markdown(f"""
        <div class="client-box" style="border-left: 5px solid {border_color};">
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
