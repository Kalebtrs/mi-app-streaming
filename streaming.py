import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Precios actualizados
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

st.title("Gestor de Pagos Streaming")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos con manejo de errores para columnas inexistentes
try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
except Exception:
    df_existente = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# Formulario
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
                "Dia": int(dia_pago)
            }])
            
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            # Intentar guardar
            conn.update(data=df_final)
            st.success("¡Cliente guardado!")
            st.rerun()

# Alertas del día (Protección contra KeyError)
hoy = datetime.now().day
st.header(f"Alertas para hoy (Dia {hoy})")

if not df_existente.empty and 'Dia' in df_existente.columns:
    df_existente['Dia'] = pd.to_numeric(df_existente['Dia'], errors='coerce')
    deudores = df_existente[df_existente['Dia'] == hoy]
    
    if not deudores.empty:
        for _, fila in deudores.iterrows():
            st.error(f"PAGO PENDIENTE: {fila['Nombre']} - ${fila['Total']}")
    else:
        st.info("Sin pagos para hoy")

# Lista de Clientes
if not df_existente.empty:
    st.divider()
    st.subheader("Clientes Registrados")
    for i, fila in df_existente.iterrows():
        # Uso de .get() para evitar errores si faltan columnas
        nombre_c = fila.get('Nombre', 'S/N')
        dia_c = fila.get('Dia', '?')
        with st.expander(f"{nombre_c} - Dia {dia_c}"):
            st.write(f"Servicios: {fila.get('Plataformas', 'No especificado')}")
            st.write(f"Cobro: ${fila.get('Total', 0)}")
            if st.button("Eliminar", key=f"del_{i}"):
                df_final = df_existente.drop(i)
                conn.update(data=df_final)
                st.rerun()
