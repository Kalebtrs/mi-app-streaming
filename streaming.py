import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="Streaming App", layout="centered")

# 2. CSS
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

    div[data-testid="stExpander"] {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    div.stButton > button:first-child {
        background: linear-gradient(45deg, #FF0080, #FF8C00, #40E0D0) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }

    .pago-alerta {
        background-color: rgba(255, 75, 75, 0.12);
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .no-alerta {
        background-color: rgba(0, 255, 150, 0.1);
        border-left: 5px solid #00cc88;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Streaming Control</h1>", unsafe_allow_html=True)

# Datos
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

df["Dia"] = pd.to_numeric(df["Dia"], errors="coerce")

# =========================================================
# 🔔 1. ALERTAS (SUELTAS, NO EN PANEL)
# =========================================================

from zoneinfo import ZoneInfo
hoy = datetime.now(ZoneInfo("America/Mexico_City")).day
clientes_hoy = df[df["Dia"] == hoy]

if not clientes_hoy.empty:
    for _, row in clientes_hoy.iterrows():
        st.markdown(f"""
            <div class="pago-alerta">
                <strong>{row['Nombre']}</strong> debe pagar hoy 
                <strong>${row['Total a Pagar']}</strong><br>
                <small>Servicios: {row['Plataformas']}</small>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="no-alerta">
            Hoy es día {hoy}. No hay cobros programados 🎉
        </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================================================
# ➕ 2. NUEVO CLIENTE
# =========================================================

with st.expander("Nuevo Cliente"):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Escribe el nombre...")
        servicios = st.multiselect("Plataformas y Combos", options=list(PRECIOS.keys()))
        dias = [str(i) for i in range(1, 32)]
        dia = st.selectbox("Día de Corte", options=dias, index=None)

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

# =========================================================
# ⚙️ 3. GESTIONAR
# =========================================================

with st.expander("Gestionar"):
    if not df.empty:
        borrar = st.selectbox("Seleccionar para eliminar", df["Nombre"].unique())
        if st.button("ELIMINAR CLIENTE"):
            df_new = df[df["Nombre"] != borrar]
            conn.update(worksheet="Hoja 1", data=df_new)
            st.rerun()
    else:
        st.info("No hay datos para gestionar.")

# =========================================================
# 📋 4. CLIENTES ACTIVOS (PANEL)
# =========================================================

with st.expander("Clientes Activos"):
    if not df.empty:
        st.dataframe(
            df[["Nombre", "Plataformas", "Dia", "Total a Pagar"]],
            use_container_width=True,
            hide_index=True
        )

        total_m = pd.to_numeric(df["Total a Pagar"]).sum()
        st.metric(
            label="Recaudación Mensual Esperada",
            value=f"${total_m:,.0f}"
        )
    else:
        st.info("No hay clientes registrados aún.")


