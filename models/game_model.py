"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
MODEL: game_model.py
Modelo de estado del juego, persistencia híbrida (Supabase PostgreSQL + Fallback Local JSON) y métricas.
"""

import os
import json
from typing import Dict, Any, List, Optional
from models.supabase_client import get_supabase_client, is_supabase_connected

HIGHSCORES_FILE = "highscores.json"

DIFFICULTY_PRESETS = {
    "normal": {
        "name": "SecOps Standard",
        "speed_mult": 1.0,
        "antivirus_sec": 10,
        "description": "Equilibrio táctico estándar recomendado para estudiantes."
    },
    "novato": {
        "name": "Junior Developer",
        "speed_mult": 0.8,
        "antivirus_sec": 14,
        "description": "Velocidad reducida para aprender el enrutamiento de paquetes TCP/IP."
    },
    "hardcore": {
        "name": "Red Team Attack (Hardcore)",
        "speed_mult": 1.25,
        "antivirus_sec": 6,
        "description": "Amenazas hiperactivas con ramp-up acelerado para ingenieros senior."
    }
}

VOCATIONAL_TIPS: List[str] = [
    "🛡️ ¿Sabías que un Especialista en Ciberseguridad protege infraestructuras críticas como redes eléctricas, satélites y bancos?",
    "🌐 El protocolo TCP/IP garantiza que los paquetes de datos lleguen íntegros a través de múltiples routers usando checksums y ACKs.",
    "🔒 La criptografía de clave pública (RSA / Curvas Elípticas) es la base que protege las compras y contraseñas de todo el planeta.",
    "🚨 En el modelo 'Zero Trust' de ciberseguridad, nunca se confía en ningún dispositivo, incluso si está dentro de la red corporativa.",
    "💡 La Ingeniería de Sistemas combina Arquitectura de Software, Cloud Computing, Ciberdefensa e Inteligencia Artificial."
]


class GameModel:
    """Modelo de datos centralizado con persistencia en Supabase y respaldo local en JSON."""

    def __init__(self):
        self.highscores_path = HIGHSCORES_FILE
        self.scores_data = self._load_scores_local()

    # -------------------------------------------------------------------------
    # Persistencia Local (Fallback)
    # -------------------------------------------------------------------------
    def _load_scores_local(self) -> Dict[str, Any]:
        default = {
            "high_score": 0,
            "top_player": "DEV_SECOPS",
            "history": []
        }
        if os.path.exists(self.highscores_path):
            try:
                with open(self.highscores_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data.get("history"), list):
                        default["history"] = data["history"]
                        default["high_score"] = data.get("high_score", 0)
                        default["top_player"] = data.get("top_player", "DEV_SECOPS")
            except Exception:
                pass
        return default

    def _save_score_local(self, score: int, player_name: str, level: str) -> bool:
        """Guarda en JSON local de respaldo."""
        is_new_record = False
        if score > self.scores_data.get("high_score", 0):
            self.scores_data["high_score"] = score
            self.scores_data["top_player"] = player_name
            is_new_record = True

        history = self.scores_data.setdefault("history", [])
        history.append({"player": player_name, "score": score, "level": level})
        history.sort(key=lambda x: x["score"], reverse=True)
        self.scores_data["history"] = history[:15]

        try:
            with open(self.highscores_path, "w", encoding="utf-8") as f:
                json.dump(self.scores_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return is_new_record

    # -------------------------------------------------------------------------
    # Operaciones Híbridas (Supabase Cloud + Fallback Local)
    # -------------------------------------------------------------------------
    def save_score(self, score: int, player_name: str = "DEV_JUNIOR", level: str = "Nivel 1", difficulty: str = "normal") -> bool:
        """
        Registra un puntaje en la nube Supabase y en la caché local.
        Retorna True si representa un nuevo récord global.
        """
        player_clean = (player_name or "OPERADOR").strip().upper()[:20]
        is_new_record = False

        # 1. Intentar registrar en Supabase
        supabase = get_supabase_client()
        if supabase:
            try:
                # Usar la función RPC 'submit_score' para inserción atómica
                rpc_res = supabase.rpc("submit_score", {
                    "p_player_tag": player_clean,
                    "p_score": score,
                    "p_level": level,
                    "p_difficulty": difficulty
                }).execute()

                if rpc_res and rpc_res.data:
                    data = rpc_res.data
                    is_new_record = bool(data.get("is_new_global_record", False))
                else:
                    # Alternativa manual si el RPC no existiera
                    supabase.table("players").upsert({
                        "player_tag": player_clean,
                        "highest_score": score,
                        "highest_level": level
                    }, on_conflict="player_tag").execute()

                    supabase.table("scores").insert({
                        "player_tag": player_clean,
                        "score": score,
                        "level": level,
                        "difficulty": difficulty
                    }).execute()
            except Exception:
                # Falla silenciosa con fallback a local
                pass

        # 2. Respaldo en JSON local siempre
        local_record = self._save_score_local(score, player_clean, level)
        return is_new_record or local_record

    def get_high_score(self) -> int:
        """Obtiene el récord mundial más alto vigente."""
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("scores").select("score").order("score", desc=True).limit(1).execute()
                if res.data and len(res.data) > 0:
                    return int(res.data[0]["score"])
                return 0
            except Exception:
                pass

        self.scores_data = self._load_scores_local()
        return self.scores_data.get("high_score", 0)

    def get_top_player(self) -> str:
        """Obtiene el nombre del operador que ostenta el récord actual."""
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("scores").select("player_tag").order("score", desc=True).limit(1).execute()
                if res.data and len(res.data) > 0:
                    return str(res.data[0]["player_tag"])
                return "SIN RÉCORD"
            except Exception:
                pass

        self.scores_data = self._load_scores_local()
        return self.scores_data.get("top_player", "SIN RÉCORD")

    def get_top_5(self) -> List[Dict[str, Any]]:
        """Retorna exclusivamente los mejores 5 operadores (para HUD y tarjetas en vivo)."""
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("scores").select("player_tag, score, level").order("score", desc=True).order("created_at", desc=False).limit(5).execute()
                if res.data and len(res.data) > 0:
                    return [
                        {
                            "player": row.get("player_tag", "ANON"),
                            "score": int(row.get("score", 0)),
                            "level": row.get("level", "Nivel 1")
                        }
                        for row in res.data
                    ]
            except Exception:
                pass

        self.scores_data = self._load_scores_local()
        history = self.scores_data.get("history", [])
        return history[:5]

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Retorna el Salón de la Fama extendido (Top 20)."""
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("scores").select("player_tag, score, level, difficulty, created_at").order("score", desc=True).order("created_at", desc=False).limit(20).execute()
                if res.data and len(res.data) > 0:
                    return [
                        {
                            "player": row.get("player_tag", "ANON"),
                            "score": int(row.get("score", 0)),
                            "level": row.get("level", "Nivel 1"),
                            "difficulty": row.get("difficulty", "normal"),
                            "created_at": row.get("created_at", "")
                        }
                        for row in res.data
                    ]
            except Exception:
                pass

        self.scores_data = self._load_scores_local()
        return self.scores_data.get("history", [])

    @staticmethod
    def get_difficulty_presets() -> Dict[str, Any]:
        return DIFFICULTY_PRESETS

    @staticmethod
    def get_vocational_tips() -> List[str]:
        # Consultar tips desde Supabase si están disponibles
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("vocational_tips").select("tip_text").eq("is_active", True).execute()
                if res.data and len(res.data) > 0:
                    return [row["tip_text"] for row in res.data]
            except Exception:
                pass
        return VOCATIONAL_TIPS
