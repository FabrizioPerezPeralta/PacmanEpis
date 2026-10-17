"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
VIEW: dashboard_view.py
Capa de Presentación para el Dashboard de Ciberseguridad, Métricas e Información Vocacional en Streamlit.
"""

import streamlit as st
from typing import List, Dict, Any
from models.threat_model import CyberThreat, FirewallToken


class DashboardView:
    """Renderiza paneles de control, enciclopedia de amenazas y telemetría de red en Streamlit."""

    @staticmethod
    def render_header():
        st.markdown(
            """
            <div style="margin-bottom: 6px; padding: 6px 14px; background: linear-gradient(90deg, rgba(0,240,255,0.06) 0%, rgba(255,0,119,0.06) 100%); border: 1px solid rgba(0,240,255,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">🕹️</span>
                    <span style="font-size: 15px; font-weight: 900; letter-spacing: 1.5px; background: linear-gradient(90deg, #00f0ff, #ffffff, #ff0077); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        SYS-ENGINEER ARCADE 198X // CYBER PACKET
                    </span>
                </div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1px;">
                    SUBRED TCP/IP • MISIÓN CIBERDEFENSA
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_metrics(high_score: int, top_player: str, difficulty_name: str, credits: int):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="🏆 Récord de Red (Bytes)", value=f"{high_score:,}")
        with col2:
            st.metric(label="👤 Operador Líder", value=top_player)
        with col3:
            st.metric(label="⚙️ Perfil SecOps", value=difficulty_name)
        with col4:
            st.metric(label="🪙 Créditos en Buffer", value=f"{credits} Fichas")

    @staticmethod
    def render_threat_matrix(threats: List[CyberThreat]):
        st.markdown("### 🚨 Matriz de Ciberamenazas (Algoritmos de Caza)")
        st.caption("Cada virus en el laberinto replica un comportamiento ofensivo real estudiado en Seguridad Informática:")

        cols = st.columns(len(threats))
        for i, threat in enumerate(threats):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background: rgba(13, 20, 43, 0.8); border: 1px solid {threat.color_hex}; border-radius: 8px; padding: 12px; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                        <div style="font-size: 24px; text-align: center; margin-bottom: 6px;">{threat.icon}</div>
                        <div style="color: {threat.color_hex}; font-weight: 800; font-size: 13px; text-align: center; margin-bottom: 6px;">
                            {threat.name}
                        </div>
                        <div style="font-size: 11px; color: #e2e8f0; margin-bottom: 6px;">
                            <strong>IA:</strong> {threat.ai_strategy}
                        </div>
                        <div style="font-size: 10px; color: #94a3b8; margin-bottom: 6px;">
                            <strong>Impacto:</strong> {threat.real_world_impact}
                        </div>
                        <div style="font-size: 10px; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 4px; border-radius: 4px;">
                            <strong>Defensa:</strong> {threat.defense_advice}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    @staticmethod
    def render_defense_tokens(tokens: List[FirewallToken]):
        st.markdown("### 🛡️ Arsenal de Firewall (Superpellets de Mitigación)")
        st.caption("Consigue tokens en las esquinas de la subred para neutralizar vectores de ataque:")

        cols = st.columns(len(tokens))
        for i, tok in enumerate(tokens):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 12px; height: 100%;">
                        <div style="font-size: 22px; text-align: center; margin-bottom: 4px;">{tok.icon}</div>
                        <div style="color: #00f0ff; font-weight: bold; font-size: 12px; text-align: center; margin-bottom: 4px;">
                            {tok.name}
                        </div>
                        <div style="font-size: 11px; color: #cbd5e1; margin-bottom: 6px;">
                            {tok.effect}
                        </div>
                        <div style="font-size: 10px; color: #fde047; font-style: italic;">
                            💡 {tok.tactical_tip}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    @staticmethod
    def render_vocational_banner(tips: List[str]):
        import random
        tip = random.choice(tips) if tips else "La Ingeniería de Sistemas protege el mundo interconectado."
        st.markdown(
            f"""
            <div style="margin-top: 15px; padding: 14px 18px; background: linear-gradient(90deg, rgba(168, 85, 247, 0.15) 0%, rgba(0, 240, 255, 0.15) 100%); border-left: 4px solid #a855f7; border-radius: 8px;">
                <div style="font-size: 11px; text-transform: uppercase; font-weight: bold; color: #d8b4fe; letter-spacing: 1px; margin-bottom: 4px;">
                    🎓 Vocación Tecnológica // ¿Por qué estudiar Ingeniería de Sistemas?
                </div>
                <div style="font-size: 13px; color: #f1f5f9; line-height: 1.5;">
                    {tip}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_top_5_side_card(top_5: List[Dict[str, Any]], current_player: str, current_diff: str):
        """Renderiza la tarjeta lateral izquierda con el TOP 5 de operadores destacados y su nivel alcanzado."""
        st.markdown(
            """
            <div style="background: linear-gradient(180deg, #0e1428 0%, #080c1a 100%); border: 2px solid #00f0ff; border-radius: 10px; padding: 12px; box-shadow: 0 0 15px rgba(0, 240, 255, 0.18);">
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(0, 240, 255, 0.25); padding-bottom: 6px; margin-bottom: 8px;">
                    <div>
                        <h3 style="margin: 0; color: #00f0ff; font-size: 13px; font-weight: 800; letter-spacing: 1px;">
                            🏆 TOP 5 DE USUARIOS
                        </h3>
                        <span style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">
                            Mejores Puntuaciones
                        </span>
                    </div>
                    <span style="background: rgba(0,240,255,0.15); border: 1px solid #00f0ff; color: #00f0ff; padding: 1px 6px; border-radius: 10px; font-size: 8px; font-weight: bold;">
                        EN VIVO
                    </span>
                </div>
            """,
            unsafe_allow_html=True
        )

        if not top_5:
            st.markdown(
                """
                <div style="text-align: center; padding: 25px 10px; color: #64748b; font-size: 11px;">
                    <div style="font-size: 24px; margin-bottom: 6px;">🕹️</div>
                    <strong style="color: #00f0ff; letter-spacing: 1px;">TABLA LIMPIA</strong><br>
                    <span style="font-size: 10px; color: #94a3b8;">¡Sé el primer operador en establecer un récord!</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            rank_badges = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
            colors = ["#ffe600", "#e2e8f0", "#f97316", "#38bdf8", "#a855f7"]
            for idx, entry in enumerate(top_5[:5]):
                badge = rank_badges[idx] if idx < len(rank_badges) else f"#{idx+1}"
                color = colors[idx] if idx < len(colors) else "#cbd5e1"
                p_name = entry.get("player", f"OPERADOR_{idx+1}")
                p_score = entry.get("score", 0)
                p_lvl = entry.get("level", f"Nivel {8 - idx}")

                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid {color}44; border-left: 3px solid {color}; border-radius: 5px; padding: 5px 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 15px;">{badge}</span>
                            <div>
                                <div style="color: {color}; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;">
                                    {p_name}
                                </div>
                                <div style="font-size: 9px; color: #64748b;">
                                    {p_lvl}
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #00f0ff; font-weight: 800; font-size: 11px;">
                                {p_score:,}
                            </div>
                            <div style="font-size: 8px; color: #64748b;">
                                BYTES
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Estado del Operador Conectado
        st.markdown(
            f"""
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                        <span style="color: #94a3b8;">👤 Operador:</span>
                        <strong style="color: #ffe600;">{current_player}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                        <span style="color: #94a3b8;">⚙️ Dificultad:</span>
                        <strong style="color: #38bdf8;">{current_diff}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">🌐 Estado:</span>
                        <strong style="color: #00ff88;">🟢 CONECTADO</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_leaderboard(leaderboard: List[Dict[str, Any]]):
        st.markdown("### 🏅 Salón de la Fama (Operadores Destacados)")
        if not leaderboard:
            st.info("Aún no hay partidas registradas en el servidor. ¡Sé el primero en establecer un récord!")
            return

        table_data = []
        for rank, entry in enumerate(leaderboard, start=1):
            badge = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            table_data.append({
                "Rango": badge,
                "Operador": entry.get("player", "ANON_USER"),
                "Bytes Salvados": f"{entry.get('score', 0):,}",
                "Nivel": entry.get("level", "Nivel 1")
            })
        st.table(table_data)
