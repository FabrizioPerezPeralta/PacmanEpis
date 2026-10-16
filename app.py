"""
SYS-ENGINEER ARCADE 198X - PAC-MAN CYBER EDITION
Arquitectura MVC para despliegue web con Streamlit.
Misión Ciberseguridad & Redes TCP/IP.
"""

import streamlit as st
from controllers.game_controller import GameController

# 1. Configuración de la Página
st.set_page_config(
    page_title="SYS-ENGINEER ARCADE 198X // Cyber Packet",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inyección de Estilos Globales Retro-Cibernéticos para Streamlit
st.markdown(
    """
    <style>
        /* Tipografías y Colores Base */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&display=swap');

        .stApp {
            background-color: #060913;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(0, 240, 255, 0.07), transparent 70%),
                linear-gradient(180deg, #05070f 0%, #080c1b 100%);
            color: #e2e8f0;
            font-family: 'Share Tech Mono', monospace;
        }

        /* Títulos y Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 1px;
        }

        /* Métricas */
        [data-testid="stMetricValue"] {
            font-family: 'Orbitron', sans-serif !important;
            color: #00f0ff !important;
            font-weight: 800 !important;
        }

        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 11px !important;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* Pestañas */
        button[data-baseweb="tab"] {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 12px !important;
            letter-spacing: 1px;
            color: #94a3b8 !important;
            border-radius: 6px 6px 0 0;
            transition: all 0.2s ease;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00f0ff !important;
            border-bottom-color: #00f0ff !important;
            background: rgba(0, 240, 255, 0.08) !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #090e1f !important;
            border-right: 1px solid rgba(0, 240, 255, 0.15) !important;
        }

        /* Botones primarios */
        .stButton>button {
            border: 1px solid #00f0ff !important;
            background: rgba(0, 240, 255, 0.12) !important;
            color: #00f0ff !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 11px !important;
            letter-spacing: 1px !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }

        .stButton>button:hover {
            background: #00f0ff !important;
            color: #05070f !important;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
        }

        /* Tablas */
        table {
            border-collapse: collapse !important;
            width: 100% !important;
            border: 1px solid rgba(0, 240, 255, 0.2) !important;
        }
        th {
            background: rgba(0, 240, 255, 0.15) !important;
            color: #00f0ff !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 11px !important;
            padding: 8px !important;
        }
        td {
            padding: 8px !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
            color: #e2e8f0 !important;
            font-size: 12px !important;
        }

        /* Scrollbars futuristas */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #05070f;
        }
        ::-webkit-scrollbar-thumb {
            background: #1b2640;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00f0ff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Instanciación y ejecución del Controlador MVC
    controller = GameController()
    controller.run()


if __name__ == "__main__":
    main()
