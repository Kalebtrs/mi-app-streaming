import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. DISEÑO COMPACTO
st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    .header-spin {
        background-color: #6221E5; color: white; padding: 20px;
        margin: 10px 0px 20px 0px; text-align: center; border-radius: 20px;
    }
    .header-spin h1 { margin: 0; font-size: 24px; }
    .stButton>button { background-color: #6221E5 !important; color: white !important; border-radius: 12px !important; width: 100% !important; height: 45px; font-weight: bold; }
    </style>
    <div class="header-spin">
        <h1>¡Qué gusto verte!</h1>
        <p>Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 2. CONEXIÓN (IMPORTANTE)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leemos la hoja (asegúrate que en tu Excel la pestaña se llame Hoja1 o Sheet1)
    df = conn.read(worksheet="Hoja1", ttl=0).dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 3. FORMULARIO CON TUS TEXTOS
with st.form("registro_cliente", clear_on_submit=True):
    nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
    
    plataformas = st.multiselect(
        "PLATAFORMAS", 
        ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"],
        placeholder="Selecciona la plataforma"
    )
    
    # Campo de día vacío por defecto
    dia = st.number_input("DIA DE CORTE", min_value=1, max_value=31, value=None, placeholder="Escribe el día de corte")
    
    if st.form_submit_button("GUARDAR CLIENTE"):
        if nombre and plataformas and dia:
            new_row = pd.DataFrame([{
                "Nombre": nombre.upper(),
                "Plataformas": ", ".join(plataformas),
                "Dia": int(dia)
            }])
            
            # Combinamos datos nuevos con viejos
            df_actualizado = pd.concat([df, new_row], ignore_index=True)
            
            # INTENTO DE GUARDADO
            try:
                conn.update(worksheet="Hoja1", data=df_actualizado)
                st.success("✅ ¡Cliente guardado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.info("Revisa si tus Secrets en Streamlit tienen permisos de edición.")
        else:
            st.warning("⚠️ Por favor, llena todos los campos.")

# 4. LISTADO VISUAL
st.markdown("### Clientes Registrados")
if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div style="background-color: white; padding: 12px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #EEE; display: flex; justify-content: space-between;">
            <div><b>{fila['Nombre']}</b><br><small>{fila['Plataformas']}</small></div>
            <div style="color: #6221E5; font-weight: bold;">Día {int(fila['Dia'])}</div>
        </div>
        """, unsafe_allow_html=True)
