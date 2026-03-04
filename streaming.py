import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Gestor Streaming", page_icon="🎬")

st.markdown("<h1 style='text-align: center; color: #6221E5;'>🎬 Control de Clientes y Cobros</h1>", unsafe_allow_html=True)

# 1. Diccionario de Precios (Basado en tu imagen)
PRECIOS = {
    "Prime video": 50,
    "HBO": 70,
    "Netflix": 70,
    "Disney": 50,
    "Vix": 30,
    "Combo 1": 85,
    "Combo 2": 100,
    "Combo 3": 110,
    "Combo 4": 115
}

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos actuales
try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# 4. Formulario de Registro
with st.expander("➕ Registrar Nuevo Cliente", expanded=True):
    with st.form("nuevo_cliente"):
        nombre = st.text_input("Nombre del Cliente")
        
        # Selección de plataformas usando las llaves del diccionario
        seleccionadas = st.multiselect("Selecciona las Plataformas / Combos", list(PRECIOS.keys()))
        
        dia = st.number_input("Día de Corte", 1, 31, 1)
        
        # Calcular el total automáticamente
        total_pago = sum(PRECIOS[p] for p in seleccionadas)
        st.info(f"💰 Total calculado: ${total_pago}")
        
        if st.form_submit_button("Guardar en la Base de Datos"):
            if nombre and seleccionadas:
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(seleccionadas)],
                    "Dia": [int(dia)],
                    "Total a Pagar": [total_pago]
                })
                
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                
                try:
                    conn.update(worksheet="Hoja 1", data=df_actualizado)
                    st.success(f"✅ ¡{nombre} registrado! Total: ${total_pago}")
                    st.rerun()
                except Exception as e:
                    st.error("Error al guardar. Verifica los permisos de Editor en el Google Sheet.")
            else:
                st.warning("Completa el nombre y elige al menos una opción.")

# 5. Mostrar Lista de Clientes
st.write("### 📋 Clientes Actuales")
if not df.empty:
    # Mostramos la tabla y añadimos una fila de resumen al final si deseas
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    total_mensual = df["Total a Pagar"].sum()
    st.metric("Ganancia Mensual Estimada", f"${total_mensual}")
else:
    st.info("No hay clientes registrados todavía.")
