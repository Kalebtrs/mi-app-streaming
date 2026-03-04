import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming Manager", page_icon="🎬", layout="centered")

# 2. DISEÑO COMPACTO Y SIN DISTRACCIONES
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F7F7F9 !important; }
    header, footer { visibility: hidden !important; }
    
    /* Banner Morado a la medida del formulario */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 15px;
        margin: -70px -500px 20px -500px;
        text-align: center;
        border-radius: 0 0 30px 30px;
    }
    
    .header-spin h1 { margin: 0; font-size: 20px; font-family: sans-serif; }

    /* Tarjetas de Clientes */
    .client-box {
        background-color: white;
        padding: 12px 18px;
        border-radius: 20px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #EEE;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    /* Botón Morado Estilo Spin */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
    
    <div class="header-spin">
        <h1>Gestor de Clientes</h1>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 4. PANEL DE REGISTRO (SOLO NOMBRE, PLATAFORMAS Y DÍA)
with st.container():
    with st.form("registro_cliente", clear_on_submit=True):
        # Lugar para el nombre
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
        
        # Panel de plataformas
        plataformas = st.multiselect("PLATAFORMAS ACTIVAS", 
                                    ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"])
        
        # Día de corte
        dia = st.number_input("DÍA DE CORTE (1-31)", 1, 31, datetime.now().day)
        
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

# 5. LISTADO DE CLIENTES (MOVIMIENTOS)
st.markdown("### Clientes Registrados")
if not df.empty:
    # Aviso de quién paga hoy
    hoy = datetime.now().day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    pagan_hoy = df[df['Dia'] == hoy]
    
    for _, fila in pagan_hoy.iterrows():
        st.error(f"🚨 HOY TOCA COBRO: {fila['Nombre']}")

    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="client-box">
            <div>
                <b style="color:#333; font-size:16px;">{fila['Nombre']}</b><br>
                <small style="color:#888;">{fila['Plataformas']}</small>
            </div>
            <div style="text-align: right;">
                <span style="color:#6221E5; font-weight:bold; font-size:14px;">Día {int(fila['Dia'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón discreto para borrar si el cliente se va
        if st.button("Eliminar", key=f"del_{i}"):
            df_final = df.drop(i)
            conn.update(data=df_final)
            st.rerun()
