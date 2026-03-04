import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

# 2. DISEÑO ESTILO SPIN (Banner ajustado y textos limpios)
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

    /* Ajuste de etiquetas */
    label { font-weight: bold !important; color: #333 !important; }
    </style>
    
    <div class="header-spin">
        <h1>¡Qué gusto verte!</h1>
        <p>Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos actuales
try:
    df = conn.read(worksheet="Sheet1", ttl=0).dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 4. FORMULARIO DE REGISTRO
with st.container():
    with st.form("registro_cliente", clear_on_submit=True):
        # Nombre
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
        
        # Selección de plataforma (Texto personalizado)
        plataformas = st.multiselect(
            "SELECCIONA LA PLATAFORMA", 
            ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"],
            placeholder="Selecciona la plataforma"
        )
        
        # Día de corte (Sin número inicial y texto personalizado)
        dia = st.number_input("DIA DE CORTE", min_value=1, max_value=31, value=None, placeholder="Escribe el día de corte")
        
        if st.form_submit_button("GUARDAR CLIENTE"):
            if nombre and plataformas and dia:
                # Crear nueva fila
                new_row = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas),
                    "Dia": int(dia)
                }])
                
                # Unir con datos existentes
                df_actualizado = pd.concat([df, new_row], ignore_index=True)
                
                # Intentar guardar en Google Sheets
                try:
                    conn.update(worksheet="Sheet1", data=df_actualizado)
                    st.success("✅ ¡Cliente guardado correctamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error de permisos: {e}")
            else:
                st.warning("⚠️ Por favor rellena todos los campos.")

# 5. LISTADO DE CLIENTES REGISTRADOS
st.markdown("---")
st.markdown("### Clientes Registrados")

if not df.empty:
    hoy = datetime.now().day
    # Asegurar que la columna Dia sea numérica
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    
    for i, fila in df.iterrows():
        # Resaltar si hoy es su día de corte
        es_hoy = fila['Dia'] == hoy
        border_style = "border-left: 6px solid #6221E5;" if es_hoy else "border-left: 1px solid #EEE;"
        bg_color = "#F0E9FF" if es_hoy else "white"

        st.markdown(f"""
        <div class="client-box" style="{border_style} background-color: {bg_color};">
            <div>
                <b style="color:#333; font-size:16px;">{fila['Nombre']}</b><br>
                <small style="color:#666;">{fila['Plataformas']}</small>
            </div>
            <div style="text-align: right;">
                <span style="color:#6221E5; font-weight:bold; font-size:14px;">Día {int(fila['Dia'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para eliminar cliente
        if st.button("Eliminar", key=f"del_{i}"):
            df_final = df.drop(i)
            conn.update(worksheet="Sheet1", data=df_final)
            st.rerun()
else:
    st.info("Aún no hay clientes registrados.")
