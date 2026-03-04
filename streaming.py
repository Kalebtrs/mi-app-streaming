import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# ---------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------
st.set_page_config(page_title="Gestor de Pagos", page_icon="💳")

# ---------------------------------------------------
# ESTILOS MODERNOS TIPO APP
# ---------------------------------------------------
st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-color: #F4F7FF;
}

/* Contenedor tipo app */
.main-card {
    background: white;
    padding: 30px;
    border-radius: 25px;
    box-shadow: 0px 15px 35px rgba(0, 77, 255, 0.15);
    max-width: 500px;
    margin: auto;
}

/* Título principal */
.main-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: #2D3A5D;
    margin-bottom: 25px;
}

/* Subtítulos */
.section-title {
    font-weight: 600;
    color: #004DFF;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput>div>div>input {
    border-radius: 12px;
    border: 2px solid #E0E6FF;
    padding: 10px;
}

/* Botón principal */
.stFormSubmitButton>button {
    width: 100%;
    border-radius: 12px;
    background-color: #004DFF;
    color: white;
    font-weight: 600;
    border: none;
    padding: 10px;
    transition: 0.3s;
}

.stFormSubmitButton>button:hover {
    background-color: #0033AA;
}

/* Tarjetas de clientes */
.client-card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.05);
    border-left: 5px solid #004DFF;
}

/* Alertas */
.alert-card {
    background: #FFEFF0;
    border-left: 5px solid #FF4D4D;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="main-title">GESTOR DE PAGOS</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# PRECIOS
# ---------------------------------------------------
PRECIOS = {
    "Prime Video": 50,
    "HBO": 70,
    "Netflix": 70,
    "Disney": 50,
    "Vix": 30,
    "Combo 1": 85,
    "Combo 2": 100,
    "Combo 3": 110,
    "Combo 4": 115
}

# ---------------------------------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
except:
    df_existente = pd.DataFrame(columns=["Nombre", "Telefono", "Plataformas", "Total", "Dia"])

# ---------------------------------------------------
# FORMULARIO NUEVO CLIENTE
# ---------------------------------------------------
st.markdown('<div class="section-title">Nuevo Cliente</div>', unsafe_allow_html=True)

with st.form("nuevo_cliente", clear_on_submit=True):

    nombre = st.text_input("Nombre Completo")
    telefono = st.text_input("Número de WhatsApp (+52...)")

    st.markdown('<div class="section-title">Servicios</div>', unsafe_allow_html=True)

    plataformas_elegidas = []
    for p in PRECIOS:
        if st.checkbox(f"{p} (${PRECIOS[p]})"):
            plataformas_elegidas.append(p)

    dia_pago = st.number_input("Día de corte", min_value=1, max_value=31, value=datetime.now().day)

    guardar = st.form_submit_button("AÑADIR CLIENTE")

    if guardar:
        if nombre and telefono and plataformas_elegidas:

            if not telefono.startswith("+"):
                telefono = "+" + telefono

            total = sum(PRECIOS[p] for p in plataformas_elegidas)

            nueva_fila = pd.DataFrame([{
                "Nombre": nombre.upper(),
                "Telefono": telefono,
                "Plataformas": ", ".join(plataformas_elegidas),
                "Total": total,
                "Dia": int(dia_pago)
            }])

            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            conn.update(data=df_final)

            st.success("Cliente añadido correctamente ✅")
            st.rerun()

# ---------------------------------------------------
# ALERTAS DEL DÍA
# ---------------------------------------------------
hoy = datetime.now().day

st.markdown(f'<div class="section-title">Alertas de Hoy (Día {hoy})</div>', unsafe_allow_html=True)

if not df_existente.empty:

    df_existente["Dia"] = pd.to_numeric(df_existente["Dia"], errors="coerce")
    deudores = df_existente[df_existente["Dia"] == hoy]

    if not deudores.empty:
        for _, fila in deudores.iterrows():

            mensaje = f"Hola {fila['Nombre']} 👋, recordatorio de pago de {fila['Plataformas']} por ${fila['Total']}. Gracias."
            mensaje_url = urllib.parse.quote(mensaje)

            telefono_limpio = fila["Telefono"].replace("+", "")
            link = f"https://wa.me/{telefono_limpio}?text={mensaje_url}"

            st.markdown(f"""
            <div class="alert-card">
                PAGO DE HOY: {fila['Nombre']} - ${fila['Total']}<br>
                <a href="{link}" target="_blank">Enviar mensaje por WhatsApp</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sin pagos para hoy 🎉")

# ---------------------------------------------------
# LISTA DE CLIENTES
# ---------------------------------------------------
if not df_existente.empty:

    st.markdown('<div class="section-title">Clientes Registrados</div>', unsafe_allow_html=True)

    for i, fila in df_existente.iterrows():

        st.markdown(f"""
        <div class="client-card">
            <b>{fila['Nombre']}</b><br>
            Día de corte: {fila['Dia']}<br>
            Servicios: {fila['Plataformas']}<br>
            Total: <b>${fila['Total']}</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Eliminar {fila['Nombre']}", key=f"del_{i}"):

            df_final = df_existente.drop(i)
            conn.update(data=df_final)

            st.success("Cliente eliminado ✅")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
