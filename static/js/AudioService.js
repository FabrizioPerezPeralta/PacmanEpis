/**
 * SYS-ENGINEER ARCADE 198X
 * PATRÓN DE DISEÑO: Facade + Singleton (Audio Synthesis Service)
 * 
 * Propósito:
 * Oculta la complejidad de la Web Audio API (nodos osciladores, envolventes de ganancia,
 * ruteo de compresión y scheduling temporal) detrás de una interfaz simple y expresiva.
 * Incluye un DynamicsCompressorNode maestro para evitar distorsiones y clipping.
 */

class AudioService {
  constructor() {
    this.ctx = null;
    this.enabled = true;
    this.volume = 0.22;
    this.bgmPlaying = false;
    this.bgmTimer = null;
    this.compressor = null;

    // Escucha eventos de audio automáticamente vía EventBus
    if (window.SysArcade && window.SysArcade.events) {
      window.SysArcade.events.on('sfx', (sfxName) => this.play(sfxName));
    }
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();

        // Master Limiter / DynamicsCompressorNode
        this.compressor = this.ctx.createDynamicsCompressor();
        this.compressor.threshold.setValueAtTime(-12, this.ctx.currentTime);
        this.compressor.knee.setValueAtTime(30, this.ctx.currentTime);
        this.compressor.ratio.setValueAtTime(12, this.ctx.currentTime);
        this.compressor.attack.setValueAtTime(0.003, this.ctx.currentTime);
        this.compressor.release.setValueAtTime(0.25, this.ctx.currentTime);
        this.compressor.connect(this.ctx.destination);
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.stopBgm();
    }
    return this.enabled;
  }

  playTone(freq, type = 'square', duration = 0.1, delay = 0, volFactor = 1.0) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime + delay;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, now);

      gain.gain.setValueAtTime(this.volume * volFactor, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

      osc.connect(gain);
      gain.connect(this.compressor || this.ctx.destination);

      osc.start(now);
      osc.stop(now + duration);
    } catch (e) {}
  }

  playSweep(startFreq, endFreq, type = 'square', duration = 0.2, volFactor = 1.0) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(startFreq, now);
      osc.frequency.exponentialRampToValueAtTime(Math.max(10, endFreq), now + duration);

      gain.gain.setValueAtTime(this.volume * volFactor, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

      osc.connect(gain);
      gain.connect(this.compressor || this.ctx.destination);

      osc.start(now);
      osc.stop(now + duration);
    } catch (e) {}
  }

  play(sfxName) {
    switch (sfxName) {
      case 'coin':
        this.playTone(987.77, 'square', 0.08, 0, 0.8);
        this.playTone(1318.51, 'square', 0.28, 0.08, 0.8);
        break;
      case 'select':
        this.playTone(587.33, 'triangle', 0.05, 0, 0.6);
        break;
      case 'game_start':
        [440, 554, 659, 880].forEach((f, i) => this.playTone(f, 'square', 0.12, i * 0.08, 0.7));
        break;
      case 'jump':
        this.playSweep(150, 480, 'square', 0.14, 0.6);
        break;
      case 'point':
        this.playTone(523.25, 'square', 0.08, 0, 0.6);
        this.playTone(783.99, 'square', 0.15, 0.08, 0.6);
        break;
      case 'hammer_smash':
        this.playSweep(300, 100, 'square', 0.1, 0.8);
        this.playTone(880, 'triangle', 0.08, 0, 0.7);
        break;
      case 'hammer_pickup':
        [587, 740, 880].forEach((f, i) => this.playTone(f, 'square', 0.08, i * 0.06, 0.7));
        break;
      case 'bomb_explosion':
        this.playSweep(400, 45, 'sawtooth', 0.45, 0.9);
        this.playTone(55, 'square', 0.3, 0.05, 0.8);
        break;
      case 'victory':
        [523, 659, 784, 1046, 880, 1046].forEach((f, i) => this.playTone(f, 'square', 0.14, i * 0.1, 0.8));
        break;
      case 'death':
        [320, 260, 200, 140, 80].forEach((f, i) => this.playTone(f, 'sawtooth', 0.12, i * 0.1, 0.7));
        break;
      case 'pacman_waka':
        this.playSweep(280, 360, 'triangle', 0.06, 0.5);
        break;
      case 'eat_ghost':
        for (let i = 0; i < 5; i++) {
          this.playTone(440 * Math.pow(1.12, i), 'square', 0.05, i * 0.04, 0.7);
        }
        break;
      case 'sniper_shot':
        this.playSweep(1200, 200, 'sawtooth', 0.15, 0.8);
        this.playTone(80, 'square', 0.1, 0.04, 0.7);
        break;
      case 'vortex':
        for (let i = 0; i < 4; i++) {
          this.playSweep(200 + i * 150, 600 + i * 100, 'triangle', 0.08, 0.5);
        }
        break;
      case 'big_bang':
        this.playSweep(80, 950, 'sawtooth', 0.3, 0.9);
        setTimeout(() => {
          this.playSweep(800, 40, 'triangle', 0.6, 1.0);
          this.playTone(50, 'square', 0.7, 0, 0.9);
        }, 180);
        break;
      case 'tetris_rotate':
        this.playTone(440, 'triangle', 0.05, 0, 0.5);
        break;
      case 'tetris_drop':
        this.playSweep(300, 120, 'square', 0.08, 0.6);
        break;
      case 'tetris_line':
        [523, 659, 784, 1046].forEach((f, i) => this.playTone(f, 'square', 0.08, i * 0.05, 0.7));
        break;
      case 'tetris_tetris':
        [523, 659, 784, 1046, 1318].forEach((f, i) => this.playTone(f, 'square', 0.1, i * 0.06, 0.8));
        break;
      case 'fire_burn':
        this.playSweep(90, 140, 'triangle', 0.15, 0.35);
        break;
      case 'mega_clear':
        [523, 659, 784, 1046, 1318, 1567].forEach((f, i) => this.playTone(f, 'square', 0.14, i * 0.07, 0.85));
        break;
    }
  }

  // Tetris Korobeiniki 8-Bit Synthesizer Chiptune BGM
  startBgm() {
    if (this.bgmPlaying || !this.enabled) return;
    this.init();
    this.bgmPlaying = true;

    const melody = [
      { f: 659.25, d: 400 }, { f: 493.88, d: 200 }, { f: 523.25, d: 200 }, { f: 587.33, d: 400 },
      { f: 523.25, d: 200 }, { f: 493.88, d: 200 }, { f: 440.00, d: 400 }, { f: 440.00, d: 200 },
      { f: 523.25, d: 200 }, { f: 659.25, d: 400 }, { f: 587.33, d: 200 }, { f: 523.25, d: 200 },
      { f: 493.88, d: 600 }, { f: 523.25, d: 200 }, { f: 587.33, d: 400 }, { f: 659.25, d: 400 },
      { f: 523.25, d: 400 }, { f: 440.00, d: 400 }, { f: 440.00, d: 400 }
    ];

    let noteIdx = 0;
    const playNext = () => {
      if (!this.bgmPlaying || !this.enabled) return;
      const note = melody[noteIdx];
      this.playTone(note.f, 'square', (note.d / 1000) * 0.8, 0, 0.35);
      this.playTone(note.f / 2, 'triangle', (note.d / 1000) * 0.9, 0, 0.4);
      noteIdx = (noteIdx + 1) % melody.length;
      this.bgmTimer = setTimeout(playNext, note.d);
    };

    playNext();
  }

  stopBgm() {
    this.bgmPlaying = false;
    if (this.bgmTimer) {
      clearTimeout(this.bgmTimer);
      this.bgmTimer = null;
    }
  }

  /* -----------------------------------------------------------
     MÉTODOS DE COMPATIBILIDAD (ADAPTER / BACKWARD COMPATIBILITY)
     ----------------------------------------------------------- */
  toggleAudio() { return this.toggle(); }
  playCoin() { this.play('coin'); }
  playSelect() { this.play('select'); }
  playGameStart() { this.play('game_start'); }
  gameStart() { this.play('game_start'); }
  playPacmanWaka() { this.play('pacman_waka'); }
  playPacmanEatGhost() { this.play('eat_ghost'); }
  playPacmanEatFruit() { this.play('point'); }
  playPacmanDeath() { this.play('death'); }
  playTetrisRotate() { this.play('tetris_rotate'); }
  playTetrisDrop() { this.play('tetris_drop'); }
  playTetrisLine() { this.play('tetris_line'); }
  playTetrisTetris() { this.play('tetris_tetris'); }
  startTetrisBGM() { this.startBgm(); }
  stopTetrisBGM() { this.stopBgm(); }
  playDKJump() { this.play('jump'); }
  playDKBarrel() { this.playTone(85, 'square', 0.06, 0, 0.4); }
  playDKPoint() { this.play('point'); }
  playDKVictory() { this.play('victory'); }
  playDKDeath() { this.play('death'); }
  playSniperShot() { this.play('sniper_shot'); }
  playVortex() { this.play('vortex'); }
  playBigBang() { this.play('big_bang'); }
  playDKBombExplosion() { this.play('bomb_explosion'); }
  playHammerSmash() { this.play('hammer_smash'); }
  playHammerPickup() { this.play('hammer_pickup'); }
  playFireBurn() { this.play('fire_burn'); }
  playMegaClear() { this.play('mega_clear'); }
}

window.SysArcade = window.SysArcade || {};
window.SysArcade.AudioService = AudioService;
window.SysArcade.audio = new AudioService();
// Mantener compatibilidad retroAudio
window.retroAudio = window.SysArcade.audio;

