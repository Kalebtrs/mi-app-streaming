import streamlit as st
from datetime import datetime

# 1. Configuración de la "Memoria" de la App
if 'lista_clientes' not in st.session_state:
    st.session_state.lista_clientes = []

st.title("📱 Gestor de Pagos Streaming")

# 2. Formulario para agregar clientes con Plataformas
with st.form("nuevo_cliente"):
    st.subheader("🚀 Registrar Nuevo Servicio")
    
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Nombre del Cliente")
        monto = st.number_input("Monto a pagar ($)", min_value=0)
    
    with col_b:
        # Aquí recuperamos las plataformas que tenías
        plataforma = st.selectbox("Plataforma / Combo", [
            "Netflix", 
            "Disney+ / Star+", 
            "HBO Max", 
            "Prime Video", 
            "Paramount+", 
            "Combo Especial",
            "Otro"
        ])
        dia_pago = st.number_input("Día de corte (1-31)", min_value=1, max_value=31)
    
    boton_guardar = st.form_submit_button("Añadir a la lista")

    if boton_guardar:
        if nombre:
            nuevo = {
                "Nombre": nombre.upper(), 
                "Plataforma": plataforma,
                "Total": monto, 
                "Dia": dia_pago
            }
            st.session_state.lista_clientes.append(nuevo)
            st.success(f"✅ {nombre} registrado en {plataforma}")
        else:
            st.error("Por favor escribe un nombre")

# 3. Alertas para hoy (Día automático)
hoy = datetime.now().day
st.header(f"📅 Alertas para hoy (Día {hoy})")

deudores_hoy = [c for c in st.session_state.lista_clientes if c['Dia'] == hoy]

if deudores_hoy:
    for c in deudores_hoy:
        # Alerta roja como la que tenías antes
        st.error(f"⚠️ {c['Nombre']} debe pagar hoy: ${c['Total']} ({c['Plataforma']})")
else:
    st.info("No hay pagos pendientes para hoy.")

# 4. Tabla de Clientes Activos
if st.session_state.lista_clientes:
    st.divider()
    st.subheader("👥 Clientes Registrados")
    
    for i, c in enumerate(st.session_state.lista_clientes):
