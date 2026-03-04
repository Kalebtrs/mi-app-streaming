import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Precios de tu lista
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

st.title("Gestor de Pagos Streaming")

# Conexión a tu hoja "App"
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos
try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
except Exception:
    df_existente = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# Registro
with st.form("nuevo_cliente", clear_on_submit=True):
    st.subheader("Registrar Nuevo Cliente")
    nombre = st.text_input("Nombre del Cliente")
    
    with st.expander("Plataformas (Abrir/Cerrar)"):
        plataformas_elegidas = []
        for p in PRECIOS.keys():
            if st.checkbox(p, key=f"ch_{p}"):
                plataformas_elegidas.append(p)
    
    dia_pago = st.number_input("Dia de corte", min_value=1, max_value=31, value=datetime.now().day)
    boton_guardar = st.form_submit_button("Añadir Cliente")

    if boton_guardar:
        if nombre and plataformas_elegidas:
            total = sum(PRECIOS[p] for p in plataformas_elegidas)
            nueva_fila = pd.DataFrame([{
                "Nombre": nombre.upper(),
                "Plataformas": ", ".join(plataformas_elegidas),
                "Total": total,
                "Dia": dia_pago
            }])
            
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            conn.update(data=df_final)
            st.success(f"Guardado con éxito en tu Google Sheet")
            st.rerun()

# Alertas y Lista
hoy = datetime.now().day
st.header(f"Alertas para hoy (Dia {hoy})")
if not df_existente.empty:
    df_existente['Dia'] = pd.to_numeric(df_existente['Dia'], errors='coerce')
    deudores = df_existente[df_existente['Dia'] == hoy]
    
    for _, fila in deudores.iterrows():
        st.error(f"PAGO: {fila['Nombre']} - ${fila['Total']}")

    st.divider()
    st.subheader("Clientes Registrados")
    for i, fila in df_existente.iterrows():
        with st.expander(f"{fila['Nombre']} - Dia {fila['Dia']}"):
            st.write(f"Servicios: {fila['Plataformas']}")
            st.write(f"Cobro: ${fila['Total']}")
            if st.button("Eliminar", key=f"del_{i}"):
                df_final = df_existente.drop(i)
                conn.update(data=df_final)
                st.rerun()
