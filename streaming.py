import streamlit as st
from datetime import datetime

# 1. Configuración de la "Memoria" de la App
if 'lista_clientes' not in st.session_state:
    st.session_state.lista_clientes = []

st.title("📱 Mi Gestor de Pagos")

# 2. Formulario para agregar clientes
with st.form("nuevo_cliente"):
    st.subheader("Registrar Nuevo Cliente")
    nombre = st.text_input("Nombre del Cliente")
    monto = st.number_input("Monto a pagar ($)", min_value=0)
    dia_pago = st.number_input("Día de corte (1-31)", min_value=1, max_value=31)
    
    boton_guardar = st.form_submit_button("Guardar Cliente")

    if boton_guardar:
        if nombre:
            nuevo = {"Nombre": nombre.upper(), "Total": monto, "Dia": dia_pago}
            st.session_state.lista_clientes.append(nuevo)
            st.success(f"✅ {nombre} agregado con éxito")
        else:
            st.error("Por favor escribe un nombre")

# 3. Alertas para hoy
hoy = datetime.now().day
st.header(f"📅 Alertas para hoy (Día {hoy})")

deudores_hoy = [c for c in st.session_state.lista_clientes if c['Dia'] == hoy]

if deudores_hoy:
    for c in deudores_hoy:
        st.error(f"⚠️ {c['Nombre']} debe pagar hoy: ${c['Total']}")
else:
    st.info("No hay pagos pendientes para hoy.")

# 4. Lista total de clientes
if st.session_state.lista_clientes:
    st.subheader("Lista de Clientes Registrados")
    for i, c in enumerate(st.session_state.lista_clientes):
        col1, col2 = st.columns([3, 1])
        col1.write(f"👤 **{c['Nombre']}** - Paga el día {c['Dia']} (${c['Total']})")
        if col2.button("Eliminar", key=f"btn_{i}"):
            st.session_state.lista_clientes.pop(i)
            st.rerun()
