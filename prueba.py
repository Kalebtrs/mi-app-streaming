import streamlit as st
from datetime import datetime
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Streaming", layout="wide")

# 1. Definición de Precios (Basado en tu tabla)
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, 
    "Disney": 50, "Vix": 30, "Combo 1": 85, 
    "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

st.title("📱 Gestor de Pagos Streaming")

# 2. Formulario para agregar/editar cliente
with st.expander("➕ Agregar o Editar Cliente"):
    nombre = st.text_input("Nombre del Cliente")
    dia_pago = st.number_input("Día de pago (1-31)", min_value=1, max_value=31, value=15)
    
    st.write("Selecciona los servicios activos:")
    col1, col2, col3 = st.columns(3)
    
    servicios_seleccionados = []
    # Creamos checkboxes para cada plataforma
    for i, plataforma in enumerate(PRECIOS.keys()):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(plataforma):
                servicios_seleccionados.append(plataforma)

# 3. Cálculo de Total Interactivo
total_cliente = sum(PRECIOS[s] for s in servicios_seleccionados)
st.metric(label="Total a Pagar", value=f"${total_cliente}")

# 4. Sistema de Alertas de Hoy
dia_actual = datetime.now().day
st.subheader(f"📅 Alertas para hoy (Día {dia_actual})")

# Ejemplo de datos (En una app real, esto vendría de una base de datos)
clientes_demo = [
    {"Nombre": "CAPISTRAN", "Dia": 30, "Total": 50},
    {"Nombre": "KARELI", "Dia": 4, "Total": 70}, # Ejemplo para hoy si fuera día 4
]

for c in clientes_demo:
    if c["Dia"] == dia_actual:
        st.error(f"⚠️ {c['Nombre']} debe pagar hoy: ${c['Total']}")
    elif abs(c["Dia"] - dia_actual) <= 2:
        st.warning(f"🔔 {c['Nombre']} paga pronto (Día {c['Dia']})")

# 5. Tabla de Precios de Referencia
with st.sidebar:
    st.header("Lista de Precios")
    df_precios = pd.DataFrame(list(PRECIOS.items()), columns=['Plataforma', 'Precio'])
    st.table(df_precios)