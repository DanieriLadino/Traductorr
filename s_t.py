import os
import time
import glob
import hashlib

import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from googletrans import Translator

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Traductor por voz", page_icon="🎙️", layout="centered")

IMAGEN_URL = (
    "https://cdn0.expertoanimal.com/es/posts/4/5/7/"
    "los_5_perros_mas_inteligentes_del_mundo_4754_orig.jpg"
)

IDIOMAS = {
    "🇪🇸 Español": "es",
    "🇬🇧 Inglés": "en",
    "🇧🇩 Bengalí": "bn",
    "🇰🇷 Coreano": "ko",
    "🇨🇳 Mandarín": "zh-cn",
    "🇯🇵 Japonés": "ja",
}

ACENTOS = {
    "Por defecto": "com",
    "México": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 55%, #312e81 100%);
        color: #e2e8f0;
    }

    .hero {
        text-align: center;
        padding: 1.5rem 1rem 0.5rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #f472b6, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p { color: #cbd5e1; font-size: 1.05rem; margin-top: .3rem; }

    .card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        margin: 1rem 0;
        backdrop-filter: blur(6px);
    }
    .card h3 { margin-top: 0; color: #f8fafc; }

    .texto-voz {
        font-size: 1.2rem;
        font-style: italic;
        color: #fde68a;
    }

    [data-testid="stImage"] img {
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
    }

    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 12px;
        padding: .7rem 1rem;
        font-weight: 600;
        color: white;
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, .45);
        color: white;
    }

    label, .stCheckbox span { color: #e2e8f0 !important; }

    section[data-testid="stSidebar"] {
        background: #0b1020;
        border-right: 1px solid rgba(255,255,255,.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎙️ Cómo usarlo")
    st.markdown(
        """
        1. Pulsa **Escuchar** y habla cuando el navegador lo indique.  
        2. Elige el idioma de entrada y de salida.  
        3. Pulsa **Traducir** y escucha el resultado.
        """
    )
    st.info("El reconocimiento de voz funciona en Chrome o Edge.")

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>Traductor por voz</h1>
        <p>Habla, elige el idioma y escucha la traducción.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.image(IMAGEN_URL, use_container_width=True)

# ---------------------------------------------------------------------------
# Botón de reconocimiento de voz
# ---------------------------------------------------------------------------
st.markdown('<div class="card"><h3>1 · Habla</h3>', unsafe_allow_html=True)

stt_button = Button(label="🎤  Escuchar", width=300, height=50, button_type="primary")
stt_button.js_on_event(
    "button_click",
    CustomJS(
        code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'es-ES';

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        };
        recognition.start();
        """
    ),
)

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)
st.markdown("</div>", unsafe_allow_html=True)

if result and "GET_TEXT" in result:
    st.session_state["texto"] = result.get("GET_TEXT")

texto = st.session_state.get("texto")

# ---------------------------------------------------------------------------
# Traducción
# ---------------------------------------------------------------------------
def traducir_y_hablar(texto, origen, destino, tld):
    traductor = Translator()
    traduccion = traductor.translate(texto, src=origen, dest=destino).text
    os.makedirs("temp", exist_ok=True)
    nombre = hashlib.md5(f"{texto}{destino}{tld}".encode()).hexdigest()[:12]
    ruta = f"temp/{nombre}.mp3"
    gTTS(traduccion, lang=destino, tld=tld, slow=False).save(ruta)
    return ruta, traduccion


def limpiar_audios(dias=7):
    limite = time.time() - dias * 86400
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < limite:
            os.remove(f)


if texto:
    st.markdown(
        f'<div class="card"><h3>Lo que dijiste</h3>'
        f'<p class="texto-voz">“{texto}”</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 2 · Configura la traducción")
    col1, col2 = st.columns(2)
    with col1:
        idioma_in = st.selectbox("Idioma de entrada", list(IDIOMAS), index=0)
    with col2:
        idioma_out = st.selectbox("Idioma de salida", list(IDIOMAS), index=1)

    col3, col4 = st.columns([2, 1])
    with col3:
        acento = st.selectbox("Acento", list(ACENTOS))
    with col4:
        st.write("")
        st.write("")
        mostrar_texto = st.checkbox("Mostrar texto", value=True)

    if st.button("✨ Traducir"):
        with st.spinner("Traduciendo y generando audio..."):
            try:
                ruta, traduccion = traducir_y_hablar(
                    texto, IDIOMAS[idioma_in], IDIOMAS[idioma_out], ACENTOS[acento]
                )
            except Exception as e:
                st.error(f"No se pudo traducir: {e}")
            else:
                st.markdown('<div class="card"><h3>3 · Tu audio</h3>', unsafe_allow_html=True)
                with open(ruta, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                if mostrar_texto:
                    st.markdown(f'<p class="texto-voz">{traduccion}</p>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    limpiar_audios(7)
else:
    st.caption("Pulsa el botón y di algo para empezar.")
