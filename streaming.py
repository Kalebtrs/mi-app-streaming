import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración visual de la página
st.set_page_config(
    page_title="Control de Streaming",
    page_icon="🎬",
    layout="centered"
)

# Estilos para que se vea igual a tu captura
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

# 2. Conexión a Google Sheets
# Nota: "gsheets" es el nombre que debe coincidir con [connections.gsheets] en tus Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Intentamos leer la hoja para verificar la conexión
    df = conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
except Exception as e:
    st.error("❌ Error de conexión. Revisa que tus 'Secrets' en Streamlit tengan el formato TOML correcto y que la llave privada sea válida.")
    st.info("Asegúrate de haber compartido el Google Sheet con el correo de la Cuenta de Servicio como 'Editor'.")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 3. Formulario de Registro (Interfaz de tu captura)
with st.container():
    nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="¿A quién registramos?")
    
    opciones_tv = ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"]
    plataformas_sel = st.multiselect("PLATAFORMAS", opciones_tv, placeholder="Selecciona la plataforma")
    
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
                
                # Combinar con los datos existentes
                df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
                
                # Actualizar la hoja de Google
                conn.update(worksheet="Hoja 1", data=df_actualizado)
                
                st.success(f"✅ ¡{nombre} registrado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("⚠️ Por favor rellena el nombre y selecciona al menos una plataforma.")

# 4. Lista de Clientes registrados
st.write("---")
st.markdown("Lista de Clientes")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.write("No hay clientes registrados todavía.")


