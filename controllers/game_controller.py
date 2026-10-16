"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
CONTROLLER: game_controller.py
Controlador central que orquesta el Modelo (GameModel, ThreatModel) y las Vistas (ArcadeView, DashboardView).
"""

import streamlit as st
from models.game_model import GameModel
from models.threat_model import ThreatModel
from views.arcade_view import ArcadeView
from views.dashboard_view import DashboardView


class GameController:
    """Controlador que gestiona la lógica de aplicación, estado de sesión y sincronización MVC."""

    def __init__(self):
        self.game_model = GameModel()
        self.threat_model = ThreatModel()
        self.arcade_view = ArcadeView()
        self.dashboard_view = DashboardView()
        self._initialize_session()

    def _initialize_session(self):
        """Inicializa variables en el SessionState de Streamlit si no existen."""
        if "player_name" not in st.session_state:
            st.session_state["player_name"] = "DEV_SECOPS"
        if "difficulty" not in st.session_state:
            st.session_state["difficulty"] = "normal"
        if "credits" not in st.session_state:
            st.session_state["credits"] = 5
        if "audio_enabled" not in st.session_state:
            st.session_state["audio_enabled"] = True

    def insert_credit(self):
        """Aumenta las fichas / créditos disponibles."""
        st.session_state["credits"] += 1
        st.toast("🪙 ¡Crédito insertado! Buffer de vidas recargado.", icon="🕹️")

    def set_difficulty(self, difficulty_key: str):
        """Actualiza el nivel de dificultad en la sesión."""
        st.session_state["difficulty"] = difficulty_key

    def submit_score(self, score: int, player_name: str, level: str = "Nivel 1"):
        """Registra un nuevo puntaje en el modelo persistente."""
        if score > 0:
            is_record = self.game_model.save_score(score, player_name, level)
            if is_record:
                st.balloons()
                st.success(f"🎉 ¡NUEVO RÉCORD DE RED! {player_name} alcanzó {score:,} Bytes ({level}).")
            else:
                st.info(f"✅ Puntaje de {score:,} Bytes ({level}) registrado para {player_name}.")

    def render_sidebar(self):
        """Construye los controles interactivos de la barra lateral."""
        with st.sidebar:
            st.markdown(
                """
                <div style="text-align: center; padding: 10px 0; border-bottom: 1px solid rgba(0,240,255,0.2);">
                    <h2 style="color: #00f0ff; margin: 0; font-size: 20px;">🕹️ CABINA DE CONTROL</h2>
                    <span style="font-size: 11px; color: #94a3b8;">SISTEMA OPERATIVO ARCADE v2.5</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")
            # Identificador del Operador (Puesto arriba de todo)
            player = st.text_input(
                "👤 Tag de Operador / Usuario",
                value=st.session_state["player_name"],
                max_chars=12,
                help="Tu alias de red que aparecerá en el Top 5."
            )
            if player:
                st.session_state["player_name"] = player.strip().upper()

            st.divider()

            # Ranura de Monedas / Créditos
            col_cred1, col_cred2 = st.columns([2, 1])
            with col_cred1:
                st.metric(label="Créditos Restantes", value=f"{st.session_state['credits']} Fichas")
            with col_cred2:
                st.write("")
                if st.button("🪙 INSERT", use_container_width=True, help="Insertar moneda virtual"):
                    self.insert_credit()

            st.divider()

            # Selector de Perfil de Seguridad (Dificultad)
            presets = self.game_model.get_difficulty_presets()
            diff_options = list(presets.keys())
            diff_names = [presets[k]["name"] for k in diff_options]
            current_index = diff_options.index(st.session_state["difficulty"])

            selected_name = st.selectbox(
                "⚙️ Perfil de SecOps (Dificultad)",
                options=diff_names,
                index=current_index,
                help="Ajusta la velocidad base y agresividad de los virus cazadores."
            )
            # Actualizar estado si cambió
            for k, val in presets.items():
                if val["name"] == selected_name:
                    self.set_difficulty(k)
                    st.caption(f"ℹ️ {val['description']}")
                    break

            st.divider()

            # Formulario manual para certificar puntaje
            with st.expander("📝 Certificar Puntaje Manual", expanded=False):
                manual_score = st.number_input("Bytes Logrados", min_value=0, max_value=999999, step=100)
                manual_level = st.selectbox("Nivel Superado", [f"Nivel {i}" for i in range(1, 101)], index=0)
                if st.button("Guardar en Leaderboard", use_container_width=True):
                    self.submit_score(manual_score, st.session_state["player_name"], manual_level)
                    st.rerun()

            st.divider()

            # Guía Rápida de Teclas
            st.markdown(
                """
                <div style="font-size: 11px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 10px;">
                    <strong style="color: #00f0ff;">🎮 GUÍA DE CONTROLES:</strong><br>
                    • <strong>Flechas / WASD:</strong> Mover Paquete<br>
                    • <strong>ESPACIO / Z / K:</strong> Disparo Sniper 🎯<br>
                    • <strong>P:</strong> Pausar / Reanudar ⏸️<br>
                    • <strong>R:</strong> Reiniciar Nivel 🔄<br>
                    • <strong>Táctil:</strong> Usa la cruceta D-Pad y botones inferiores.
                </div>
                """,
                unsafe_allow_html=True
            )

    def run(self):
        """Punto de ejecución principal que coordina vistas y modelos."""
        # 1. Barra lateral de control
        self.render_sidebar()

        # 2. Encabezado principal
        self.dashboard_view.render_header()

        # 3. Métricas clave superiores
        presets = self.game_model.get_difficulty_presets()
        active_preset = presets.get(st.session_state["difficulty"], presets["normal"])
        high_score = self.game_model.get_high_score()
        top_player = self.game_model.get_top_player()

        self.dashboard_view.render_metrics(
            high_score=high_score,
            top_player=top_player,
            difficulty_name=active_preset["name"],
            credits=st.session_state["credits"]
        )

        st.write("")

        # 4. Organización por Pestañas Profesionales
        tab_arcade, tab_intel, tab_leaderboard = st.tabs([
            "🕹️ PANTALLA ARCADE (CYBER PACKET)",
            "🛡️ MATRIZ DE CIBERDEFENSA",
            "🏆 SALÓN DE LA FAMA & VOCACIÓN"
        ])

        with tab_arcade:
            # Layout con TOP 5 a la izquierda y Gabinete Arcade a la derecha
            col_top5, col_arcade = st.columns([1.1, 2.3], gap="medium")

            with col_top5:
                top_5 = self.game_model.get_top_5()
                self.dashboard_view.render_top_5_side_card(
                    top_5=top_5,
                    current_player=st.session_state["player_name"],
                    current_diff=active_preset["name"]
                )

            with col_arcade:
                # Renderizar Gabinete Arcade interactivo con autenticación previa
                self.arcade_view.render(
                    initial_high_score=high_score,
                    top_player=top_player,
                    player_name=st.session_state["player_name"],
                    difficulty_speed=active_preset["speed_mult"],
                    top_5=self.game_model.get_top_5(),
                    height=860
                )

        with tab_intel:
            # Matriz de Ciberamenazas y Arsenal de Tokens
            threats = self.threat_model.get_all_threats()
            self.dashboard_view.render_threat_matrix(threats)

            st.write("")
            tokens = self.threat_model.get_firewall_tokens()
            self.dashboard_view.render_defense_tokens(tokens)

        with tab_leaderboard:
            # Leaderboard y Píldora vocacional
            col_lead, col_info = st.columns([3, 2])
            with col_lead:
                leaderboard = self.game_model.get_leaderboard()
                self.dashboard_view.render_leaderboard(leaderboard)
            with col_info:
                tips = self.game_model.get_vocational_tips()
                self.dashboard_view.render_vocational_banner(tips)

                st.markdown(
                    """
                    <div style="margin-top: 15px; padding: 12px; background: rgba(13, 20, 43, 0.6); border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.15);">
                        <h4 style="color: #00f0ff; margin-top: 0; font-size: 13px;">🌐 ¿Cómo se conecta con Ingeniería de Sistemas?</h4>
                        <ul style="font-size: 11px; color: #cbd5e1; padding-left: 16px; margin-bottom: 0;">
                            <li><strong>Redes y Enrutamiento:</strong> Algoritmos Dijkstra y enrutamiento dinámico para paquetes TCP/IP.</li>
                            <li><strong>Ciberseguridad Ofensiva/Defensiva:</strong> Análisis de firmas, detección heurística y arquitecturas Zero Trust.</li>
                            <li><strong>Patrones de Software:</strong> Arquitectura MVC, Template Method, Singleton y EventBus implementados en este mismo proyecto.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
