import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Center", page_icon="🎬", layout="centered")

# 2. DISEÑO PROFESIONAL DE PLATAFORMAS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 50px 20px 30px 20px;
        margin: -80px -500px 30px -500px;
        text-align: center;
        border-radius: 0 0 50px 50px;
    }

    /* Contenedor de Logos de Plataformas */
    .platform-grid {
        display: flex;
        justify-content: space-around;
        margin: 20px 0 30px 0;
    }
    .platform-card {
        text-align: center;
        width: 70px;
    }
    .img-circle {
        width: 60px;
        height: 60px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 28px; /* Aquí irán los logos */
        margin-bottom: 8px;
    }

    /* Estilo de Tarjetas de Clientes */
    .client-box {
        background-color: white;
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #EEE;
    }
    
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    </style>
    
    <div class="header-spin">
        <h1 style="margin:0;">¡Qué gusto verte!</h1>
        <p style="margin:0; opacity:0.8;">Tu Central de Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# 4. SECCIÓN DE ICONOS DE PLATAFORMAS
st.markdown("### Seleccionar Plataforma")
st.markdown("""
    <div class="platform-grid">
        <div class="platform-card"><div class="img-circle">🔴</div><small>Netflix</small></div>
        <div class="platform-card"><div class="img-circle">🔵</div><small>Disney+</small></div>
        <div class="platform-card"><div class="img-circle">🟣</div><small>HBO Max</small></div>
        <div class="platform-card"><div class="img-circle">🟠</div><small>Paramount</small></div>
    </div>
""", unsafe_allow_html=True)

# 5. FORMULARIO DE REGISTRO
with st.form("registro_streaming"):
    nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Ej: Juan Pérez")
    plataformas = st.multiselect("¿QUÉ PLATAFORMAS CONTRATÓ?", 
                                ["Netflix Premium", "Disney+ / Star+", "HBO Max", "Vix Premium", "Prime Video", "Combo Total"])
    
    col1, col2 = st.columns(2)
    dia = col1.number_input("DÍA DE CORTE", 1, 31, datetime.now().day)
    costo = col2.number_input("PRECIO VENTA $", 0, 1000, 150)
    
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
            st.success("¡Venta registrada con éxito!")
            st.rerun()

# 6. LISTADO DE CLIENTES ACTIVOS
st.markdown("### Clientes Activos")
if not df.empty:
    # Mostrar alertas de cobro para hoy
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    cobros_hoy = df[df['Dia'] == hoy]
    
    for _, fila in cobros_hoy.iterrows():
        st.error(f"⚠️ COBRAR HOY A: {fila['Nombre']} (${fila['Total']})")

    # Lista general
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-box">
            <div>
                <b style="color:#333;">{fila['Nombre']}</b><br>
                <small style="color:#666;">{fila['Plataformas']} (Día {int(fila['Dia'])})</small>
            </div>
            <div style="color:#6221E5; font-weight:bold;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Eliminar {fila['Nombre']}", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
