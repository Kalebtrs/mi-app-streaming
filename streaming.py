import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuracion de la pagina
st.set_page_config(page_title="Gestor Streaming")

st.markdown("<h1 style='text-align: center; color: #6221E5;'>Control de Clientes</h1>", unsafe_allow_html=True)

# 1. Diccionario de Precios
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

# 2. Conexion con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos y asegurar columnas
try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
    if "Total a Pagar" not in df.columns:
        df["Total a Pagar"] = 0
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# --- SECCION: REGISTRAR ---
with st.expander("Registrar Nuevo Cliente", expanded=True):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente")
        seleccionadas = st.multiselect("Selecciona las Plataformas / Combos", list(PRECIOS.keys()))
        
        # CAMBIO AQUI: Lista de dias del 1 al 31 con mensaje inicial
        opciones_dias = ["Selecciona dia de corte"] + [str(i) for i in range(1, 32)]
        dia_seleccionado = st.selectbox("Dia de Corte", opciones_dias)
        
        total_pago = sum(PRECIOS[p] for p in seleccionadas)
        st.write(f"Total a pagar: ${total_pago}")
        
        btn_guardar = st.form_submit_button("Guardar en la Base de Datos")
        
        if btn_guardar:
            # Validacion: Que el nombre no este vacio, haya plataformas y el dia no sea el mensaje inicial
            if nombre and seleccionadas and dia_seleccionado != "Selecciona dia de corte":
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(seleccionadas)],
                    "Dia": [int(dia_seleccionado)],
                    "Total a Pagar": [total_pago]
                })
                
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                
                try:
                    conn.update(worksheet="Hoja 1", data=df_actualizado)
                    st.success("Registro guardado exitosamente")
                    st.rerun()
                except Exception:
                    st.error("Error al conectar con la base de datos")
            else:
                st.warning("Por favor rellena el nombre, selecciona plataformas y elige un dia de corte valido")

# --- SECCION: BORRAR ---
if not df.empty:
    with st.expander("Borrar un Cliente"):
        cliente_a_borrar = st.selectbox("Selecciona el cliente para eliminar", df["Nombre"].unique())
        if st.button("Confirmar Eliminacion", type="primary"):
            df_reducido = df[df["Nombre"] != cliente_a_borrar]
            try:
                conn.update(worksheet="Hoja 1", data=df_reducido)
                st.info("Cliente eliminado")
                st.rerun()
            except Exception:
                st.error("No se pudo completar la eliminacion")

# --- SECCION: TABLA DE DATOS ---
st.write("---")
st.write("### Lista de Clientes Activos")
if not df.empty:
    df["Total a Pagar"] = pd.to_numeric(df["Total a Pagar"], errors='coerce').fillna(0)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    total_mensual = df["Total a Pagar"].sum()
    st.metric("Recaudacion Total Mensual", f"${total_mensual:,.2f}")
else:
    st.write("No hay registros activos")
