import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS: SIMETRÍA Y ESTILO MINIMALISTA
st.markdown("""
    <style>
    /* Título limpio y centrado */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    
    /* Reset de formularios para eliminar espacios excesivos */
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
    
    /* Ajuste de espaciado interno del formulario para simetría */
    .stForm > div { padding-top: 20px !important; }

    /* Alineación de flechas de expander */
    .stExpander details summary svg { order: 2 !important; margin-left: auto !important; }
    .stExpander details summary { display: flex !important; justify-content: space-between; align-items: center; font-weight: 600; }

    /* Cuadros de Alerta Neutros */
    .alerta-pago {
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
        border: 1px solid #333;
        background-color: #111;
        font-family: sans-serif;
    }
    .hoy { border-left: 3px solid #E50914; } 
    .manana { border-left: 3px solid #555; }
    
    /* Botón de Guardar Simétrico */
    div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 700 !important;
        float: right;
        margin-top: 20px;
    }

    /* Ajuste de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Streaming Control</h1>", unsafe_allow_html=True)

# 3. DATOS Y CONEXIÓN
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
    if "Pagado" not in df.columns:
        df["Pagado"] = "NO"
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar", "Pagado"])

# --- PANEL 1: NUEVO CLIENTE ---
with st.expander("Nuevo Cliente", expanded=False):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Escriba el nombre completo...")
        servicios = st.multiselect("Plataformas y Combos", options=list(PRECIOS.keys()))
        dias = [str(i) for i in range(1, 32)]
        dia = st.selectbox("Dia de Corte", options=dias, index=None, placeholder="Seleccione el dia")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and servicios and dia:
                total = sum(PRECIOS.get(s, 0) for s in servicios)
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(servicios)],
                    "Dia": [int(dia)],
                    "Total a Pagar": [total],
                    "Pagado": ["NO"]
                })
                df = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Hoja 1", data=df)
                st.rerun()

# --- PANEL 2: GESTIONAR ---
with st.expander("Gestionar Sistema", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Reiniciar Ciclo", use_container_width=True):
            df["Pagado"] = "NO"
            conn.update(worksheet="Hoja 1", data=df)
            st.rerun()
    with col_b:
        if not df.empty:
            borrar = st.selectbox("Eliminar Registro", df["Nombre"].unique())
            if st.button("Confirmar Eliminacion", type="primary", use_container_width=True):
                df = df[df["Nombre"] != borrar]
                conn.update(worksheet="Hoja 1", data=df)
                st.rerun()

# --- PANEL 3: LISTA DE CLIENTES ---
with st.expander("Base de Clientes", expanded=True):
    if not df.empty:
        st.dataframe(
            df[["Nombre", "Plataformas", "Dia", "Total a Pagar", "Pagado"]], 
            use_container_width=True, 
            hide_index=True
        )
        total_m = pd.to_numeric(df["Total a Pagar"]).sum()
        st.metric(label="Ingreso Mensual", value=f"${total_m:,.0f}")
    else:
        st.info("Sin registros en la base de datos.")

# --- PANEL 4: ALERTAS ---
st.write("---")
st.subheader("Alertas de Cobro")

if not df.empty:
    hoy_dt = datetime.now()
    dia_hoy = hoy_dt.day
    dia_manana = (hoy_dt + timedelta(days=1)).day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')

    # Alertas de Hoy
    clientes_hoy = df[(df['Dia'] == dia_hoy) & (df['Pagado'] == "NO")]
    if not clientes_hoy.empty:
        st.write("**Pendientes Hoy**")
        for i, row in clientes_hoy.iterrows():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(f'<div class="alerta-pago hoy"><strong>{row["Nombre"]}</strong> | Total: ${row["Total a Pagar"]}</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("PAGADO", key=f"pay_{i}"):
                    df.at[i, "Pagado"] = "SI"
                    conn.update(worksheet="Hoja 1", data=df)
                    st.rerun()
    
    # Alertas de Mañana
    clientes_manana = df[df['Dia'] == dia_manana]
    if not clientes_manana.empty:
        st.write("**Proximos Mañana**")
        for _, row in clientes_manana.iterrows():
            st.markdown(f'<div class="alerta-pago manana">{row["Nombre"]} | Total: ${row["Total a Pagar"]}</div>', unsafe_allow_html=True)
    
    if clientes_hoy.empty and clientes_manana.empty:
        st.write("No hay cobros programados para hoy o mañana.")
else:
    st.write("No hay datos para generar alertas.")
