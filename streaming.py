import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Streaming",
    page_icon="🎬",
    layout="centered"
)

# Estilos visuales
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #6221E5;
        color: white;
    }
    .titulo-container {
        background-color: #6221E5;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo-container'><h1>¡Qué gusto verte!</h1><p>Tu Central de Streaming</p></div>", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    # Creamos la conexión usando los secretos configurados en el Dashboard
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos los datos existentes (ajusta "Hoja 1" al nombre real de tu pestaña)
    df = conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
except Exception as e:
    st.error("❌ Error de conexión o formato de llave.")
    st.info("Revisa que en Secrets hayas usado comillas triples para la private_key.")
    st.write(f"Detalle técnico: {e}")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# --- FORMULARIO DE REGISTRO ---
with st.container():
    nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
    
    opciones_tv = ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"]
    plataformas_sel = st.multiselect("PLATAFORMAS", opciones_tv)
    
    dia_corte = st.number_input("DÍA DE CORTE", min_value=1, max_value=31, value=1)
    
    boton_guardar = st.button("GUARDAR CLIENTE")

    if boton_guardar:
        if nombre and plataformas_sel:
            try:
                # Crear el nuevo registro
                nuevo_registro = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas_sel),
                    "Dia": int(dia_corte)
                }])
                
                # Combinar con los datos anteriores
                df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
                
                # Subir a Google Sheets
                conn.update(worksheet="Hoja 1", data=df_actualizado)
                
                st.success(f"✅ ¡{nombre} guardado!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("⚠️ Completa los campos antes de guardar.")

# --- LISTA DE CLIENTES ---
st.write("---")
st.markdown("### 📋 Clientes Actuales")
if not df.empty:
    # Mostramos una tabla sencilla
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Opción para borrar el último registro en caso de error
    if st.button("Eliminar último registro"):
        df_borrar = df[:-1]
        conn.update(worksheet="Hoja 1", data=df_borrar)
        st.rerun()
else:
    st.info("No hay datos para mostrar.")
