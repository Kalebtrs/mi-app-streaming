import streamlit as st
from datetime import datetime

# 1. Configuración de la "Memoria" y Precios
if 'lista_clientes' not in st.session_state:
    st.session_state.lista_clientes = []

# Diccionario de precios actualizado según tu tabla
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

st.title("📱 Gestor de Pagos Streaming")

# 2. Formulario para agregar clientes
with st.form("nuevo_cliente"):
    st.subheader("Registrar Nuevo Cliente")
    
    nombre = st.text_input("Nombre del Cliente")
    
    # Selección múltiple de plataformas
    plataformas_elegidas = st.multiselect(
        "Selecciona la(s) plataforma(s)", 
        options=list(PRECIOS.keys())
    )
    
    dia_pago = st.number_input("Día de corte (1-31)", min_value=1, max_value=31, value=datetime.now().day)
    
    boton_guardar = st.form_submit_button("Añadir Cliente")

    if boton_guardar:
        if nombre and plataformas_elegidas:
            # Cálculo automático del total basado en los precios
            total_calculado = sum(PRECIOS[p] for p in plataformas_elegidas)
            
            nuevo = {
                "Nombre": nombre.upper(), 
                "Plataformas": ", ".join(plataformas_elegidas),
                "Total": total_calculado, 
                "Dia": dia_pago
            }
            st.session_state.lista_clientes.append(nuevo)
            st.success(f"✅ {nombre} registrado con un total de ${total_calculado}")
        elif not nombre:
            st.error("Escribe el nombre del cliente.")
        else:
            st.error("Selecciona al menos una plataforma.")

# 3. Alertas para hoy
hoy = datetime.now().day
st.header(f" Alertas para hoy (Día {hoy})")

deudores_hoy = [c for c in st.session_state.lista_clientes if c['Dia'] == hoy]

if deudores_hoy:
    for c in deudores_hoy:
        # Formato de alerta similar al original
        st.error(f"⚠️ {c['Nombre']} debe pagar hoy: ${c['Total']} [{c['Plataformas']}]")
else:
    st.info("No hay pagos pendientes para hoy.")

# 4. Tabla de Clientes Activos
if st.session_state.lista_clientes:
    st.divider()
    st.subheader("Clientes Registrados")
    
    for i, c in enumerate(st.session_state.lista_clientes):
        with st.expander(f" {c['Nombre']} - Día {c['Dia']}"):
            st.write(f"**Servicios:** {c['Plataformas']}")
            st.write(f"**Total a cobrar:** ${c['Total']}")
            if st.button(f"Eliminar Cliente", key=f"del_{i}"):
                st.session_state.lista_clientes.pop(i)
                st.rerun()
