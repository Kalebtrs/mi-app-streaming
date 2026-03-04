import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuracion de pagina
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS Mejorado para forzar alineacion a la derecha
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

    /* MOVER BOTON DE GUARDAR A LA DERECHA */
    .stForm > div:last-child {
        display: flex;
        justify-content: flex-end;
        width: 100%;
    }

    /* ESTILO DEL BOTON LLAMATIVO (Ajustado para no ser ancho completo) */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #FF0080, #FF8C00, #40E0D0);
        background-size: 200% auto;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(255, 0, 128, 0.4);
        transition: 0.5s;
        text-transform: uppercase;
    }

    div.stButton > button:first-child:hover {
        background-position: right center;
        transform: scale(1.05);
    }

    /* MOVER FLECHITA DEL SELECTBOX A LA DERECHA Y TEXTO */
    div[data-baseweb="select"] > div {
        text-align: right !important;
        flex-direction: row-reverse !important;
    }

    /* Boton de eliminar */
    div.stButton > button[kind="primary"] {
        background: #FF4B2B !important;
        border-radius: 8px !important;
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
        # El selector ahora tendra la flecha y el texto alineados a la derecha
        dia = st.selectbox("Día de Corte", options=dias, index=None, placeholder="Selecciona dia de corte")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and servicios and dia:
                total = sum(PRECIOS.get(s, 0) for s in servicios)
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(servicios)],
                    "Dia": [int(dia)],
                    "Total a Pagar": [total]
                })
                df_act = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Hoja 1", data=df_act)
                st.rerun()

# --- SECCION GESTION ---
if not df.empty:
    with st.expander("Gestionar"):
        borrar = st.selectbox("Seleccionar para eliminar", df["Nombre"].unique())
        if st.button("ELIMINAR CLIENTE", type="primary"):
            df_new = df[df["Nombre"] != borrar]
            conn.update(worksheet="Hoja 1", data=df_new)
            st.rerun()

# --- LISTA DE CLIENTES ---
st.write("---")
st.write("### Lista de Clientes")

if not df.empty:
    df_v = df[["Nombre", "Plataformas", "Dia", "Total a Pagar"]].copy()
    df_v["Total a Pagar"] = pd.to_numeric(df_v["Total a Pagar"]).fillna(0)
    
    st.dataframe(
        df_v, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Total a Pagar": st.column_config.NumberColumn(format="$%d"),
            "Dia": st.column_config.NumberColumn(format="%d")
        }
    )
    
    total_m = df_v["Total a Pagar"].sum()
    st.metric(label="Total Mensual", value=f"${total_m:,.0f}")
else:
    st.write("No hay clientes registrados")
