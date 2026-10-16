"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
MODEL: game_model.py
Modelo de estado del juego, persistencia de récords, configuración y métricas.
"""

import os
import json
from typing import Dict, Any, List

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
    """Modelo de datos centralizado para el estado, récords y configuración."""

    def __init__(self):
        self.highscores_path = HIGHSCORES_FILE
        self.scores_data = self._load_scores()

    def _load_scores(self) -> Dict[str, Any]:
        default = {
            "high_score": 14800,
            "top_player": "KEVIN_M",
            "history": [
                {"player": "KEVIN_M", "score": 14800, "level": "Nivel 8"},
                {"player": "ALAN_T", "score": 12200, "level": "Nivel 7"},
                {"player": "ADA_L", "score": 10450, "level": "Nivel 5"},
                {"player": "LINUS_T", "score": 8900, "level": "Nivel 4"},
                {"player": "GRACE_H", "score": 7200, "level": "Nivel 3"}
            ]
        }
        if os.path.exists(self.highscores_path):
            try:
                with open(self.highscores_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("history"):
                        default.update(data)
                    else:
                        default["high_score"] = data.get("high_score", default["high_score"])
                        default["top_player"] = data.get("top_player", default["top_player"])
            except Exception:
                pass
        return default

    def save_score(self, score: int, player_name: str = "DEV_JUNIOR", level: str = "Nivel 1") -> bool:
        """Guarda un puntaje si supera o se ubica en el récord histórico."""
        is_new_record = False
        if score > self.scores_data.get("high_score", 0):
            self.scores_data["high_score"] = score
            self.scores_data["top_player"] = player_name
            is_new_record = True

        # Agregar al historial de partidas (máximo 10)
        history = self.scores_data.setdefault("history", [])
        history.append({"player": player_name, "score": score, "level": level})
        history.sort(key=lambda x: x["score"], reverse=True)
        self.scores_data["history"] = history[:10]

        try:
            with open(self.highscores_path, "w", encoding="utf-8") as f:
                json.dump(self.scores_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return is_new_record

    def get_high_score(self) -> int:
        self.scores_data = self._load_scores()
        return self.scores_data.get("high_score", 14800)

    def get_top_player(self) -> str:
        self.scores_data = self._load_scores()
        return self.scores_data.get("top_player", "KEVIN_M")

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        self.scores_data = self._load_scores()
        return self.scores_data.get("history", [])

    def get_top_5(self) -> List[Dict[str, Any]]:
        """Retorna exclusivamente los mejores 5 operadores (frescos de disco)."""
        self.scores_data = self._load_scores()
        history = self.scores_data.get("history", [])
        return history[:5]

    @staticmethod
    def get_difficulty_presets() -> Dict[str, Any]:
        return DIFFICULTY_PRESETS

    @staticmethod
    def get_vocational_tips() -> List[str]:
        return VOCATIONAL_TIPS
