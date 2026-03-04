import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuración de página con icono de calendario
st.set_page_config(page_title="Gestor de Pagos", page_icon="📅")

# --- ESTILOS CSS PERSONALIZADOS (Inspirado en image_8.png) ---
st.markdown("""
<style>
    /* Estilo para el contenedor principal */
    {
        background-color: #F0F2F6;
    }
    
    /* Títulos grandes y limpios (como "DEVICES") */
    {
        color: #004DFF;
        font-weight: 700;
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Subtítulos centrados */
    {
        color: #2D3A5D;
        text-align: center;
        font-weight: 600;
        margin-top: 20px;
    }

    /* Contenedor de las tarjetas de plataformas (para centrar) */
    {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 15px;
        margin-bottom: 30px;
    }

    /* Estilo para cada tarjeta de plataforma */
    {
        background-color: #FFFFFF;
        border: 2px solid #D0D9FF;
        border-radius: 12px;
        padding: 15px;
        width: 140px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0, 77, 255, 0.05);
        cursor: pointer;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    /* Efecto de hover al pasar el ratón por encima */
    {
        transform: translateY(-5px);
        border-color: #004DFF;
    }

    /* Nombre de la plataforma dentro de la tarjeta */
    {
        font-weight: 700;
        color: #2D3A5D;
        font-size: 1.1em;
        margin-bottom: 8px;
    }

    /* Precio dentro de la tarjeta */
    {
        font-weight: 600;
        color: #004DFF;
        font-size: 1.3em;
    }
    
    /* Estilo para la lista de clientes (cajas grandes para cada cliente) */
    {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #004DFF;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.03);
    }
    
    /* Estilo para las alertas de pago (al estilo de los errores de image_2.png) */
    {
        background-color: #FFEFF0;
        border: 2px solid #FF5252;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
        color: #FF5252;
        font-weight: 700;
    }

</style>
""", unsafe_allow_submit=True)

# --- CONFIGURACIÓN DE DATOS ---
PRECIOS = {
    "Prime video": 50, "HBO": 70, "Netflix": 70, "Disney": 50, 
    "Vix": 30, "Combo 1": 85, "Combo 2": 100, "Combo 3": 110, "Combo 4": 115
}

# --- TÍTULO PRINCIPAL (Como el de image_8.png) ---
st.markdown("<h1>GESTOR DE PAGOS</h1>", unsafe_allow_submit=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_existente = conn.read(ttl=0)
    df_existente = df_existente.dropna(how="all")
except Exception:
    df_existente = pd.DataFrame(columns=["Nombre", "Telefono", "Plataformas", "Total", "Dia"])

# --- SECCIÓN DE REGISTRO ---
st.markdown("<h3>Nuevo Cliente</h3>", unsafe_allow_submit=True)

# Contenedor principal de la interfaz
with st.form("nuevo_cliente", clear_on_submit=True):
    # Campos de texto (Inspirado en los de image_8.png)
    nombre = st.text_input("Nombre Completo")
    telefono = st.text_input("Número de WhatsApp (con código de país, ej: +52...)", help="Para enviar mensajes de cobro automático.")

    # Título para la selección de plataformas
    st.markdown("<h3>Servicios</h3>", unsafe_allow_submit=True)

    # Contenedor de las "tarjetas" de plataformas
    platforms_html = ""
    plataformas_elegidas = []
    
    # Creamos las tarjetas
    cols = st.columns(3)
    p_keys = list(PRECIOS.keys())
    for i, p in enumerate(p_keys):
        col = cols
        with col:
            # Creamos un checkbox con estilo CSS de tarjeta
            checked = st.checkbox(p, key=f"ch_{p}")
            if checked:
                plataformas_elegidas.append(p)
            
            # HTML para la visualización de la tarjeta (imitando image_8.png)
            platforms_html = f"""
            <div class="platform-card" style="border-color: {'#004DFF' if checked else '#D0D9FF'};">
                <div class="platform-name">{p.upper()}</div>
                <div class="platform-price">${PRECIOS}</div>
            </div>
            """
            st.markdown(platforms_html, unsafe_allow_submit=True)

    st.markdown("<br>", unsafe_allow_submit=True)
    
    # Resto de los campos de registro
    dia_pago = st.number_input("Día de corte (1-31)", min_value=1, max_value=31, value=datetime.now().day, help="Día en que vence el pago de este cliente.")
    boton_guardar = st.form_submit_button("AÑADIR CLIENTE", type="primary")

    if boton_guardar:
        if nombre and telefono and plataformas_elegidas:
            # Aseguramos el formato correcto del teléfono
            if not telefono.startswith('+'):
                telefono = '+' + telefono

            total = sum(PRECIOS for p in plataformas_elegidas)
            nueva_fila = pd.DataFrame([{
                "Nombre": nombre.upper(),
                "Telefono": telefono,
                "Plataformas": ", ".join(plataformas_elegidas),
                "Total": total,
                "Dia": int(dia_pago)
            }])
            
            df_final = pd.concat(, ignore_index=True)
            conn.update(data=df_final)
            st.success(f"¡Cliente **{nombre.upper()}** añadido correctamente!")
            st.rerun()

# --- ALERTAS DEL DÍA ---
hoy = datetime.now().day
st.markdown(f"<h2>Alertas de hoy (Día {hoy})</h2>", unsafe_allow_submit=True)

if not df_existente.empty and 'Dia' in df_existente.columns:
    df_existente['Dia'] = pd.to_numeric(df_existente['Dia'], errors='coerce')
    deudores = df_existente == hoy]
    
    if not deudores.empty:
        for _, fila in deudores.iterrows():
            # Mensaje de WhatsApp
            nombre_c = fila['Nombre']
            plataformas_c = fila['Plataformas']
            total_c = fila['Total']
            telefono_c = fila['Telefono']

            mensaje = f"Hola *{nombre_c}* 👋, recordatorio de tu pago de hoy del servicio *{plataformas_c}* por un total de *${total_c}*. Gracias."
            mensaje_urled = urllib.parse.quote(mensaje)
            link_whatsapp = f"https://wa.me/{telefono_c}?text={mensaje_urled}"
            
            # HTML para la alerta
            st.markdown(f"""
            <div class="payment-alert">
                PAGO DE HOY: <b>{nombre_c}</b> (${total_c})<br>
                <a href="{link_whatsapp}" target="_blank" style="color: #FF5252; text-decoration: underline;">Enviar mensaje de cobro</a>
            </div>
            """, unsafe_allow_submit=True)
    else:
        st.info("Sin pagos para hoy")

# --- LISTA COMPLETA DE CLIENTES ---
if not df_existente.empty:
    st.divider()
    st.markdown("<h2>Clientes Registrados</h2>", unsafe_allow_submit=True)
    
    for i, fila in df_existente.iterrows():
        # Uso de .get() para mayor seguridad
        nombre_c = fila.get('Nombre', 'S/N').upper()
        dia_c = fila.get('Dia', '0')
        plataformas_c = fila.get('Plataformas', 'N/A')
        total_c = fila.get('Total', 0)
        
        # HTML para la caja del cliente
        st.markdown(f"""
        <div class="client-box">
            <b>{nombre_c}</b><br>
            Día de corte: {dia_c}<br>
            Servicios: {plataformas_c}<br>
            Total: <b>${total_c}</b>
        </div>
        """, unsafe_allow_submit=True)
        
        # Botón para eliminar cliente
        with st.expander("Opciones de Cliente"):
            if st.button("Eliminar Cliente", key=f"del_{i}"):
                df_final = df_existente.drop(i)
                conn.update(data=df_final)
                st.success(f"¡Cliente **{nombre_c}** eliminado!")
                st.rerun()
