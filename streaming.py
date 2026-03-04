import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuración para que se vea como una App móvil
st.set_page_config(page_title="Streaming App", page_icon="📱", layout="centered")

# --- DISEÑO TIPO SMART HOME (CSS AVANZADO) ---
st.markdown("""
<style>
    /* Fondo oscuro como la imagen */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Título estilo neón */
    .main-title {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 800;
        text-align: left;
        margin-bottom: 5px;
        font-family: 'sans-serif';
    }
    
    .sub-title {
        color: #808495;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Tarjetas de Clientes (Estilo Smart Home) */
    .card {
        background: #1E232E;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #2D343F;
    }
    
    .card-title {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 18px;
    }
    
    .card-price {
        color: #3D5AFE;
        font-size: 22px;
        font-weight: 700;
    }

    /* Badge de estado (Activo/Hoy) */
    .badge-today {
        background-color: #FF4B4B;
        color: white;
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }

    /* Inputs estilo oscuro */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #1E232E !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #2D343F !important;
    }
</style>
""", unsafe_allow_submit=True)

# --- ENCABEZADO ---
st.markdown('<div class="main-title">Streaming Manager</div>', unsafe_allow_submit=True)
st.markdown('<div class="sub-title">Control de pagos y dispositivos</div>', unsafe_allow_submit=True)

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
except Exception:
    df_existente = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# --- REGISTRO (DENTRO DE UNA TARJETA) ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_submit=True)
    st.markdown('<span style="color:white; font-weight:bold;">Añadir Nuevo</span>', unsafe_allow_submit=True)
    
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre del titular")
        
        # Selección de servicios en columnas
        servicios = ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo"]
        elegidos = st.multiselect("Selecciona Dispositivos/Servicios", servicios)
        
        col1, col2 = st.columns(2)
        with col1:
            dia = st.number_input("Día cobro", 1, 31, datetime.now().day)
        with col2:
            monto = st.number_input("Monto $", 0, 500, 70)
            
        submit = st.form_submit_button("REGISTRAR DISPOSITIVO")
        
        if submit and nombre:
            nueva_fila = pd.DataFrame([{"Nombre": nombre.upper(), "Plataformas": ", ".join(elegidos), "Total": monto, "Dia": int(dia)}])
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            conn.update(data=df_final)
            st.success("Registrado")
            st.rerun()
    st.markdown('</div>', unsafe_allow_submit=True)

# --- ALERTAS DE HOY (ESTILO NOTIFICACIÓN) ---
hoy = datetime.now().day
if not df_existente.empty:
    df_existente['Dia'] = pd.to_numeric(df_existente['Dia'], errors='coerce')
    deudores = df_existente[df_existente['Dia'] == hoy]
    
    if not deudores.empty:
        st.markdown('<h3>Pagos Pendientes Hoy</h3>', unsafe_allow_submit=True)
        for _, fila in deudores.iterrows():
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #FF4B4B 0%, #1E232E 100%); padding:15px; border-radius:15px; margin-bottom:10px; border-left: 5px solid white;">
                <b style="color:white;">🔔 {fila['Nombre']}</b><br>
                <small style="color:white;">Cobrar ${fila['Total']} por {fila['Plataformas']}</small>
            </div>
            """, unsafe_allow_submit=True)

# --- LISTA DE DISPOSITIVOS (CLIENTES) ---
st.markdown('<br><h3>Dispositivos Conectados</h3>', unsafe_allow_submit=True)

if not df_existente.empty:
    # Mostramos los clientes en un diseño de cuadrícula (2 por fila)
    for i, fila in df_existente.iterrows():
        # Cada cliente es una "Tarjeta de Dispositivo"
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between;">
                <span class="card-title">👤 {fila['Nombre']}</span>
                <span class="badge-today">Día {int(fila['Dia'])}</span>
            </div>
            <div style="color: #808495; font-size: 13px; margin: 10px 0;">{fila['Plataformas']}</div>
            <div class="card-price">${fila['Total']}</div>
        </div>
        """, unsafe_allow_submit=True)
        
        # Botón pequeño para eliminar
        if st.button(f"Desconectar {fila['Nombre']}", key=f"btn_{i}"):
            df_final = df_existente.drop(i)
            conn.update(data=df_final)
            st.rerun()
