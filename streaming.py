import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuracion de la pagina
st.set_page_config(page_title="Gestor Streaming", layout="centered")

# Estilo oscuro personalizado
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stForm { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 20px; }
    .stExpander { background-color: #161B22; border: 1px solid #30363D; }
    h1 { color: #58A6FF !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Control de Clientes</h1>", unsafe_allow_html=True)

# 1. Diccionario de Precios oficial
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

# 2. Conexion con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos
try:
    df = conn.read(worksheet="Hoja 1", ttl=0)
    df = df.dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Nombre", "Plataformas", "Dia", "Total a Pagar"])

# --- SECCION: REGISTRAR ---
with st.expander("Registrar Nuevo Cliente", expanded=True):
    with st.form("nuevo_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente", placeholder="Escribe el nombre...")
        
        # Etiquetas personalizadas
        seleccionadas = st.multiselect(
            "Plataformas y Combos", 
            options=list(PRECIOS.keys()),
            placeholder="Selecciona el servicio",
            key="plataformas_input"
        )
        
        opciones_dias = [str(i) for i in range(1, 32)]
        dia_seleccionado = st.selectbox(
            "Día de Corte", 
            options=opciones_dias, 
            index=None, 
            placeholder="Selecciona dia de corte",
            key="dia_input"
        )
        
        btn_guardar = st.form_submit_button("Guardar en la Base de Datos")
        
        if btn_guardar:
            if nombre and seleccionadas and dia_seleccionado:
                total_actual = sum(PRECIOS.get(p, 0) for p in seleccionadas)
                
                nueva_fila = pd.DataFrame({
                    "Nombre": [nombre.upper()],
                    "Plataformas": [", ".join(seleccionadas)],
                    "Dia": [int(dia_seleccionado)],
                    "Total a Pagar": [total_actual]
                })
                
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                
                try:
                    conn.update(worksheet="Hoja 1", data=df_actualizado)
                    st.success("¡Cliente guardado!")
                    st.rerun()
                except Exception:
                    st.error("Error al guardar")
            else:
                st.warning("Faltan datos por completar")

# --- SECCION: BORRAR ---
if not df.empty:
    with st.expander("Borrar un Cliente"):
        cliente_a_borrar = st.selectbox("Selecciona para eliminar", df["Nombre"].unique())
        if st.button("Confirmar Eliminacion", type="primary"):
            df_reducido = df[df["Nombre"] != cliente_a_borrar]
            conn.update(worksheet="Hoja 1", data=df_reducido)
            st.rerun()

# --- SECCION: TABLA ---
st.write("---")
st.write("### Clientes Activos")
if not df.empty:
    # 1. Definimos y filtramos el orden de las columnas que pediste
    columnas_ordenadas = ["Nombre", "Plataformas", "Dia", "Total a Pagar"]
    df_mostrar = df[[c for c in columnas_ordenadas if c in df.columns]].copy()
    
    # 2. Aseguramos que el total sea numerico para aplicar formato
    df_mostrar["Total a Pagar"] = pd.to_numeric(df_mostrar["Total a Pagar"], errors='coerce').fillna(0)
    
    # 3. Mostramos la tabla con el formato de moneda ($)
    st.dataframe(
        df_mostrar, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Total a Pagar": st.column_config.NumberColumn(format="$%d")
        }
    )
    
    recaudacion = df_mostrar["Total a Pagar"].sum()
    st.metric("Recaudacion Mensual", f"${recaudacion:,.2f}")
else:
    st.write("No hay registros en este momento")
