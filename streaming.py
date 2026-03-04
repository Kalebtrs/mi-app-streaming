import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Gestor Streaming", page_icon="🎬")

st.markdown("<h1 style='text-align: center; color: #6221E5;'>🎬 Control de Clientes</h1>", unsafe_allow_html=True)

# 1. Diccionario de Precios
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos y asegurar columnas
try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
    if "Total a Pagar" not in df.columns:
        df["Total a Pagar"] = 0
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# --- SECCIÓN A: REGISTRAR ---
with st.expander("➕ Registrar Nuevo Cliente"):
    with st.form("nuevo_cliente"):
        nombre = st.text_input("Nombre del Cliente")
        seleccionadas = st.multiselect("Selecciona las Plataformas / Combos", list(PRECIOS.keys()))
        dia = st.number_input("Día de Corte", 1, 31, 1)
        total_pago = sum(PRECIOS[p] for p in seleccionadas)
        
        if st.form_submit_button("Guardar en la Base de Datos"):
            if nombre and seleccionadas:
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(seleccionadas)],
                    "Dia": [int(dia)],
                    "Total a Pagar": [total_pago]
                })
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Hoja 1", data=df_actualizado)
                st.success(f"✅ ¡{nombre} registrado!")
                st.rerun()

# --- SECCIÓN B: ELIMINAR (Lo nuevo) ---
if not df.empty:
    with st.expander("🗑️ Borrar un Cliente"):
        cliente_a_borrar = st.selectbox("Selecciona el cliente que deseas eliminar", df["Nombre"].unique())
        if st.button("Eliminar Cliente Definitivamente", type="primary"):
            # Filtramos el DataFrame para quitar al cliente seleccionado
            df_reducido = df[df["Nombre"] != cliente_a_borrar]
            
            try:
                conn.update(worksheet="Hoja 1", data=df_reducido)
                st.warning(f"❌ Cliente {cliente_a_borrar} eliminado.")
                st.rerun()
            except Exception as e:
                st.error("No se pudo eliminar en Google Sheets.")

# --- SECCIÓN C: TABLA Y MÉTRICAS ---
st.write("---")
st.write("### 📋 Lista de Clientes Activos")
if not df.empty:
    df["Total a Pagar"] = pd.to_numeric(df["Total a Pagar"], errors='coerce').fillna(0)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    total_mensual = df["Total a Pagar"].sum()
    st.metric("Recaudación Total", f"${total_mensual:,.2f}")
else:
    st.info("La lista está vacía.")
