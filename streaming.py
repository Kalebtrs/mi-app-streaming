Aquí tienes el código completo y corregido. He integrado la lógica de Google Sheets, la seguridad de los Secrets y el diseño estilo Fintech (Spin) con el banner morado y las tarjetas redondeadas.

Nota Importante: Para que el diseño se vea perfecto, recuerda que debes tener el archivo .streamlit/config.toml en tu GitHub (como hicimos en el paso anterior) y el tema de la App en "Light".

Python
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="Spin Streaming", page_icon="💜", layout="centered")

# 2. INYECCIÓN DE DISEÑO "SPIN BY OXXO" (CSS AGRESIVO)
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    header {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    
    /* Fondo y Contenedor */
    .stApp {
        background-color: #F7F7F9 !important;
    }
    .block-container {
        padding-top: 0rem !important;
        max-width: 500px !important;
    }

    /* Banner Morado Curvo */
    .header-spin {
        background-color: #6221E5;
        color: white;
        padding: 60px 20px 40px 20px;
        margin: 0px -500px 30px -500px;
        text-align: center;
        border-radius: 0 0 50px 50px;
        box-shadow: 0 4px 15px rgba(98, 33, 229, 0.2);
    }

    /* Títulos de sección */
    .section-title {
        color: #1A1A1A;
        font-weight: 700;
        font-size: 18px;
        margin: 20px 0 10px 0;
    }

    /* Iconos Circulares */
    .grid-icons {
        display: flex;
        justify-content: space-around;
        margin-bottom: 25px;
    }
    .circle-wrap { text-align: center; width: 70px; }
    .circle {
        width: 55px;
        height: 55px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        font-size: 24px;
        margin: 0 auto 5px auto;
    }

    /* Tarjetas Blancas de Clientes */
    .movimiento-card {
        background-color: white;
        padding: 18px;
        border-radius: 20px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        border: 1px solid #F0F0F0;
    }

    /* Botón Morado Spin */
    .stButton>button {
        background-color: #6221E5 !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        height: 52px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: 0.3s;
    }
    </style>

    <div class="header-spin">
        <h1 style="margin:0; font-size:26px;">¡Qué gusto verte!</h1>
        <p style="margin:0; opacity:0.8; font-size:14px;">Gestor de Pagos Streaming</p>
    </div>
""", unsafe_allow_html=True)

# 3. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Nombre", "Plataformas", "Total", "Dia"])

df = cargar_datos()

# 4. INTERFAZ VISUAL: "HOY QUIERO..."
st.markdown('<p class="section-title">Hoy quiero...</p>', unsafe_allow_html=True)
st.markdown("""
    <div class="grid-icons">
        <div class="circle-wrap"><div class="circle">🎬</div><small>Netflix</small></div>
        <div class="circle-wrap"><div class="circle">🏰</div><small>Disney</small></div>
        <div class="circle-wrap"><div class="circle">🐉</div><small>HBO</small></div>
        <div class="circle-wrap"><div class="circle">⚽</div><small>Vix</small></div>
    </div>
""", unsafe_allow_html=True)

# 5. FORMULARIO DE REGISTRO
with st.container():
    st.markdown('<p class="section-title">Registrar nuevo servicio</p>', unsafe_allow_html=True)
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Ej: Yolanda")
        servicios = st.multiselect("PLATAFORMAS", ["Netflix", "Disney", "HBO", "Prime", "Vix", "Combo"])
        
        col1, col2 = st.columns(2)
        with col1:
            dia = st.number_input("DÍA DE COBRO", 1, 31, datetime.now().day)
        with col2:
            monto = st.number_input("MONTO $", 0, 2000, 70)
        
        enviar = st.form_submit_button("REGISTRAR MOVIMIENTO")

        if enviar:
            if nombre and servicios:
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Plataformas": ", ".join(servicios),
                    "Total": monto,
                    "Dia": int(dia)
                }])
                df_final = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(data=df_final)
                st.success("✅ Registro guardado en la nube")
                st.rerun()
            else:
                st.warning("⚠️ Por favor llena el nombre y elige al menos 1 servicio")

# 6. ALERTAS DE COBRO
hoy = datetime.now().day
st.markdown(f'<p class="section-title">Cobros de hoy (Día {hoy})</p>', unsafe_allow_html=True)

if not df.empty:
    df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
    pendientes = df[df['Dia'] == hoy]
    
    if not pendientes.empty:
        for _, fila in pendientes.iterrows():
            st.error(f"🚨 COBRAR A: {fila['Nombre']} - ${fila['Total']}")
    else:
        st.info("No hay cobros pendientes para hoy.")

# 7. LISTA DE CLIENTES (MIS MOVIMIENTOS)
st.markdown('<p class="section-title">Mis movimientos (Clientes)</p>', unsafe_allow_html=True)

if not df.empty:
    for i, fila in df.iterrows():
        st.markdown(f"""
        <div class="movimiento-card">
            <div>
                <b style="color:#333; font-size:15px;">{fila['Nombre']}</b><br>
                <small style="color:#888;">{fila['Plataformas']} • Día {int(fila['Dia'])}</small>
            </div>
            <div style="color:#6221E5; font-weight:bold; font-size:18px;">
                ${fila['Total']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para eliminar con clave única
        if st.button(f"Eliminar {fila['Nombre']}", key=f"del_{i}"):
            df_final = df.drop(i)
            conn.update(data=df_final)
            st.rerun()
else:
    st.write("Aún no tienes clientes registrados.")
