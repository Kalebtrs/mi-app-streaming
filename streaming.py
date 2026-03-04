import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración básica
st.set_page_config(page_title="Gestor Streaming", page_icon="🎬")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #6221E5; color: white; }
    .titulo { text-align: center; color: #6221E5; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🎬 Control de Clientes Streaming</h1>", unsafe_allow_html=True)

# Conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Importante: worksheet="Hoja 1" debe ser el nombre exacto de la pestaña en tu Excel
    df = conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    plataformas = st.multiselect("Plataformas", ["Netflix", "Disney+", "HBO Max", "Prime Video", "Vix Premium"])
    dia = st.number_input("Día de Corte", 1, 31, 1)
    
    if st.form_submit_button("Guardar"):
        if nombre and plataformas:
            nueva_fila = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(plataformas), "Dia": int(dia)}])
            df_final = pd.concat([df, nueva_fila], ignore_index=True)
            
            try:
                conn.update(worksheet="Hoja 1", data=df_final)
                st.success("¡Guardado!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al escribir: {e}")
        else:
            st.warning("Llena los campos.")

# Tabla
st.write("### 📋 Clientes")
st.dataframe(df, use_container_width=True, hide_index=True)
