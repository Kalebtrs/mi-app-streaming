import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la interfaz
st.set_page_config(page_title="Gestor de Streaming", page_icon="🎬")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; background-color: #6221E5; color: white; border-radius: 5px; }
    .titulo { text-align: center; color: #6221E5; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🎬 Control de Clientes Streaming</h1>", unsafe_allow_html=True)

# 2. Conexión a la base de datos (Google Sheets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Nombre de la hoja en tu Google Sheet (ej. "Hoja 1")
    df = conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 3. Formulario para registrar nuevos clientes
with st.expander("➕ Registrar Nuevo Cliente", expanded=True):
    with st.form("registro_cliente"):
        nombre = st.text_input("Nombre del Cliente")
        plataformas = st.multiselect("Plataformas", ["Netflix", "Disney+", "HBO Max", "Prime Video", "Star+", "Paramount+"])
        dia_corte = st.number_input("Día de Corte", min_value=1, max_value=31, value=1)
        
        btn_guardar = st.form_submit_button("Guardar en la Base de Datos")
        
        if btn_guardar:
            if nombre and plataformas:
                # Crear nueva fila
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas),
                    "Dia": int(dia_corte)
                }])
                
                # Unir con datos viejos y subir
                df_final = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Hoja 1", data=df_final)
                
                st.success(f"¡Cliente {nombre} guardado correctamente!")
                st.rerun()
            else:
                st.warning("Por favor completa los campos obligatorios.")

# 4. Tabla de Clientes Actuales
st.markdown("### 📋 Lista de Clientes")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No hay clientes registrados aún.")
