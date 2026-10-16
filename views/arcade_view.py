"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
VIEW: arcade_view.py
Capa de Presentación para el Mueble Arcade y Canvas CRT Web (Cyber Packet / Pac-Man).
"""

import os
from typing import List, Dict, Any
import streamlit as st
import streamlit.components.v1 as components


class ArcadeView:
    """Renderiza el componente del Arcade Cabinet CRT interactivo dentro de Streamlit."""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.css_path = os.path.join(base_dir, "static", "css", "arcade.css")
        self.js_base_path = os.path.join(base_dir, "static", "js", "BaseGame.js")
        self.js_audio_path = os.path.join(base_dir, "static", "js", "AudioService.js")
        self.js_game_path = os.path.join(base_dir, "static", "js", "CyberPacketGame.js")

    def _read_file(self, filepath: str) -> str:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"/* Error loading {filepath}: {e} */"

    def generate_html(
        self,
        initial_high_score: int = 14800,
        top_player: str = "KEVIN_M",
        player_name: str = "DEV_SECOPS",
        difficulty_speed: float = 1.0,
        top_5: List[Dict[str, Any]] = None
    ) -> str:
        """Ensambla el documento HTML autónomo con autenticación inicial de usuario, audio y Game Loop."""
        css_content = self._read_file(self.css_path)
        base_game_js = self._read_file(self.js_base_path)
        audio_service_js = self._read_file(self.js_audio_path)
        game_js = self._read_file(self.js_game_path)

        # Generar markup para mini-top5 dentro del modal
        top_5_html = ""
        if top_5:
            rows = []
            badges = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
            for idx, item in enumerate(top_5[:5]):
                b = badges[idx] if idx < len(badges) else f"#{idx+1}"
                name = item.get("player", "ANON")
                score = item.get("score", 0)
                lvl = item.get("level", f"Nivel {8-idx}")
                rows.append(f"""
                <div style="display: flex; justify-content: space-between; font-size: 8px; margin-bottom: 3px; color: #a5b4fc;">
                  <span>{b} {name} ({lvl})</span>
                  <span style="color: #00f0ff; font-weight: bold;">{score:,} B</span>
                </div>
                """)
            top_5_html = "".join(rows)

        html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Cyber Packet Arcade Screen</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Press+Start+2P&family=VT323&family=Share+Tech+Mono&display=swap" rel="stylesheet">
  <style>
    {css_content}

    /* Streamlit Iframe specific adaptations */
    html, body {{
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0;
      background: #05070f;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      overflow-x: hidden;
      overflow-y: auto;
    }}

    .arcade-wrapper {{
      width: 100%;
      max-width: 600px;
      margin: 6px auto;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .auth-box-input {{
      width: 100%;
      max-width: 300px;
      padding: 10px 14px;
      background: #070c1e;
      border: 2px solid var(--neon-cyan);
      border-radius: 8px;
      color: var(--neon-yellow);
      font-family: var(--font-retro);
      font-size: 11px;
      text-align: center;
      text-transform: uppercase;
      outline: none;
      box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
      margin-bottom: 14px;
    }}

    .auth-box-input:focus {{
      border-color: #ffe600;
      box-shadow: 0 0 20px rgba(255, 230, 0, 0.6);
    }}
  </style>
</head>
<body class="arcade-container-body">
  <div class="arcade-wrapper">
    <!-- MUEBLE ARCADE RETRO -->
    <div class="arcade-cabinet" id="arcadeCabinet">
      
      <!-- MARQUEE SUPERIOR ILUMINADA -->
      <div class="marquee-bar">
        <div class="marquee-title">
          <span>🕹️</span>
          <span>CYBER PACKET // 198X</span>
        </div>
        <div class="marquee-badge" id="btnAudioToggle" style="cursor: pointer;" title="Activar/Silenciar Chiptune Audio">
          🔊 AUDIO: <span id="audioStateText">ON</span>
        </div>
      </div>

      <!-- PANTALLA CRT CON BISEL Y SCANLINES -->
      <div class="crt-monitor-frame">
        <div class="bezel-inner">
          <div class="crt-screen">
            <div class="crt-scanlines"></div>
            <div class="crt-vignette"></div>

            <!-- HUD SUPERIOR RETRO -->
            <div class="hud-bar">
              <div class="hud-item">
                <span class="hud-label">OPERADOR</span>
                <span class="hud-value" id="hudPlayer" style="color: #ffe600;">{player_name[:10]}</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">BYTES</span>
                <span class="hud-value" id="hudScore">00000</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">RECORD</span>
                <span class="hud-value gold" id="hudHighScore">{initial_high_score:05d}</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">NIVEL</span>
                <span class="hud-value" id="hudLevel">1 / 100</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">NODOS</span>
                <span class="hud-value" id="hudLives" style="color: #ff0077;">❤️❤️❤️</span>
              </div>
            </div>

            <!-- LIENZO CANVAS DE ALTA VELOCIDAD (28x31 TILES) -->
            <div class="canvas-wrap">
              <canvas id="gameCanvas" width="560" height="620"></canvas>

              <!-- OVERLAY DE INICIO: PEDIR NOMBRE DE USUARIO PRIMERO -->
              <div class="canvas-overlay active" id="authOverlay">
                <div style="font-size: 28px; margin-bottom: 6px;">🚨</div>
                <h2 class="overlay-title" style="color: #00f0ff; font-size: 13px; letter-spacing: 1.5px; margin-bottom: 8px;">
                  ACCESO A LA SUBRED TCP/IP
                </h2>
                <p class="overlay-msg" style="font-size: 15px; margin-bottom: 12px; color: #cbd5e1;">
                  Identifícate con tu nombre de usuario para autorizar el enrutamiento:
                </p>
                
                <input type="text" id="inputPlayerName" class="auth-box-input" maxlength="12" value="{player_name}" placeholder="TU NOMBRE..." autofocus />
                
                <div class="overlay-buttons" style="margin-bottom: 16px;">
                  <button class="retro-btn" id="btnStartWithUser" style="background: var(--neon-cyan); color: #05070f; font-weight: bold; font-size: 10px; padding: 12px 20px; box-shadow: 0 0 15px rgba(0,240,255,0.6);">
                    ▶ INICIAR JUEGO [ENTER]
                  </button>
                </div>

                <div style="width: 100%; max-width: 320px; background: rgba(8, 12, 26, 0.9); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 12px; text-align: left;">
                  <div style="font-size: 7px; color: #ffe600; text-transform: uppercase; margin-bottom: 4px; font-weight: bold;">
                    🏆 TOP 5 DE USUARIOS DESTACADOS:
                  </div>
                  {top_5_html}
                </div>
              </div>

              <!-- OVERLAY DE PAUSA / GAME OVER -->
              <div class="canvas-overlay" id="screenOverlay">
                <h2 class="overlay-title" id="overlayTitle">GAME OVER</h2>
                <p class="overlay-msg" id="overlayMsg">El virus secuestró tu paquete TCP/IP.</p>
                <div class="overlay-buttons">
                  <button class="retro-btn" id="btnOverlayAction">REINTENTAR [R]</button>
                  <button class="retro-btn" id="btnChangeUser" style="border-color: #ffe600; color: #ffe600;">CAMBIAR NOMBRE</button>
                </div>
              </div>
            </div>

            <!-- SUB-HUD: FIREWALL TOKEN ACTIVO Y ESTADO DE RED -->
            <div class="sub-hud-bar">
              <div>
                <span>TOKEN:</span>
                <span class="sub-hud-val" id="hudActiveToken">NINGUNO</span>
              </div>
              <div>
                <span id="hudThreatLevel" style="color: #00f0ff;">👻 5+ VIRUS ACTIVOS</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- DECK DE CONTROL VIRTUAL (TOUCH / MOUSE) -->
      <div class="arcade-control-deck">
        <!-- CRUCETA D-PAD -->
        <div class="dpad-container">
          <button class="dpad-btn dpad-up" id="btnUp" title="Arriba">▲</button>
          <button class="dpad-btn dpad-left" id="btnLeft" title="Izquierda">◀</button>
          <div class="dpad-btn dpad-center"></div>
          <button class="dpad-btn dpad-right" id="btnRight" title="Derecha">▶</button>
          <button class="dpad-btn dpad-down" id="btnDown" title="Abajo">▼</button>
        </div>

        <!-- BOTONES DE ACCIÓN RETRO -->
        <div class="action-buttons-group">
          <button class="action-circle-btn" id="btnAction" title="Disparo Cyber Sniper (Espacio)">
            <span style="font-size: 15px;">🎯</span>
            <span>SNIPER</span>
          </button>
          <button class="action-circle-btn btn-pause-action" id="btnPause" title="Pausa (P)">
            <span style="font-size: 13px;">⏸️</span>
            <span>PAUSA</span>
          </button>
        </div>
      </div>

    </div>
  </div>

  <!-- INYECCIÓN DE ARQUITECTURA JS DEL JUEGO -->
  <script>
    window.SysArcade = window.SysArcade || {{}};
  </script>
  <script>
    {base_game_js}
  </script>
  <script>
    {audio_service_js}
  </script>
  <script>
    {game_js}
  </script>

  <!-- BOOTSTRAP DEL CONTROLADOR CLIENTE -->
  <script>
    (function() {{
      const canvas = document.getElementById('gameCanvas');
      const hudPlayer = document.getElementById('hudPlayer');
      const hudScore = document.getElementById('hudScore');
      const hudHighScore = document.getElementById('hudHighScore');
      const hudLevel = document.getElementById('hudLevel');
      const hudLives = document.getElementById('hudLives');
      const hudActiveToken = document.getElementById('hudActiveToken');
      const hudThreatLevel = document.getElementById('hudThreatLevel');
      
      const authOverlay = document.getElementById('authOverlay');
      const inputPlayerName = document.getElementById('inputPlayerName');
      const btnStartWithUser = document.getElementById('btnStartWithUser');
      
      const overlay = document.getElementById('screenOverlay');
      const overlayTitle = document.getElementById('overlayTitle');
      const overlayMsg = document.getElementById('overlayMsg');
      const btnOverlayAction = document.getElementById('btnOverlayAction');
      const btnChangeUser = document.getElementById('btnChangeUser');
      
      const btnAudioToggle = document.getElementById('btnAudioToggle');
      const audioStateText = document.getElementById('audioStateText');

      // Instancia de Audio Retro
      const audioService = new AudioService();
      window.SysArcade.audio = audioService;

      let currentGame = null;
      let highestScore = {initial_high_score};
      const speedMultiplier = {difficulty_speed};
      let activeOperatorName = "{player_name}";

      function updateHUD(data) {{
        if (data.score !== undefined) {{
          hudScore.innerText = String(data.score).padStart(5, '0');
          if (data.score > highestScore) {{
            highestScore = data.score;
            hudHighScore.innerText = String(highestScore).padStart(5, '0');
          }}
        }}
        if (data.highScore !== undefined && data.highScore > highestScore) {{
          highestScore = data.highScore;
          hudHighScore.innerText = String(highestScore).padStart(5, '0');
        }}
        if (data.level) hudLevel.innerText = data.level;
        if (data.lives !== undefined) {{
          const hearts = '❤️'.repeat(Math.max(0, data.lives));
          hudLives.innerText = hearts || '💀 0';
        }}
      }}

      function updateStatus(powerText, eventText) {{
        if (hudActiveToken && powerText) {{
          hudActiveToken.innerText = powerText;
          if (powerText.includes('SNIPER')) {{
            hudActiveToken.style.color = '#00f0ff';
          }} else if (powerText.includes('VÓRTICE')) {{
            hudActiveToken.style.color = '#a855f7';
          }} else if (powerText.includes('BIG BANG')) {{
            hudActiveToken.style.color = '#ff0055';
          }} else if (powerText.includes('COME')) {{
            hudActiveToken.style.color = '#ffe600';
          }} else {{
            hudActiveToken.style.color = '#00ff88';
          }}
        }}
        if (hudThreatLevel && eventText) {{
          hudThreatLevel.innerText = eventText;
        }}
      }}

      function showGameOver(finalScore) {{
        overlayTitle.innerText = "SISTEMA COMPROMETIDO";
        overlayTitle.style.color = "#ff0055";
        overlayMsg.innerHTML = `Operador: <strong>${{activeOperatorName}}</strong><br>Puntaje Final: <strong>${{finalScore.toLocaleString()}} Bytes</strong>.<br>Las ciberamenazas interceptaron tus paquetes. ¡Refuerza el cortafuegos e inténtalo de nuevo!`;
        btnOverlayAction.innerText = "REINTENTAR [R]";
        overlay.classList.add('active');
        audioService.play('death');
      }}

      function initNewGame() {{
        if (currentGame) {{
          currentGame.stop();
        }}
        authOverlay.classList.remove('active');
        overlay.classList.remove('active');
        
        currentGame = new CyberPacketGame(
          canvas,
          updateHUD,
          showGameOver,
          updateStatus
        );

        // Inyectar audio
        currentGame.audio = audioService;
        
        // Ajustar velocidad según dificultad
        if (speedMultiplier) {{
          currentGame.ghostSpeedMult *= speedMultiplier;
        }}

        currentGame.start();
        audioService.init();
        audioService.play('game_start');
      }}

      function authenticateAndStart() {{
        const raw = inputPlayerName.value.trim().toUpperCase();
        activeOperatorName = raw.slice(0, 12) || "DEV_SECOPS";
        hudPlayer.innerText = activeOperatorName;
        audioService.init();
        initNewGame();
      }}

      btnStartWithUser.addEventListener('click', authenticateAndStart);

      inputPlayerName.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') {{
          e.preventDefault();
          authenticateAndStart();
        }}
      }});

      btnChangeUser.addEventListener('click', () => {{
        overlay.classList.remove('active');
        authOverlay.classList.add('active');
        inputPlayerName.focus();
      }});

      // Controles táctiles del D-Pad
      const dirMap = {{
        'btnUp': 'ArrowUp',
        'btnDown': 'ArrowDown',
        'btnLeft': 'ArrowLeft',
        'btnRight': 'ArrowRight'
      }};

      Object.entries(dirMap).forEach(([id, code]) => {{
        const btn = document.getElementById(id);
        if (btn) {{
          const trigger = (e) => {{
            e.preventDefault();
            btn.classList.add('pressed');
            audioService.init();
            if (currentGame && currentGame.isRunning) currentGame.handleInput(code);
          }};
          const release = () => btn.classList.remove('pressed');

          btn.addEventListener('touchstart', trigger, {{ passive: false }});
          btn.addEventListener('touchend', release);
          btn.addEventListener('mousedown', trigger);
          btn.addEventListener('mouseup', release);
          btn.addEventListener('mouseleave', release);
        }}
      }});

      // Botón Acción (Sniper)
      const btnAction = document.getElementById('btnAction');
      if (btnAction) {{
        const doAction = (e) => {{
          e.preventDefault();
          audioService.init();
          if (currentGame && currentGame.isRunning) currentGame.handleInput('Space');
        }};
        btnAction.addEventListener('touchstart', doAction, {{ passive: false }});
        btnAction.addEventListener('mousedown', doAction);
      }}

      // Botón Pausa
      const btnPause = document.getElementById('btnPause');
      if (btnPause) {{
        btnPause.addEventListener('click', (e) => {{
          e.preventDefault();
          if (!currentGame) return;
          currentGame.pause();
          if (currentGame.isPaused) {{
            overlayTitle.innerText = "TRANSMISIÓN EN PAUSA";
            overlayTitle.style.color = "#ffe600";
            overlayMsg.innerText = `Operador ${{activeOperatorName}}: Buffer de red suspendido.`;
            btnOverlayAction.innerText = "CONTINUAR [P]";
            overlay.classList.add('active');
          }} else {{
            overlay.classList.remove('active');
          }}
        }});
      }}

      // Botón Overlay Acción (Continuar o Reiniciar)
      btnOverlayAction.addEventListener('click', () => {{
        if (currentGame && currentGame.isPaused) {{
          currentGame.pause();
          overlay.classList.remove('active');
        }} else {{
          initNewGame();
        }}
      }});

      // Silenciar / Activar Audio
      btnAudioToggle.addEventListener('click', () => {{
        const enabled = audioService.toggle();
        audioStateText.innerText = enabled ? 'ON' : 'OFF';
        audioStateText.style.color = enabled ? '#ffe600' : '#888';
      }});

      // Manejador Global de Teclado
      window.addEventListener('keydown', (e) => {{
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) {{
          if (document.activeElement !== inputPlayerName) {{
            e.preventDefault();
          }}
        }}

        audioService.init();

        if (authOverlay.classList.contains('active')) {{
          if (e.key === 'Enter') {{
            authenticateAndStart();
          }}
          return;
        }}

        if (e.code === 'KeyP') {{
          if (currentGame) {{
            currentGame.pause();
            if (currentGame.isPaused) {{
              overlayTitle.innerText = "TRANSMISIÓN EN PAUSA";
              overlayTitle.style.color = "#ffe600";
              overlayMsg.innerText = `Operador ${{activeOperatorName}}: Buffer suspendido.`;
              btnOverlayAction.innerText = "CONTINUAR [P]";
              overlay.classList.add('active');
            }} else {{
              overlay.classList.remove('active');
            }}
          }}
          return;
        }}

        if (e.code === 'KeyR') {{
          initNewGame();
          return;
        }}

        if (currentGame && currentGame.isRunning) {{
          currentGame.handleInput(e.code);
        }}
      }});

      // Focus automático en input de nombre al abrir
      setTimeout(() => {{
        if (inputPlayerName) inputPlayerName.focus();
      }}, 300);

    }})();
  </script>
</body>
</html>"""
        return html_template

    def render(
        self,
        initial_high_score: int = 14800,
        top_player: str = "KEVIN_M",
        player_name: str = "DEV_SECOPS",
        difficulty_speed: float = 1.0,
        top_5: List[Dict[str, Any]] = None,
        height: int = 860
    ):
        """Emite el componente Web dentro del árbol de renderizado de Streamlit."""
        html_code = self.generate_html(
            initial_high_score=initial_high_score,
            top_player=top_player,
            player_name=player_name,
            difficulty_speed=difficulty_speed,
            top_5=top_5
        )
        components.html(html_code, height=height, scrolling=False)
