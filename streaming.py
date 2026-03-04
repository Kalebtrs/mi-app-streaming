import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Precios actualizados
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

st.title("Gestor de Pagos Streaming")

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos con seguridad
try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
    # Verificamos si la columna 'Dia' existe, si no, la creamos vacía
    if 'Dia' not in df_existente.columns:
        df_existente['Dia'] = None
except Exception:
    df_existente = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# 4. Formulario
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
            conn.update(data=df_final)
            st.success(f"¡Guardado con éxito!")
            st.rerun()

# 5. Alertas (Aquí es donde daba el error)
hoy = datetime.now().day
st.header(f"Alertas para hoy (Dia {hoy})")

if not df_existente.empty and 'Dia' in df_existente.columns:
    # Convertimos a número con cuidado
    df_existente['Dia'] = pd.to_numeric(df_existente['Dia'], errors='coerce')
    deudores = df_existente[df_existente['Dia'] == hoy]
    
    if not deudores.empty:
        for _, fila in deudores.iterrows():
            st.error(f"PAGO PENDIENTE: {fila['Nombre']} - ${fila['Total']}")
    else:
        st.info("Sin pagos para hoy")

# 6. Lista de Clientes
if not df_existente.empty:
    st.divider()
    st.subheader("Clientes Registrados")
    for i, fila in df_existente.iterrows():
        with st.expander(f"{fila.get('Nombre', 'S/N')} - Dia {fila.get('Dia', '0')}"):
            st.write(f"Servicios: {fila.get('Plataformas', 'N/A')}")
            st.write(f"Cobro: ${fila.get('Total', 0)}")
            if st.button("Eliminar", key=f"del_{i}"):
                df_final = df_existente.drop(i)
                conn.update(data=df_final)
                st.rerun()
