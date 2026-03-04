import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuracion de pagina optimizada para moviles
st.set_page_config(page_title="Streaming App", layout="centered")

# CSS para el estilo oscuro neón sin emojis
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E0E0E0; }
    
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00DBDE 0%, #FC00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }

    .stForm, .stExpander {
        background-color: #1A1F29 !important;
        border: 1px solid #30363D !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    div.stButton > button:first-child {
        background: linear-gradient(45deg, #00C6FF, #0072FF);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #FF416C, #FF4B2B) !important;
    }

    @media (max-width: 640px) {
        .main-title { font-size: 1.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Streaming Control</h1>", unsafe_allow_html=True)

# Datos y Conexion
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

# --- REGISTRO ---
with st.expander("Nuevo Cliente", expanded=True):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Escribe el nombre")
        
        servicios = st.multiselect(
            "Plataformas y Combos", 
            options=list(PRECIOS.keys()),
            placeholder="Selecciona el servicio",
            key="ms"
        )
        
        dias = [str(i) for i in range(1, 32)]
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

# --- GESTION ---
if not df.empty:
    with st.expander("Gestionar"):
        borrar = st.selectbox("Seleccionar cliente para eliminar", df["Nombre"].unique())
        if st.button("ELIMINAR CLIENTE", type="primary"):
            df_new = df[df["Nombre"] != borrar]
            conn.update(worksheet="Hoja 1", data=df_new)
            st.rerun()

# --- LISTADO ADAPTABLE (Orden solicitado) ---
st.write("---")
st.write("### Lista de Clientes")

if not df.empty:
    # 1. Tabla de Clientes
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
    
    # 2. Total Mensual al final
    total_m = df_v["Total a Pagar"].sum()
    st.metric(label="Total Mensual", value=f"${total_m:,.0f}")
else:
    st.write("No hay clientes registrados")
