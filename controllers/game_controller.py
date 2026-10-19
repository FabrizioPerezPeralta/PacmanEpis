"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
CONTROLLER: game_controller.py
Controlador central que orquesta el Modelo (GameModel, ThreatModel) y las Vistas (ArcadeView, DashboardView).
"""

import streamlit as st
from models.game_model import GameModel
from models.threat_model import ThreatModel
from models.api_server import start_background_api
from views.arcade_view import ArcadeView
from views.dashboard_view import DashboardView


from models.supabase_client import get_supabase_status


class GameController:
    """Controlador que gestiona la lógica de aplicación, estado de sesión y sincronización MVC."""

    def __init__(self):
        # Iniciar servidor API ligero en segundo plano para sincronización multijugador
        start_background_api(port=8502)

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
            diff = st.session_state.get("difficulty", "normal")
            is_record = self.game_model.save_score(score, player_name, level, difficulty=diff)
            if is_record:
                st.balloons()
                st.success(f"🎉 ¡NUEVO RÉCORD DE RED! {player_name} alcanzó {score:,} Bytes ({level}).")
            else:
                st.info(f"✅ Puntaje de {score:,} Bytes ({level}) registrado para {player_name}.")

    def render_top_bar(self, presets, active_preset):
        """Barra de comando superior horizontal que sustituye la barra lateral para maximizar el campo visual."""
        sb_status = get_supabase_status()

        c_brand, c_status, c_player, c_diff, c_coins, c_help = st.columns(
            [2.4, 1.3, 1.4, 1.6, 1.4, 0.7], gap="small"
        )

        with c_brand:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; padding-top: 2px;">
                    <span style="font-size: 22px; filter: drop-shadow(0 0 8px #00f0ff);">🕹️</span>
                    <div>
                        <div style="font-size: 14px; font-weight: 900; letter-spacing: 1.2px; background: linear-gradient(90deg, #00f0ff, #fff, #ff0077); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;">
                            CYBER PACKET // 198X
                        </div>
                        <div style="font-size: 8px; color: #64748b; letter-spacing: 0.8px;">
                            SUBRED TCP/IP • MISIÓN CIBERDEFENSA
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c_status:
            if sb_status["connected"]:
                st.markdown(
                    """
                    <div style="margin-top: 4px; font-size: 9px; color: #00ff88; text-align: center; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.35); border-radius: 6px; padding: 5px 6px; font-weight: bold; letter-spacing: 0.5px;">
                        ☁️ SUPABASE CLOUD 🟢
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="margin-top: 4px; font-size: 9px; color: #fde047; text-align: center; background: rgba(253, 224, 71, 0.08); border: 1px solid rgba(253, 224, 71, 0.35); border-radius: 6px; padding: 5px 6px; font-weight: bold; letter-spacing: 0.5px;">
                        💾 MODO LOCAL (JSON) 🟡
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with c_player:
            player = st.text_input(
                "Operador",
                value=st.session_state["player_name"],
                max_chars=12,
                label_visibility="collapsed",
                placeholder="TAG OPERADOR"
            )
            if player:
                st.session_state["player_name"] = player.strip().upper()

        with c_diff:
            diff_options = list(presets.keys())
            diff_names = [presets[k]["name"] for k in diff_options]
            current_index = diff_options.index(st.session_state["difficulty"])
            selected_name = st.selectbox(
                "Dificultad",
                options=diff_names,
                index=current_index,
                label_visibility="collapsed"
            )
            for k, val in presets.items():
                if val["name"] == selected_name:
                    self.set_difficulty(k)
                    break

        with c_coins:
            col_fichas, col_btn = st.columns([1, 1], gap="small")
            with col_fichas:
                st.markdown(
                    f"""
                    <div style="margin-top: 2px; text-align: center; background: rgba(255, 230, 0, 0.06); border: 1px solid rgba(255, 230, 0, 0.3); border-radius: 6px; padding: 3px 4px;">
                        <div style="font-size: 7px; color: #94a3b8; text-transform: uppercase;">FICHAS</div>
                        <div style="font-size: 13px; font-weight: 900; color: #ffe600; text-shadow: 0 0 6px rgba(255,230,0,0.5);">{st.session_state['credits']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_btn:
                if st.button("🪙 +1", use_container_width=True, help="Insertar moneda virtual"):
                    self.insert_credit()
                    st.rerun()

        with c_help:
            with st.popover("🎮 Guía", use_container_width=True):
                st.markdown(
                    """
                    <div style="font-size: 11px; color: #cbd5e1; line-height: 1.5;">
                        <strong style="color: #00f0ff;">🎮 GUÍA DE CONTROLES:</strong><br>
                        • <strong>Flechas / WASD:</strong> Mover Paquete<br>
                        • <strong>ESPACIO / Z / K:</strong> Disparo Sniper 🎯<br>
                        • <strong>P:</strong> Pausar / Reanudar ⏸️<br>
                        • <strong>R:</strong> Reiniciar Nivel 🔄<br>
                        • <strong>Táctil / Ratón:</strong> Cruceta D-Pad y botones virtuales.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    @st.fragment(run_every="2s")
    def render_live_top_5_fragment(self, active_preset_name: str):
        """Renderiza la tarjeta del Top 5 con auto-actualización reactiva en tiempo real cada 2 segundos."""
        top_5 = self.game_model.get_top_5()
        self.dashboard_view.render_top_5_side_card(
            top_5=top_5,
            current_player=st.session_state["player_name"],
            current_diff=active_preset_name
        )

    def run(self):
        """Punto de ejecución principal que coordina vistas y modelos."""
        # Verificar si hay puntajes entrantes por parámetros de URL
        if "s" in st.query_params and "p" in st.query_params:
            try:
                p = st.query_params["p"]
                s = int(st.query_params["s"])
                l = st.query_params.get("l", "Nivel 1")
                self.submit_score(s, p, l)
                del st.query_params["s"]
                if "p" in st.query_params: del st.query_params["p"]
                if "l" in st.query_params: del st.query_params["l"]
            except Exception:
                pass

        # 1. Parámetros de juego
        presets = self.game_model.get_difficulty_presets()
        active_preset = presets.get(st.session_state["difficulty"], presets["normal"])
        high_score = self.game_model.get_high_score()
        top_player = self.game_model.get_top_player()

        # 2. Barra de comando superior (Sustituye la barra lateral)
        self.render_top_bar(presets, active_preset)

        # 3. Vista Principal Expandida: Consola Arcade con máximo campo visual
        col_side, col_arcade = st.columns([1, 2.5], gap="large")

        with col_side:
            # Ranking Top 5 en vivo (Auto-actualizable cada 2s)
            self.render_live_top_5_fragment(active_preset["name"])

            # Pestañas de telemetría y ayuda
            tab_threats, tab_score, tab_voc = st.tabs(["🚨 Amenazas", "📝 Certificar", "🎓 Vocación"])
            with tab_threats:
                st.markdown(
                    """
                    <div style="font-size: 10px; color: #94a3b8; line-height: 1.5; padding: 4px 0;">
                        <strong style="color: #ff0055;">• Blinky (Ransomware):</strong> Persecución directa.<br>
                        <strong style="color: #ff99cc;">• Pinky (Phishing):</strong> Emboscada anticipada.<br>
                        <strong style="color: #00f0ff;">• Inky (Spyware):</strong> Pinza coordinada.<br>
                        <strong style="color: #ff9900;">• Clyde (Trojan):</strong> Amague y engaño.<br>
                        <strong style="color: #bf00ff;">• Sue (Polimórfico):</strong> Intercepción diagonal.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with tab_score:
                manual_score = st.number_input("Bytes Logrados", min_value=0, max_value=999999, step=100)
                manual_level = st.selectbox("Nivel Superado", [f"Nivel {i}" for i in range(1, 101)], index=0)
                if st.button("Guardar en Leaderboard", use_container_width=True):
                    self.submit_score(manual_score, st.session_state["player_name"], manual_level)
                    st.rerun()
            with tab_voc:
                self.dashboard_view.render_vocational_banner(self.game_model.get_vocational_tips())

        with col_arcade:
            # Renderizar Gabinete Arcade interactivo con mayor campo visual (height=810)
            self.arcade_view.render(
                initial_high_score=high_score,
                top_player=top_player,
                player_name=st.session_state["player_name"],
                difficulty_speed=active_preset["speed_mult"],
                top_5=self.game_model.get_top_5(),
                height=685
            )
