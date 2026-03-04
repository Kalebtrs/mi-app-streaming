import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

# Diseño
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    .header-spin {
        background-color: #6221E5; color: white; padding: 20px;
        text-align: center; border-radius: 20px; margin-bottom: 20px;
    }
    .stButton>button { background-color: #6221E5 !important; color: white !important; width: 100%; border-radius: 12px; }
    </style>
    <div class="header-spin">
        <h1>¡Qué gusto verte!</h1>
        <p>Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos de la "Hoja 1"
try:
    df = conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# Formulario
with st.form("registro", clear_on_submit=True):
    nombre = st.text_input("NOMBRE DEL CLIENTE")
    plataformas = st.multiselect("SELECCIONA LA PLATAFORMA", ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"], placeholder="Selecciona la plataforma")
    dia = st.number_input("DIA DE CORTE", 1, 31, value=None, placeholder="Día de corte")
    
    if st.form_submit_button("GUARDAR CLIENTE"):
        if nombre and plataformas and dia:
            nueva_fila = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(plataformas), "Dia": int(dia)}])
            df_final = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(worksheet="Hoja 1", data=df_final)
            st.success("¡Guardado!")
            st.rerun()

# Lista
st.markdown("### Clientes Registrados")
for i, fila in df.iterrows():
    st.write(f"👤 **{fila['Nombre']}** - {fila['Plataformas']} (Día {int(fila['Dia'])})")
    if st.button("Eliminar", key=f"del_{i}"):
        df_borrar = df.drop(i)
        conn.update(worksheet="Hoja 1", data=df_borrar)
        st.rerun()
