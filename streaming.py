import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuracion de pagina
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS: Espaciado extra y diseño limpio
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00DBDE 0%, #FC00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* --- ELIMINAR RECUADRO INTERNO --- */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* --- FLECHA DEL EXPANDER A LA DERECHA --- */
    .stExpander details summary svg {
        order: 2 !important;
        margin-left: auto !important;
    }
    .stExpander details summary {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
    }

    /* --- EL ESPACIO QUE PEDISTE (Día de corte vs Botón) --- */
    .stForm > div:last-child {
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
        padding-top: 60px !important; /* <--- Aumentado a 60px para el espacio marcado en rojo */
        margin-bottom: 10px !important;
    }

    /* BOTON LLAMATIVO Y A LA DERECHA */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #FF0080, #FF8C00, #40E0D0) !important;
        background-size: 200% auto !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2.5rem !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(255, 0, 128, 0.4) !important;
        transition: 0.5s !important;
        text-transform: uppercase !important;
        width: auto !important;
    }

    /* --- FLECHAS DE LOS SELECTORES A LA DERECHA --- */
    div[data-baseweb="select"] {
        position: relative !important;
    }
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] + div {
        position: absolute !important;
        right: 10px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Streaming Control</h1>", unsafe_allow_html=True)

# 3. Datos y Conexion
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# --- SECCION REGISTRO ---
with st.expander("Nuevo Cliente", expanded=False):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Escribe el nombre...")
        servicios = st.multiselect("Plataformas y Combos", options=list(PRECIOS.keys()), placeholder="Selecciona el servicio")
        
        dias = [str(i) for i in range(1, 32)]
        dia = st
