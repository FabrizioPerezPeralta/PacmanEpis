"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
VIEW: arcade_view.py
Capa de Presentación para el Mueble Arcade y Canvas CRT Web (Cyber Packet / Pac-Man).
"""

import os
from typing import List, Dict, Any
import streamlit as st
import streamlit.components.v1 as components
from models.supabase_client import get_supabase_credentials


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
        initial_high_score: int = 0,
        top_player: str = "DEV_SECOPS",
        player_name: str = "DEV_SECOPS",
        difficulty_speed: float = 1.0,
        top_5: List[Dict[str, Any]] = None
    ) -> str:
        """Ensambla el documento HTML autónomo con autenticación inicial de usuario, audio y Game Loop."""
        css_content = self._read_file(self.css_path)
        base_game_js = self._read_file(self.js_base_path)
        audio_service_js = self._read_file(self.js_audio_path)
        game_js = self._read_file(self.js_game_path)
        sb_url, sb_key = get_supabase_credentials()
        sb_url_str = sb_url or ""
        sb_key_str = sb_key or ""

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
      max-width: 500px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .auth-box-input {{
      width: 100%;
      max-width: 280px;
      padding: 8px 12px;
      background: #080d22;
      border: 2px solid var(--neon-cyan);
      border-radius: 6px;
      color: var(--neon-yellow);
      font-family: var(--font-retro);
      font-size: 11px;
      text-align: center;
      text-transform: uppercase;
      outline: none;
      box-shadow: 0 0 15px rgba(0, 240, 255, 0.35);
      margin-bottom: 8px;
      letter-spacing: 1px;
      transition: all 0.25s ease;
    }}

    .auth-box-input:focus {{
      border-color: #ffe600;
      box-shadow: 0 0 25px rgba(255, 230, 0, 0.7);
      background: #0c1433;
    }}

    .auth-box-input::placeholder {{
      color: #64748b;
      font-size: 9px;
      letter-spacing: 0.5px;
    }}

    @keyframes pulseNotice {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.03); opacity: 0.9; }}
    }}

    @keyframes shake {{
      0%, 100% {{ transform: translateX(0); }}
      20%, 60% {{ transform: translateX(-6px); }}
      40%, 80% {{ transform: translateX(6px); }}
    }}

    .shake {{
      animation: shake 0.4s ease;
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

              <!-- OVERLAY DE INICIO: PEDIR NOMBRE DE USUARIO OBLIGATORIO -->
              <div class="canvas-overlay active" id="authOverlay" style="padding: 14px 18px;">
                <div style="font-size: 26px; margin-bottom: 4px; filter: drop-shadow(0 0 10px #00f0ff);">🎮</div>
                
                <div style="display: inline-block; background: rgba(0, 240, 255, 0.15); border: 1px solid #00f0ff; border-radius: 16px; padding: 2px 10px; font-size: 8px; font-weight: bold; letter-spacing: 1.5px; color: #00f0ff; margin-bottom: 6px; text-transform: uppercase;">
                  PASO 1 // REGISTRO DE OPERADOR
                </div>

                <h1 style="color: #ffe600; font-size: 13px; font-weight: 900; letter-spacing: 1px; text-shadow: 0 0 10px rgba(255, 230, 0, 0.7); margin: 0 0 6px 0; line-height: 1.3;">
                  ¡INGRESA TU NOMBRE DE USUARIO!
                </h1>

                <p style="font-size: 11px; margin-bottom: 8px; color: #cbd5e1; font-family: var(--font-pixel); line-height: 1.3; max-width: 290px;">
                  Tu puntaje se guardará automáticamente en <strong style="color: #00ff88;">Supabase</strong> con este nombre:
                </p>
                
                <input type="text" id="inputPlayerName" class="auth-box-input" maxlength="12" value="" placeholder="ESCRIBE TU NOMBRE AQUÍ..." autofocus autocomplete="off" />
                
                <div id="authWarning" style="display: none; color: #ff0055; font-size: 8px; font-weight: bold; margin-top: -4px; margin-bottom: 8px; text-shadow: 0 0 8px rgba(255, 0, 85, 0.8);">
                  ⚠️ ¡DEBES ESCRIBIR TU NOMBRE PARA COMENZAR!
                </div>

                <div class="overlay-buttons" style="margin-bottom: 4px;">
                  <button class="retro-btn" id="btnStartWithUser" style="background: linear-gradient(90deg, #00f0ff, #00d2ff); color: #05070f; font-weight: 900; font-size: 9px; padding: 8px 20px; box-shadow: 0 0 15px rgba(0,240,255,0.7); border: 2px solid #fff; letter-spacing: 1px;">
                    ▶ CONFIRMAR Y JUGAR [ENTER]
                  </button>
                </div>

                <div style="font-size: 7px; color: #64748b; margin-top: 4px; letter-spacing: 0.5px;">
                  🎯 Máximo 12 caracteres (Letras, números o guiones)
                </div>
              </div>

              <!-- OVERLAY DE PAUSA / GAME OVER -->
              <div class="canvas-overlay" id="screenOverlay">
                <h2 class="overlay-title" id="overlayTitle">GAME OVER</h2>
                <p class="overlay-msg" id="overlayMsg">El virus secuestró tu paquete TCP/IP.</p>
                <div id="gameOverTop5Container" style="width: 100%; max-width: 320px; background: rgba(8, 12, 26, 0.95); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 12px; margin-bottom: 14px; text-align: left;">
                  <div style="font-size: 7px; color: #ffe600; text-transform: uppercase; margin-bottom: 4px; font-weight: bold;">
                    🏆 TABLA ACTUALIZADA TOP 5:
                  </div>
                  <div id="gameOverTop5List">
                    {top_5_html}
                  </div>
                </div>
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
      const SUPABASE_REST_URL = "{sb_url_str}";
      const SUPABASE_ANON_KEY = "{sb_key_str}";

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

      function renderTop5List(top5Data) {{
        if (!top5Data || !top5Data.length) return;
        const badges = ["🥇", "🥈", "🥉", "🎖️", "🎖️"];
        const rows = top5Data.slice(0, 5).map((item, idx) => {{
          const b = badges[idx] || `#${{idx+1}}`;
          const name = item.player || 'ANON';
          const score = (item.score || 0).toLocaleString();
          const lvl = item.level || `Nivel ${{8-idx}}`;
          return `
            <div style="display: flex; justify-content: space-between; font-size: 8px; margin-bottom: 3px; color: #a5b4fc;">
              <span>${{b}} ${{name}} (${{lvl}})</span>
              <span style="color: #00f0ff; font-weight: bold;">${{score}} B</span>
            </div>
          `;
        }}).join('');

        const miniEl = document.getElementById('miniTop5Container');
        if (miniEl) miniEl.innerHTML = rows;

        const overEl = document.getElementById('gameOverTop5List');
        if (overEl) overEl.innerHTML = rows;
      }}

      function syncScoreToServer(finalScore, levelNum) {{
        const payload = {{
          player: activeOperatorName,
          score: finalScore,
          level: `Nivel ${{levelNum || 1}}`
        }};

        // 1. Sincronización directa a Supabase Cloud vía PostgREST RPC si está disponible
        if (SUPABASE_REST_URL && SUPABASE_ANON_KEY) {{
          fetch(`${{SUPABASE_REST_URL}}/rest/v1/rpc/submit_score`, {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`
            }},
            body: JSON.stringify({{
              p_player_tag: activeOperatorName,
              p_score: finalScore,
              p_level: `Nivel ${{levelNum || 1}}`,
              p_difficulty: 'normal'
            }})
          }})
          .then(res => res.json())
          .then(() => {{
            fetchTop5FromServer();
          }})
          .catch(() => {{}});
        }}

        // 2. Sincronización a API local en puerto 8502 (Fallback)
        const host = window.location.hostname || 'localhost';
        const apiUrl = `http://${{host}}:8502/api/score`;

        fetch(apiUrl, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }})
        .then(res => res.json())
        .then(data => {{
          if (data.top_5) {{
            renderTop5List(data.top_5);
          }}
        }})
        .catch(() => {{}});
      }}

      function fetchTop5FromServer() {{
        // Consultar Supabase si está activo
        if (SUPABASE_REST_URL && SUPABASE_ANON_KEY) {{
          fetch(`${{SUPABASE_REST_URL}}/rest/v1/scores?select=player_tag,score,level&order=score.desc,created_at.asc&limit=5`, {{
            headers: {{
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`
            }}
          }})
          .then(res => res.json())
          .then(data => {{
            if (Array.isArray(data) && data.length > 0) {{
              const mapped = data.map(item => ({{
                player: item.player_tag,
                score: item.score,
                level: item.level
              }}));
              renderTop5List(mapped);
              if (mapped[0] && mapped[0].score > highestScore) {{
                highestScore = mapped[0].score;
                hudHighScore.innerText = String(highestScore).padStart(5, '0');
              }}
            }}
          }})
          .catch(() => {{}});
        }}

        // También consultar API local
        const host = window.location.hostname || 'localhost';
        const apiUrl = `http://${{host}}:8502/api/top5`;
        fetch(apiUrl)
        .then(res => res.json())
        .then(data => {{
          if (data.top_5) {{
            renderTop5List(data.top_5);
            if (data.high_score && data.high_score > highestScore) {{
              highestScore = data.high_score;
              hudHighScore.innerText = String(highestScore).padStart(5, '0');
            }}
          }}
        }})
        .catch(() => {{}});
      }}

      // Polling cada 3 segundos para actualización en tiempo real
      setInterval(fetchTop5FromServer, 3000);

      function showGameOver(finalScore) {{
        overlayTitle.innerText = "SISTEMA COMPROMETIDO";
        overlayTitle.style.color = "#ff0055";
        const lvl = currentGame ? currentGame.level : 1;
        overlayMsg.innerHTML = `Operador: <strong>${{activeOperatorName}}</strong><br>Puntaje Final: <strong>${{finalScore.toLocaleString()}} Bytes</strong> (Nivel ${{lvl}}).<br>¡Récord sincronizado en tiempo real con el Top 5!`;
        btnOverlayAction.innerText = "REINTENTAR [R]";
        overlay.classList.add('active');
        audioService.play('death');

        // Sincronizar puntaje con el servidor multijugador
        syncScoreToServer(finalScore, lvl);
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
        if (!raw) {{
          const authWarning = document.getElementById('authWarning');
          if (authWarning) {{
            authWarning.style.display = 'block';
            authWarning.classList.add('shake');
            setTimeout(() => authWarning.classList.remove('shake'), 400);
          }}
          inputPlayerName.style.borderColor = '#ff0055';
          inputPlayerName.style.boxShadow = '0 0 25px rgba(255, 0, 85, 0.8)';
          inputPlayerName.focus();
          return;
        }}
        activeOperatorName = raw.slice(0, 12);
        hudPlayer.innerText = activeOperatorName;
        audioService.init();
        initNewGame();
      }}

      inputPlayerName.addEventListener('input', () => {{
        const authWarning = document.getElementById('authWarning');
        if (authWarning && inputPlayerName.value.trim()) {{
          authWarning.style.display = 'none';
        }}
        inputPlayerName.style.borderColor = 'var(--neon-cyan)';
        inputPlayerName.style.boxShadow = '0 0 20px rgba(0, 240, 255, 0.4)';
      }});

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
        initial_high_score: int = 0,
        top_player: str = "DEV_SECOPS",
        player_name: str = "DEV_SECOPS",
        difficulty_speed: float = 1.0,
        top_5: List[Dict[str, Any]] = None,
        height: int = 685
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
