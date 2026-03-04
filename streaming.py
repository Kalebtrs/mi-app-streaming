import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS: DISEÑO SOBRIO Y MINIMALISTA
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Eliminar recuadros internos de formularios */
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
    
    /* Espacio de 60px entre día de corte y el botón de registro */
    .stForm > div:last-child { padding-top: 60px !important; }

    /* Alineación de flechas y botones a la derecha */
    .stExpander details summary svg { order: 2 !important; margin-left: auto !important; }
    .stExpander details summary { display: flex !important; justify-content: space-between; align-items: center; }

    /* Estilos de Alerta Minimalistas */
    .alerta-pago {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #333;
        background-color: #1e1e1e; /* Fondo oscuro neutro */
    }
    .hoy { border-left: 4px solid #ff4b4b; } /* Solo una línea roja sutil */
    .manana { border-left: 4px solid #ffa500; } /* Solo una línea naranja sutil */
    
    /* Botón de Guardar Elegante (Gris oscuro / Acero) */
    div.stButton > button:first-child {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #464855 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        width: auto !important;
        float: right;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    /* Botón de Reiniciar Ciclo (Gradient más suave) */
    .stButton > button[kind="secondary"] {
        background: #262730 !important;
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
        nombre = st.text_input("Nombre", placeholder="Escribe el nombre...")
        servicios = st.multiselect("Plataformas y Combos", options=list(PRECIOS.keys()))
        dias = [str(i) for i in range(1, 32)]
        dia = st.selectbox("Día de Corte", options=dias, index=None, placeholder="Selecciona día de corte")
        
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
with st.expander("Gestionar", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Reiniciar ciclo de pagos", use_container_width=True):
            df["Pagado"] = "NO"
            conn.update(worksheet="Hoja 1", data=df)
            st.rerun()
    with col_b:
        if not df.empty:
            borrar = st.selectbox("Eliminar cliente", df["Nombre"].unique())
            if st.button("CONFIRMAR ELIMINAR", type="primary", use_container_width=True):
                df = df[df["Nombre"] != borrar]
                conn.update(worksheet="Hoja 1", data=df)
                st.rerun()

# --- PANEL 3: LISTA DE CLIENTES ---
with st.expander("Clientes", expanded=True):
    if not df.empty:
        st.dataframe(
            df[["Nombre", "Plataformas", "Dia", "Total a Pagar", "Pagado"]], 
            use_container_width=True, 
            hide_index=True
        )
        total_m = pd.to_numeric(df["Total a Pagar"]).sum()
        st.metric(label="Ingreso Mensual Esperado", value=f"${total_m:,.0f}")
    else:
        st.info("No hay clientes registrados aún.")

# --- PANEL 4: ALERTAS ---
st.markdown("###  Alertas de Pago")
if not df.empty:
    hoy_dt = datetime.now()
    dia_hoy = hoy_dt.day
    dia_manana = (hoy_dt + timedelta(days=1)).day
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')

    # Alertas de Hoy
    clientes_hoy = df[(df['Dia'] == dia_hoy) & (df['Pagado'] == "NO")]
    if not clientes_hoy.empty:
        st.write(" **Cobros Pendientes para Hoy:**")
        for i, row in clientes_hoy.iterrows():
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f'<div class="alerta-pago hoy"><strong>{row["Nombre"]}</strong> - ${row["Total a Pagar"]}</div>', unsafe_allow_html=True)
            with col_btn:
                # Botón de pago más pequeño y sutil
                if st.button(key=f"pay_{i}"):
                    df.at[i, "Pagado"] = "SÍ"
                    conn.update(worksheet="Hoja 1", data=df)
                    st.rerun()
    
    # Alertas de Mañana
    clientes_manana = df[df['Dia'] == dia_manana]
    if not clientes_manana.empty:
        st.write("**Cobros para Mañana:**")
        for _, row in clientes_manana.iterrows():
            st.markdown(f'<div class="alerta-pago manana"><strong>{row["Nombre"]}</strong> - ${row["Total a Pagar"]}</div>', unsafe_allow_html=True)
    
    if clientes_hoy.empty and clientes_manana.empty:
        st.write("No hay cobros para hoy ni mañana.")
else:
    st.write("Sin alertas pendientes.")
