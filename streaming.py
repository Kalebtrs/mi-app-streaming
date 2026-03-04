import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Center", page_icon="🎬", layout="centered")

# 2. DISEÑO ULTRA COMPACTO (ESTILO SPIN)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    /* Banner Morado Reducido */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 20px;
        margin: -75px -500px 20px -500px;
        text-align: center;
        border-radius: 0 0 35px 35px;
    }
    
    .header-spin h1 { margin: 0; font-size: 22px; }
    .header-spin p { margin: 0; opacity: 0.8; font-size: 13px; }

    /* Tarjetas de Clientes */
    .client-box {
        background-color: white;
        padding: 12px;
        border-radius: 18px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #EEE;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* Botón Morado */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
    
    <div class="header-spin">
        <h1>¡Qué gusto verte!</h1>
        <p>Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# 4. FORMULARIO DE REGISTRO (SIN EL 150)
with st.container():
    with st.form("registro_streaming", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Escribe el nombre aquí...")
        plataformas = st.multiselect("PLATAFORMAS CONTRATADAS", 
                                    ["Netflix Premium", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount", "Combo Total"])
        
        col1, col2 = st.columns(2)
        dia = col1.number_input("DÍA DE COBRO", 1, 31, datetime.now().day)
        # AQUÍ ESTÁ EL CAMBIO: El valor inicial ahora es 0
        costo = col2.number_input("PRECIO VENTA $", 0, 2000, 0)
        
        if st.form_submit_button("REGISTRAR VENTA"):
            if nombre and plataformas:
                new_data = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas),
                    "Total": costo,
                    "Dia": int(dia)
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=df)
                st.rerun()

# 5. LISTADO DE CLIENTES ACTIVOS
st.markdown("### Clientes Registrados")
if not df.empty:
    # Aviso de cobros para hoy
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    cobros_hoy = df[df['Dia'] == hoy]
    
    for _, fila in cobros_hoy.iterrows():
        st.warning(f"🔔 COBRAR HOY: {fila['Nombre']} (${fila['Total']})")

    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-box">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#777;">{fila['Plataformas']} • Día {int(fila['Dia'])}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:16px;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        # Botón pequeño para eliminar
        if st.button("Borrar", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
