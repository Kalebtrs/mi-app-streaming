import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Streaming",
    page_icon="🎬",
    layout="centered"
)

# Estilos personalizados para que se vea profesional
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #6221E5;
        color: white;
    }
    .titulo {
        text-align: center;
        color: #6221E5;
        font-family: 'Arial';
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🎬 Control de Clientes Streaming</h1>", unsafe_allow_html=True)
st.write("---")

# 1. ESTABLECER CONEXIÓN
# Esta línea busca automáticamente los datos en la pestaña 'Secrets' de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. FUNCIÓN PARA LEER DATOS
def cargar_datos():
    try:
        # worksheet="Hoja 1" debe coincidir con el nombre de la pestaña abajo en tu Excel
        return conn.read(worksheet="Hoja 1", ttl=0).dropna(how="all")
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

df = cargar_datos()

# 3. FORMULARIO DE REGISTRO
with st.expander("➕ Registrar Nuevo Cliente", expanded=True):
    with st.form("formulario_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Cliente")
            dia_corte = st.number_input("Día de Corte", min_value=1, max_value=31, step=1)
            
        with col2:
            opciones_tv = ["Netflix", "Disney+", "HBO Max", "Vix Premium", "Prime Video", "Paramount+", "Combo Total"]
            plataformas = st.multiselect("Plataformas", opciones_tv)
            
        submit = st.form_submit_button("Guardar en la Base de Datos")

        if submit:
            if nombre and plataformas and dia_corte:
                # Crear nueva fila
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(plataformas),
                    "Dia": int(dia_corte)
                }])
                
                # Unir con datos existentes
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                
                # Subir a Google Sheets
                conn.update(worksheet="Hoja 1", data=df_actualizado)
                
                st.success(f"✅ Cliente {nombre} guardado correctamente.")
                st.rerun() # Recargar la app para mostrar los cambios
            else:
                st.warning("Por favor, rellena todos los campos.")

# 4. VISUALIZACIÓN Y ELIMINACIÓN
st.markdown("### 📋 Lista de Clientes")

if not df.empty:
    # Mostramos los datos de forma limpia
    for i, fila in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 4, 1])
            c1.write(f"**{fila['Nombre']}**")
            c2.write(f"📺 {fila['Plataformas']} (Corte: día {int(fila['Dia'])})")
            
            # Botón de eliminar para cada registro
            if c3.button("🗑️", key=f"btn_{i}"):
                df_nuevo = df.drop(i)
                conn.update(worksheet="Hoja 1", data=df_nuevo)
                st.info("Registro eliminado.")
                st.rerun()
            st.divider()
else:
    st.info("No hay clientes registrados todavía.")
