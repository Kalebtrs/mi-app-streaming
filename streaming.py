import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Streaming Pay", page_icon="💜", layout="centered")

# --- CSS ESTILO FINTECH (MORADO Y CIRCULAR) ---
st.markdown("""
    <style>
    /* Fondo gris muy claro de app móvil */
    .stApp {
        background-color: #F7F7F9;
    }

    /* Encabezado Morado Superior */
    .header-purple {
        background-color: #6221E5;
        padding: 40px 20px;
        margin: -60px -20px 20px -20px;
        color: white;
        border-radius: 0 0 30px 30px;
    }

    /* Tarjetas blancas redondeadas */
    .stForm, .main-card {
        background-color: white !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 20px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05) !important;
    }

    /* Títulos de sección */
    .section-title {
        color: #1A1A1A;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 15px;
    }

    /* Estilo de los iconos circulares (Simulando la imagen) */
    .icon-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        gap: 15px;
        padding: 10px 0;
    }
    
    .icon-item {
        text-align: center;
        width: 80px;
    }

    .circle-icon {
        width: 60px;
        height: 60px;
        background-color: #F0E9FF;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px auto;
        color: #6221E5;
        font-size: 24px;
        transition: 0.3s;
        border: 2px solid transparent;
    }

    /* Botón morado principal */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 50px;
        font-weight: bold;
        border: none !important;
    }

    /* Ocultar elementos feos */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER APP ---
st.markdown("""
    <div class="header-purple">
        <h2 style="margin:0;">¡Qué gusto verte!</h2>
        <p style="opacity:0.8; margin:0;">Gestor de Streaming</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0).dropna(how="all")
except:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# --- SECCIÓN "HOY QUIERO..." ---
st.markdown('<p class="section-title">Hoy quiero...</p>', unsafe_allow_html=True)

# Usamos columnas para la selección visual
servicios_disponibles = {
    "Netflix": "🎬", "Disney": "🏰", "HBO": "🐉", 
    "Prime": "📦", "Vix": "⚽", "Combo": "🌟"
}

with st.expander("Seleccionar Servicios (Toca aquí)", expanded=True):
    plataformas_seleccionadas = []
    cols = st.columns(3)
    for i, (name, icon) in enumerate(servicios_disponibles.items()):
        if cols[i % 3].checkbox(f"{icon} {name}"):
            plataformas_seleccionadas.append(name)

# --- FORMULARIO DE REGISTRO ---
with st.form("registro"):
    nombre = st.text_input("Nombre del cliente", placeholder="Ej. Yolanda")
    col_a, col_b = st.columns(2)
    with col_a:
        dia = st.number_input("Día de pago", 1, 31, 4)
    with col_b:
        precio = st.number_input("Monto $", 0, 2000, 70)
    
    if st.form_submit_button("Depositar a mi cuenta (Registrar)"):
        if nombre and plataformas_seleccionadas:
            new_row = pd.DataFrame([{
                "Nombre": nombre.upper(), 
                "Plataformas": ", ".join(plataformas_seleccionadas), 
                "Total": precio, 
                "Dia": int(dia)
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=df)
            st.success("¡Cliente registrado!")
            st.rerun()

# --- MIS MOVIMIENTOS (CLIENTES) ---
st.markdown('<p class="section-title">Mis movimientos</p>', unsafe_allow_html=True)

hoy = datetime.now().day
if not df.empty:
    for i, fila in df.iterrows():
        # Color rojo si debe hoy, si no blanco
        es_hoy = int(fila['Dia']) == hoy
        border_color = "#FF4B4B" if es_hoy else "#EEE"
        
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 20px; margin-bottom: 10px; border: 1px solid {border_color}; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <b style="color: #333;">{fila['Nombre']}</b><br>
                <small style="color: #888;">{fila['Plataformas']} • Día {fila['Dia']}</small>
            </div>
            <div style="color: #6221E5; font-weight: bold; font-size: 18px;">
                ${fila['Total']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Eliminar", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
else:
    st.info("No hay movimientos registrados.")
