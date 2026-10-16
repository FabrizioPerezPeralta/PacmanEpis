/**
 * SYS-ENGINEER ARCADE 198X
 * PATRÓN DE DISEÑO: Template Method (Método Plantilla)
 * 
 * Propósito:
 * Define el esqueleto inmutable del ciclo de vida y del bucle de ejecución (Game Loop)
 * de cualquier juego en el Arcade (start, loop, pause, resume, stop).
 * Delega los pasos variables específicos (update, render, handleInput, onStart, onStop)
 * a las subclases especializadas (BugHunterGame, CyberPacketGame, StackOverflowGame),
 * garantizando coherencia en delta-time, cálculo de FPS y manejo de eventos.
 */

class BaseGame {
  /**
   * @param {HTMLCanvasElement} canvas Canvas principal de renderizado
   * @param {Object} options Opciones de configuración y dependencias
   */
  constructor(canvas, options = {}) {
    if (new.target === BaseGame) {
      throw new TypeError("BaseGame es una clase abstracta y no puede instanciarse directamente.");
    }

    this.canvas = canvas;
    this.ctx = canvas ? canvas.getContext('2d') : null;
    this.options = options;

    // Servicios inyectados o referenciados del namespace global
    this.events = options.events || (window.SysArcade && window.SysArcade.events);
    this.storage = options.storage || (window.SysArcade && window.SysArcade.storage);
    this.audio = options.audio || (window.SysArcade && window.SysArcade.audio);

    // Callbacks tradicionales para compatibilidad total
    this.onScoreUpdate = options.onScoreUpdate || null;
    this.onGameOver = options.onGameOver || null;
    this.onStatusUpdate = options.onStatusUpdate || null;

    // Métricas del juego
    this.score = 0;
    this.highScore = 0;
    this.lives = 3;
    this.level = 1;

    // Control del Game Loop
    this.isRunning = false;
    this.isPaused = false;
    this.isGameOver = false;
    this.animationFrameId = null;
    this.lastTime = 0;

    // Bind del bucle de animación para preservar el contexto de ejecución
    this._boundLoop = this._gameLoop.bind(this);
  }

  /* =========================================================================
     MÉTODO PLANTILLA (TEMPLATE METHOD): Ciclo de Vida del Juego
     ========================================================================= */

  /**
   * Inicia el juego. Prepara el estado, emite el evento y arranca el loop.
   */
  start() {
    this.isRunning = true;
    this.isPaused = false;
    this.isGameOver = false;
    this.lastTime = performance.now();

    this.onStart();

    if (this.events) {
      this.events.emit('game:start', { game: this.constructor.name });
    }

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.animationFrameId = requestAnimationFrame(this._boundLoop);
  }

  /**
   * Pausa o alterna el estado de pausa.
   */
  pause() {
    if (!this.isRunning || this.isGameOver) return;
    this.isPaused = !this.isPaused;

    if (this.isPaused) {
      this.onPause();
      if (this.events) this.events.emit('game:pause');
    } else {
      this.lastTime = performance.now();
      this.onResume();
      if (this.events) this.events.emit('game:resume');
    }
  }

  /**
   * Reanuda explícitamente el juego.
   */
  resume() {
    if (this.isPaused) {
      this.pause();
    }
  }

  /**
   * Detiene el juego y cancela cualquier animación en curso.
   */
  stop() {
    this.isRunning = false;
    this.isPaused = false;

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    this.onStop();

    if (this.events) {
      this.events.emit('game:stop', { game: this.constructor.name });
    }
  }

  /* =========================================================================
     NÚCLEO DEL BUCLE: Invariante del Método Plantilla
     ========================================================================= */

  /**
   * Bucle central con normalización de Delta Time para ejecución a 60 FPS estables.
   * @private
   */
  _gameLoop(timestamp) {
    if (!this.isRunning) return;

    if (!this.lastTime) this.lastTime = timestamp;
    // Límite de dt a 0.1s para evitar saltos bruscos tras pausas largas o pérdida de foco
    const dt = Math.min((timestamp - this.lastTime) / 1000, 0.1);
    this.lastTime = timestamp;

    if (!this.isPaused && !this.isGameOver) {
      this.update(dt);
    }

    if (this.ctx) {
      this.render(this.ctx);
    }

    if (this.isRunning) {
      this.animationFrameId = requestAnimationFrame(this._boundLoop);
    }
  }

  /* =========================================================================
     MÉTODOS HOOK / ABSTRACTOS (A sobrescribir por subclases especializadas)
     ========================================================================= */

  /**
   * Hook llamado al iniciar el juego.
   */
  onStart() {}

  /**
   * Hook llamado al pausar el juego.
   */
  onPause() {}

  /**
   * Hook llamado al reanudar el juego.
   */
  onResume() {}

  /**
   * Hook llamado al detener el juego.
   */
  onStop() {}

  /**
   * Lógica de actualización física y estado (debe implementarse en la subclase).
   * @param {number} dt Delta time en segundos
   */
  update(dt) {
    throw new Error(`El método update(dt) debe ser implementado por la subclase ${this.constructor.name}`);
  }

  /**
   * Lógica de renderizado gráfico en el canvas (debe implementarse en la subclase).
   * @param {CanvasRenderingContext2D} ctx Contexto 2D del canvas
   */
  render(ctx) {
    throw new Error(`El método render(ctx) debe ser implementado por la subclase ${this.constructor.name}`);
  }

  /**
   * Manejador de eventos de entrada (teclado, touch, gamepad).
   * @param {string} code Código normalizado de la tecla o acción
   * @param {boolean} isPressed true si fue presionada, false si fue soltada
   */
  handleInput(code, isPressed = true) {}

  /* =========================================================================
     COMUNICACIÓN REACTIVA Y EVENTOS
     ========================================================================= */

  /**
   * Notifica actualización de puntuación y estado al HUD.
   */
  notifyScoreUpdate(data = {}) {
    const payload = {
      score: this.score,
      highScore: this.highScore,
      lives: this.lives,
      level: this.level,
      ...data
    };

    if (this.onScoreUpdate) {
      this.onScoreUpdate(payload);
    }

    if (this.events) {
      this.events.emit('score:update', payload);
    }
  }

  /**
   * Notifica fin de la partida.
   */
  notifyGameOver(finalScore) {
    this.isGameOver = true;
    const score = finalScore !== undefined ? finalScore : this.score;

    if (this.onGameOver) {
      this.onGameOver(score);
    }

    if (this.events) {
      this.events.emit('game:over', { score, game: this.constructor.name });
    }
  }

  /**
   * Notifica actualización dinámica para el Sub-HUD inferior.
   */
  notifyStatusUpdate(val1, val2) {
    if (this.onStatusUpdate) {
      this.onStatusUpdate(val1, val2);
    }

    if (this.events) {
      this.events.emit('status:update', { val1, val2 });
    }
  }

  /**
   * Solicita la reproducción de un efecto de sonido vía EventBus / AudioService.
   */
  playSfx(sfxName) {
    if (this.events) {
      this.events.emit('sfx', sfxName);
    } else if (this.audio) {
      this.audio.play(sfxName);
    }
  }
}

// Registro en el namespace del Arcade
window.SysArcade = window.SysArcade || {};
window.SysArcade.BaseGame = BaseGame;
