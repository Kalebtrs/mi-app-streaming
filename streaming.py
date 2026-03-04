import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA compacta
st.set_page_config(page_title="Streaming Center", page_icon="🎬", layout="centered")

# 2. DISEÑO AJUSTADO Y MÁS PEQUEÑO
# Se ha reducido el padding y margin del header-spin para hacerlo más bajito.
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 15px 20px 10px 20px; /* Mucho menos padding */
        margin: -80px -500px 15px -500px; /* Margen inferior reducido */
        text-align: center;
        border-radius: 0 0 30px 30px; /* Bordes menos pronunciados */
    }
    
    .header-spin h1 {
        margin: 0;
        font-size: 20px; /* Fuente más pequeña */
    }
    
    .header-spin p {
        margin: 0;
        opacity: 0.8;
        font-size: 12px; /* Fuente de subtítulo más pequeña */
    }

    /* Estilo de Tarjetas de Clientes */
    .client-box {
        background-color: white;
        padding: 10px 15px; /* Más compacto */
        border-radius: 15px; /* Bordes más pequeños */
        margin-bottom: 8px; /* Menos espacio entre tarjetas */
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
        padding: 10px; /* Botón un poco más compacto */
    }
    
    /* Compactar inputs */
    div.stNumberInput, div.stMultiSelect, div.stTextInput {
        margin-bottom: 5px; /* Menos espacio entre campos del formulario */
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

# --- SECCIÓN DE ICONOS ELIMINADA COMO SOLICITASTE ---

# 4. FORMULARIO DE REGISTRO
with st.container():
    st.markdown("### Registrar Venta", help="Formulario compacto para añadir nuevos clientes.")
    with st.form("registro_streaming", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Ej: Juan Pérez")
        plataformas = st.multiselect("¿QUÉ PLATAFORMAS CONTRATÓ?", 
                                    ["Netflix Premium", "Disney+ / Star+", "HBO Max", "Vix Premium", "Prime Video", "Combo Total"])
        
        col1, col2 = st.columns(2)
        dia = col1.number_input("DÍA DE CORTE", 1, 31, datetime.now().day)
        costo = col2.number_input("PRECIO VENTA $", 0, 1000, 150)
        
        # Botón más compacto
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
                st.success("¡Venta registrada!")
                st.rerun()

# 5. LISTADO DE CLIENTES ACTIVOS
st.markdown("### Clientes Activos")
if not df.empty:
    # Mostrar alertas de cobro para hoy
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    cobros_hoy = df[df['Dia'] == hoy]
    
    for _, fila in cobros_hoy.iterrows():
        st.error(f"⚠️ COBRAR HOY A: {fila['Nombre']} (${fila['Total']})")

    # Lista general más compacta
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-box">
            <div>
                <b style="color:#333; font-size:14px;">{fila['Nombre']}</b><br>
                <small style="color:#666; font-size:11px;">{fila['Plataformas']} (Día {int(fila['Dia'])})</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:14px;">${fila['Total']}</div>
        </div>
        """, unsafe_allow_html=True)
        # Botón de eliminar también más pequeño
        if st.button(f"x", key=f"del_{i}", help=f"Eliminar a {fila['Nombre']}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
