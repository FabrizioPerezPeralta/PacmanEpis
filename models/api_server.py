"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
MODEL: api_server.py
Servidor HTTP ligero para sincronización multijugador en tiempo real (CORS activado).
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from models.game_model import GameModel

_api_server_instance = None
_api_thread = None


class ScoreApiHandler(BaseHTTPRequestHandler):
    """Manejador REST para registro y consulta de récords multijugador."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", "application/json")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/top5"):
            model = GameModel()
            top_5 = model.get_top_5()
            high_score = model.get_high_score()
            top_player = model.get_top_player()

            response_data = {
                "success": True,
                "high_score": high_score,
                "top_player": top_player,
                "top_5": top_5
            }

            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith("/api/score"):
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)

            try:
                data = json.loads(post_body.decode("utf-8"))
                player = data.get("player", "ANON_OPERATOR")
                score = int(data.get("score", 0))
                level = data.get("level", "Nivel 1")

                model = GameModel()
                is_record = model.save_score(score, player, level)
                updated_top5 = model.get_top_5()

                response_data = {
                    "success": True,
                    "is_record": is_record,
                    "player": player,
                    "score": score,
                    "level": level,
                    "top_5": updated_top5
                }

                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs en consola para mantener el terminal limpio
        return


def start_background_api(port: int = 8502):
    """Inicia el servidor API en un hilo de fondo (daemon) si no está activo."""
    global _api_server_instance, _api_thread
    if _api_server_instance is not None:
        return _api_server_instance

    try:
        server = HTTPServer(("0.0.0.0", port), ScoreApiHandler)
        _api_server_instance = server
        _api_thread = threading.Thread(target=server.serve_forever, daemon=True)
        _api_thread.start()
        print(f"📡 Multi-Player Leaderboard API escuchando en http://0.0.0.0:{port}")
    except OSError:
        # El puerto ya puede estar en uso por una recarga previa
        pass

    return _api_server_instance
