import streamlit as st
from datetime import datetime

# Configuracion de memoria y precios
if 'lista_clientes' not in st.session_state:
    st.session_state.lista_clientes = []

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

st.title("Gestor de Pagos Streaming")

# Formulario
with st.form("nuevo_cliente", clear_on_submit=True):
    st.subheader("Registrar Nuevo Cliente")
    
    nombre = st.text_input("Nombre del Cliente")
    
    # Menu que sube y baja para elegir plataformas
    with st.expander("Plataformas (Abrir/Cerrar)"):
        plataformas_elegidas = []
        for p in PRECIOS.keys():
            if st.checkbox(p):
                plataformas_elegidas.append(p)
    
    dia_pago = st.number_input("Dia de corte (1-31)", min_value=1, max_value=31, value=datetime.now().day)
    
    boton_guardar = st.form_submit_button("Añadir Cliente")

    if boton_guardar:
        if nombre and plataformas_elegidas:
            total_calculado = sum(PRECIOS[p] for p in plataformas_elegidas)
            nuevo = {
                "Nombre": nombre.upper(), 
                "Plataformas": ", ".join(plataformas_elegidas),
                "Total": total_calculado, 
                "Dia": dia_pago
            }
            st.session_state.lista_clientes.append(nuevo)
            st.success(f"Registrado: {nombre} - Total: ${total_calculado}")
        elif not nombre:
            st.error("Falta el nombre")
        else:
            st.error("Elige una plataforma")

# Alertas
hoy = datetime.now().day
st.header(f"Alertas para hoy (Dia {hoy})")

deudores_hoy = [c for c in st.session_state.lista_clientes if c['Dia'] == hoy]

if deudores_hoy:
    for c in deudores_hoy:
        st.error(f"PAGO PENDIENTE: {c['Nombre']} - ${c['Total']} [{c['Plataformas']}]")
else:
    st.info("Sin pagos para hoy")

# Lista de Clientes
if st.session_state.lista_clientes:
    st.divider()
    st.subheader("Clientes Registrados")
    
    for i, c in enumerate(st.session_state.lista_clientes):
        with st.expander(f"{c['Nombre']} - Dia {c['Dia']}"):
            st.write(f"Servicios: {c['Plataformas']}")
            st.write(f"Cobro: ${c['Total']}")
            if st.button(f"Eliminar", key=f"del_{i}"):
                st.session_state.lista_clientes.pop(i)
                st.rerun()
