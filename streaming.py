import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuracion de precios segun tu tabla
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

st.title("Gestor de Pagos Streaming")

# Conexion a tu Google Sheet usando el ID: 12qBXQpDFKoke8pr6nSnFCF3vl3e7D1jNgjv7Ji5b2c4
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
try:
    df_existente = conn.read(ttl=0)
    # Limpiar filas vacias si las hay
    df_existente = df_existente.dropna(how="all")
except:
    df_existente = pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

# Formulario para registrar
with st.form("nuevo_cliente", clear_on_submit=True):
    st.subheader("Registrar Nuevo Cliente")
    nombre = st.text_input("Nombre del Cliente")
    
    # Menu plegable sin emojis que sube y baja
    with st.expander("Plataformas (Abrir/Cerrar)"):
        plataformas_elegidas = []
        for p in PRECIOS.keys():
            if st.checkbox(p, key=f"ch_{p}"):
                plataformas_elegidas.append(p)
    
    dia_pago = st.number_input("Dia de corte (1-31)", min_value=1, max_value=31, value=datetime.now().day)
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
            
            # Guardar en la nube
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            conn.update(data=df_final)
            st.success(f"Guardado con exito: {nombre}")
            st.rerun()
        elif not nombre:
            st.error("Falta el nombre")
        else:
            st.error("Elige una plataforma")

# Seccion de Alertas
hoy = datetime.now().day
st.header(f"Alertas para hoy (Dia {hoy})")
# Filtrar deudores del dia
deudores = df_existente[df_existente['Dia'].astype(float) == hoy]

if not deudores.empty:
    for _, fila in deudores.iterrows():
        st.error(f"PAGO PENDIENTE: {fila['Nombre']} - ${fila['Total']} [{fila['Plataformas']}]")
else:
    st.info("Sin pagos para hoy")

# Lista de Clientes Registrados
if not df_existente.empty:
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
