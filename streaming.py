import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Gestor Streaming", page_icon="🎬")

st.markdown("<h1 style='text-align: center; color: #6221E5;'>🎬 Registro de Clientes</h1>", unsafe_allow_html=True)

# 1. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Leer datos actuales (Hoja 1 debe ser el nombre exacto de la pestaña)
try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    # Limpiar filas vacías si existen
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"Error al leer la hoja: {e}")
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia"])

# 3. Formulario para añadir clientes
with st.form("nuevo_cliente"):
    nombre = st.text_input("Nombre del Cliente")
    plataformas = st.multiselect("Plataformas", ["Netflix", "Disney+", "HBO Max", "Prime Video", "Vix Premium"])
    dia = st.number_input("Día de Pago", 1, 31, 1)
    
    if st.form_submit_button("Guardar"):
        if nombre and plataformas:
            # Crear nueva fila
            nueva_fila = pd.DataFrame({
                "Nombre": [nombre.upper()],
                "Plataformas": [", ".join(plataformas)],
                "Dia": [int(dia)]
            })
            
            # Unir con datos viejos
            df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            
            # Subir a Google Sheets
            try:
                conn.update(worksheet="Hoja 1", data=df_actualizado)
                st.success(f"✅ ¡{nombre} guardado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}. ¿Diste permisos de EDITOR al correo de la cuenta de servicio?")
        else:
            st.warning("Por favor completa el nombre y elige al menos una plataforma.")

# 4. Mostrar tabla
st.write("### 📋 Lista Actual")
st.dataframe(df, use_container_width=True, hide_index=True)
