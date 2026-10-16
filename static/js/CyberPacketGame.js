/**
 * Retro Console 198X - PAC-MAN Game Engine (Enhanced 100-Level Edition)
 * - 100 Unique Procedural Symmetrical Mazes
 * - 5+ Adaptive Hunter Ghosts with Dynamic Changing Patterns
 * - Gradual Ghost Speed Ramp with 5+ Ghosts
 * - Superpellet Powers:
 *   - 65%: Classic Eat Ghosts (10s)
 *   - 20%: Sniper 10x10 Range [Space to Shoot]
 *   - 10%: Magnetic Vortex 7x7 Radius
 *   - 5%:  Big Bang (Map Annihilation & Instant Level Clear)
 * - Maze Mutation every 2 Ghosts Eaten
 * - 3 Lives
 */

class CyberPacketGame extends BaseGame{
  constructor(canvas, onScoreUpdate, onGameOver, onStatusUpdate) {
    super(canvas, { onScoreUpdate, onGameOver, onStatusUpdate });
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.onScoreUpdate = onScoreUpdate;
    this.onGameOver = onGameOver;
    this.onStatusUpdate = onStatusUpdate;

    this.tileSize = 20;
    this.cols = 28;
    this.rows = 31;
    this.offsetX = Math.floor((this.canvas.width - this.cols * this.tileSize) / 2);
    this.offsetY = Math.floor((this.canvas.height - this.rows * this.tileSize) / 2);

    this.score = 0;
    this.highScore = 0;
    this.lives = 3;
    this.level = 1; // 1 to 100
    this.isRunning = false;
    this.isPaused = false;
    this.animationFrameId = null;

    this.map = [];
    this.totalDots = 0;
    this.dotsEaten = 0;
    this.eatenGhostsCounter = 0; // Triggers map change every 2 ghosts

    // Pac-Man Player
    this.pacman = {
      x: 13.5 * this.tileSize,
      y: 23 * this.tileSize,
      dirX: 0,
      dirY: 0,
      nextDirX: 0,
      nextDirY: 0,
      speed: 2.5,
      radius: this.tileSize * 0.45,
      mouthAngle: 0.2,
      mouthSpeed: 0.035,
      mouthDir: 1,
      angle: 0
    };

    // 5+ Hunter Ghosts
    this.ghosts = [];
    this.ghostSpeedMult = 1.0;
    this.ghostSpeedRampTimer = 0;

    // Powers System
    // activePower: null | 'classic' | 'sniper' | 'vortex' | 'bigbang'
    this.activePower = null;
    this.powerTimer = 0;
    this.sniperAmmo = 0;
    this.sniperLaser = null; // { x1, y1, x2, y2, timer }

    // Big Bang visual FX
    this.bigBangFX = null;

    // Vortex visual FX
    this.vortexAngle = 0;

    // Floating text & particles
    this.floatingScores = [];
    this.particles = [];

    // State transitions
    this.levelClearTimer = 0;
    this.isDying = false;
    this.deathTimer = 0;
    this.screenFlashTimer = 0;
  }

  /* -----------------------------------------------------------
     100 Unique Procedural Symmetrical Mazes
     ----------------------------------------------------------- */
  generateLevelMap(levelSeed, mutationIndex = 0) {
    const seed = levelSeed * 7919 + mutationIndex * 31337;
    const pseudoRandom = (offset) => {
      const s = Math.sin(seed + offset) * 10000;
      return s - Math.floor(s);
    };

    // 0: Path, 1: Wall, 2: Dot, 3: Energizer, 4: Ghost Gate, 5: Ghost House
    const grid = Array.from({ length: this.rows }, () => Array(this.cols).fill(2));

    // 1. Perimeter Walls
    for (let r = 0; r < this.rows; r++) {
      grid[r][0] = 1;
      grid[r][this.cols - 1] = 1;
    }
    for (let c = 0; c < this.cols; c++) {
      grid[0][c] = 1;
      grid[this.rows - 1][c] = 1;
    }

    // 2. Wrap Tunnels
    for (let c = 0; c < 5; c++) {
      grid[14][c] = 0;
      grid[15][c] = 0;
      grid[14][this.cols - 1 - c] = 0;
      grid[15][this.cols - 1 - c] = 0;
    }

    // 3. Central Ghost House
    for (let r = 12; r <= 16; r++) {
      for (let c = 10; c <= 17; c++) {
        if (r === 12 && (c === 13 || c === 14)) {
          grid[r][c] = 4; // Gate
        } else if (r === 12 || r === 16 || c === 10 || c === 17) {
          grid[r][c] = 1; // House Wall
        } else {
          grid[r][c] = 5; // Interior
        }
      }
    }

    // 4. Procedural Symmetrical Wall Blocks (Left half mirrored to right half)
    // We generate blocks in rows 2..28 and cols 2..12
    const blockShapes = [
      [[1,1,1],[1,0,1]],
      [[1,1],[1,1]],
      [[1,1,1,1]],
      [[1],[1],[1]],
      [[1,1,0],[0,1,1]]
    ];

    let seedIdx = 1;
    for (let r = 2; r < this.rows - 2; r += 4) {
      for (let c = 2; c < 12; c += 4) {
        // Skip ghost house vicinity
        if (r >= 10 && r <= 18 && c >= 8) continue;
        // Skip tunnel vicinity
        if ((r === 13 || r === 14 || r === 15 || r === 16) && c <= 6) continue;

        const randVal = pseudoRandom(seedIdx++);
        if (randVal > 0.3) {
          const shapeIdx = Math.floor(pseudoRandom(seedIdx++) * blockShapes.length);
          const shape = blockShapes[shapeIdx];

          for (let sr = 0; sr < shape.length; sr++) {
            for (let sc = 0; sc < shape[sr].length; sc++) {
              if (shape[sr][sc] === 1) {
                const targetR = r + sr;
                const targetC = c + sc;
                if (targetR < this.rows - 2 && targetC < 13) {
                  grid[targetR][targetC] = 1;
                  grid[targetR][this.cols - 1 - targetC] = 1; // Symmetrical mirror
                }
              }
            }
          }
        }
      }
    }

    // 5. Pacman starting position must be clear
    grid[23][13] = 0;
    grid[23][14] = 0;
    grid[22][13] = 0;
    grid[22][14] = 0;

    // 6. Strategic Energizers at 4 corners
    grid[3][1] = 3;
    grid[3][this.cols - 2] = 3;
    grid[26][1] = 3;
    grid[26][this.cols - 2] = 3;

    // 7. Ensure tunnels are clear
    grid[14][0] = 0;
    grid[15][0] = 0;
    grid[14][this.cols - 1] = 0;
    grid[15][this.cols - 1] = 0;

    return grid;
  }

  init() {
    this.map = this.generateLevelMap(this.level, 0);
    this.calculateDots();
    this.resetPositions();
    this.ghostSpeedMult = 1.0;
    this.ghostSpeedRampTimer = 0;
    this.activePower = null;
    this.powerTimer = 0;
    this.sniperAmmo = 0;
    this.eatenGhostsCounter = 0;
    this.updateStatus();
  }

  calculateDots() {
    this.totalDots = 0;
    this.dotsEaten = 0;
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        if (this.map[r][c] === 2 || this.map[r][c] === 3) {
          this.totalDots++;
        }
      }
    }
  }

  /* -----------------------------------------------------------
     5+ Ghosts Setup with Adaptive Hunting Logic
     ----------------------------------------------------------- */
  resetPositions() {
    this.pacman.x = 13.5 * this.tileSize;
    this.pacman.y = 23.5 * this.tileSize;
    this.pacman.dirX = 0;
    this.pacman.dirY = 0;
    this.pacman.nextDirX = 0;
    this.pacman.nextDirY = 0;
    this.pacman.angle = 0;

    // Speed scales slightly with level (1 to 100) - REDUCED for fair reaction time
    const baseSpeed = 1.25 + Math.min(0.6, (this.level - 1) * 0.012);

    this.ghosts = [
      // 1. Blinky (Red - Relentless Direct Pursuit)
      {
        name: 'Blinky',
        color: '#ff0033',
        x: 13.5 * this.tileSize,
        y: 11.5 * this.tileSize,
        dirX: -1,
        dirY: 0,
        baseSpeed: baseSpeed * 0.95,
        state: 'chase',
        jitterTimer: 0,
        jitterX: 0,
        jitterY: 0,
        pattern: 'direct'
      },
      // 2. Pinky (Pink - Predictive Flanker)
      {
        name: 'Pinky',
        color: '#ff99cc',
        x: 13.5 * this.tileSize,
        y: 14.5 * this.tileSize,
        dirX: 0,
        dirY: -1,
        baseSpeed: baseSpeed * 0.90,
        state: 'home',
        exitDelay: 40,
        jitterTimer: 0,
        jitterX: 0,
        jitterY: 0,
        pattern: 'anticipate'
      },
      // 3. Inky (Cyan - Pincer Hunter)
      {
        name: 'Inky',
        color: '#00f0ff',
        x: 11.5 * this.tileSize,
        y: 14.5 * this.tileSize,
        dirX: 0,
        dirY: -1,
        baseSpeed: baseSpeed * 0.86,
        state: 'home',
        exitDelay: 100,
        jitterTimer: 0,
        jitterX: 0,
        jitterY: 0,
        pattern: 'pincer'
      },
      // 4. Clyde (Orange - Feint Ambush)
      {
        name: 'Clyde',
        color: '#ff9900',
        x: 15.5 * this.tileSize,
        y: 14.5 * this.tileSize,
        dirX: 0,
        dirY: -1,
        baseSpeed: baseSpeed * 0.82,
        state: 'home',
        exitDelay: 160,
        jitterTimer: 0,
        jitterX: 0,
        jitterY: 0,
        pattern: 'feint'
      },
      // 5. Sue (Violet - Diagonal Interceptor)
      {
        name: 'Sue',
        color: '#bf00ff',
        x: 13.5 * this.tileSize,
        y: 14.5 * this.tileSize,
        dirX: 0,
        dirY: -1,
        baseSpeed: baseSpeed * 0.88,
        state: 'home',
        exitDelay: 220,
        jitterTimer: 0,
        jitterX: 0,
        jitterY: 0,
        pattern: 'diagonal'
      }
    ];

    this.isDying = false;
    this.deathTimer = 0;
  }

  start() {
    this.score = 0;
    this.lives = 3;
    this.level = 1;
    this.init();
    this.isRunning = true;
    this.isPaused = false;
    this.updateHUD();
    this.playSfx('game_start');
    this.loop();
  }

  pause() {
    this.isPaused = !this.isPaused;
  }

  /* -----------------------------------------------------------
     Controls & Shooting (Sniper)
     ----------------------------------------------------------- */
  handleInput(key) {
    if (this.isDying || this.levelClearTimer > 0) return;

    if (key === 'ArrowUp' || key === 'KeyW') {
      this.pacman.nextDirX = 0;
      this.pacman.nextDirY = -1;
    } else if (key === 'ArrowDown' || key === 'KeyS') {
      this.pacman.nextDirX = 0;
      this.pacman.nextDirY = 1;
    } else if (key === 'ArrowLeft' || key === 'KeyA') {
      this.pacman.nextDirX = -1;
      this.pacman.nextDirY = 0;
    } else if (key === 'ArrowRight' || key === 'KeyD') {
      this.pacman.nextDirX = 1;
      this.pacman.nextDirY = 0;
    } else if (key === 'Space' || key === 'KeyZ' || key === 'KeyK') {
      // Sniper shoot trigger
      if (this.activePower === 'sniper' && this.sniperAmmo > 0) {
        this.fireSniper();
      }
    }
  }

  fireSniper() {
    this.sniperAmmo--;
    this.playSfx('sniper_shot');

    // Laser beam along Pacman's facing angle or 10x10 tile box
    const rangePx = 10 * this.tileSize; // 200px range
    let targetX = this.pacman.x + (this.pacman.dirX || 1) * rangePx;
    let targetY = this.pacman.y + this.pacman.dirY * rangePx;

    this.sniperLaser = {
      x1: this.pacman.x,
      y1: this.pacman.y,
      x2: targetX,
      y2: targetY,
      timer: 15
    };

    // Eliminate any ghost within 10x10 tiles (200x200 square around Pacman or laser path)
    let snipedCount = 0;
    for (const g of this.ghosts) {
      if (g.state !== 'eaten') {
        const dx = Math.abs(g.x - this.pacman.x);
        const dy = Math.abs(g.y - this.pacman.y);
        if (dx <= rangePx / 2 && dy <= rangePx / 2) {
          g.state = 'eaten';
          this.score += 250;
          snipedCount++;
          this.addFloatingScore(g.x, g.y, 'SNIPER! +250');
          this.onGhostDefeated();
        }
      }
    }

    if (this.sniperAmmo <= 0) {
      this.activePower = null;
    }
    this.updateHUD();
    this.updateStatus();
  }

  /* -----------------------------------------------------------
     Superpellet Random Power Roll (Exact Probabilities)
     ----------------------------------------------------------- */
  rollSuperPelletPower() {
    const roll = Math.random();

    if (roll < 0.65) {
      // 1. 65%: Come-Fantasmas Clásico (10 segundos)
      this.activePower = 'classic';
      this.powerTimer = 600; // 10 seconds at 60fps
      this.ghosts.forEach(g => {
        if (g.state !== 'eaten') g.state = 'frightened';
      });
      this.addFloatingScore(this.pacman.x, this.pacman.y - 20, '🛡️ ¡ANTIVIRUS! (10s)');
      this.playSfx('point');
    } else if (roll < 0.85) {
      // 2. 20%: Cyber Sniper [ESPACIO / K]
      this.activePower = 'sniper';
      this.powerTimer = 600;
      this.sniperAmmo = 5;
      this.addFloatingScore(this.pacman.x, this.pacman.y - 20, '🎯 SNIPER [ESPACIO / K]');
      this.playSfx('sniper_shot');
    } else if (roll < 0.95) {
      // 3. 10%: Vórtice DDoS
      this.activePower = 'vortex';
      this.powerTimer = 360; // 6 seconds
      this.addFloatingScore(this.pacman.x, this.pacman.y - 20, '🌀 ¡VÓRTICE D-DOS 7x7!');
      this.playSfx('vortex');
    } else {
      // 4. 5%: Hard Reset (Parche total de seguridad)
      this.triggerBigBang();
    }

    this.updateStatus();
  }

  triggerBigBang() {
    this.activePower = 'bigbang';
    this.powerTimer = 90;
    this.bigBangFX = { radius: 10, maxRadius: 450 };

    this.playSfx('big_bang');

    // Collect all remaining points on the map + bonus
    const remainingDots = this.totalDots - this.dotsEaten;
    const bigBangBonus = remainingDots * 15 + 2000;
    this.score += bigBangBonus;
    this.dotsEaten = this.totalDots;

    // Eliminate all ghosts
    this.ghosts.forEach(g => {
      g.state = 'eaten';
    });

    this.addFloatingScore(this.canvas.width / 2, this.canvas.height / 2, `★ BIG BANG! +${bigBangBonus} ★`);

    setTimeout(() => {
      this.levelClearTimer = 60;
    }, 1200);

    this.updateHUD();
    this.updateStatus();
  }

  /* -----------------------------------------------------------
     Maze Mutation Every 2 Ghosts Eaten
     ----------------------------------------------------------- */
  onGhostDefeated() {
    this.eatenGhostsCounter++;
    if (this.eatenGhostsCounter >= 2) {
      this.mutateMaze();
      this.eatenGhostsCounter = 0;
    }
  }

  mutateMaze() {
    this.screenFlashTimer = 15;
    this.addFloatingScore(this.canvas.width / 2, this.canvas.height / 2 - 40, '⚡ ¡MUTACIÓN DE LABERINTO! ⚡');
    this.playSfx('tetris_tetris');

    // Generate new mutation variant of current level
    const newMap = this.generateLevelMap(this.level, Math.floor(Math.random() * 9999) + 1);

    // Transfer dots that were already eaten
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        if (this.map[r] && this.map[r][c] === 0 && (newMap[r][c] === 2 || newMap[r][c] === 3)) {
          newMap[r][c] = 0;
        }
      }
    }

    this.map = newMap;

    // Snap Pacman to nearest valid walkable corridor
    const currentTileX = Math.floor(this.pacman.x / this.tileSize);
    const currentTileY = Math.floor(this.pacman.y / this.tileSize);
    if (this.isWallTile(currentTileX, currentTileY)) {
      // Find open neighbor
      for (let dr = -2; dr <= 2; dr++) {
        for (let dc = -2; dc <= 2; dc++) {
          const nr = Math.max(1, Math.min(this.rows - 2, currentTileY + dr));
          const nc = Math.max(1, Math.min(this.cols - 2, currentTileX + dc));
          if (!this.isWallTile(nc, nr)) {
            this.pacman.x = nc * this.tileSize;
            this.pacman.y = nr * this.tileSize;
            break;
          }
        }
      }
    }
  }

  /* -----------------------------------------------------------
     Update Loop
     ----------------------------------------------------------- */
  update() {
    if (this.screenFlashTimer > 0) this.screenFlashTimer--;

    // Level Clear Transition
    if (this.levelClearTimer > 0) {
      this.levelClearTimer--;
      if (this.levelClearTimer === 0) {
        if (this.level < 100) {
          this.level++;
          this.init();
          this.updateHUD();
          this.playSfx('game_start');
        } else {
          // Completed all 100 Levels!
          this.isRunning = false;
          if (this.onGameOver) this.onGameOver(this.score + 10000);
        }
      }
      return;
    }

    // Dying animation
    if (this.isDying) {
      this.deathTimer++;
      if (this.deathTimer > 70) {
        this.lives--;
        this.updateHUD();
        if (this.lives <= 0) {
          this.isRunning = false;
          if (this.onGameOver) this.onGameOver(this.score);
        } else {
          this.resetPositions();
        }
      }
      return;
    }

    // Gradual Speed Ramp when 5+ ghosts on field
    const activeGhosts = this.ghosts.filter(g => g.state !== 'home');
    if (activeGhosts.length >= 5) {
      this.ghostSpeedRampTimer++;
      // Gradually ramp multiplier every 120 frames
      if (this.ghostSpeedRampTimer % 120 === 0 && this.ghostSpeedMult < 1.65) {
        this.ghostSpeedMult += 0.015;
        this.updateStatus();
      }
    }

    // Update Powers Timer
    if (this.powerTimer > 0) {
      this.powerTimer--;
      if (this.powerTimer === 0) {
        if (this.activePower === 'classic') {
          this.ghosts.forEach(g => {
            if (g.state === 'frightened') g.state = 'chase';
          });
        }
        this.activePower = null;
        this.updateStatus();
      }
    }

    // Vortex Logic: Ghosts in 7x7 tile radius sucked into Pacman's mouth
    if (this.activePower === 'vortex') {
      this.vortexAngle += 0.15;
      const vortexRadiusPx = 3.5 * this.tileSize; // 7x7 tile radius = 3.5 tiles distance
      for (const g of this.ghosts) {
        if (g.state !== 'eaten') {
          const dist = Math.hypot(this.pacman.x - g.x, this.pacman.y - g.y);
          if (dist <= vortexRadiusPx) {
            // Pull ghost toward Pacman
            const angle = Math.atan2(this.pacman.y - g.y, this.pacman.x - g.x);
            g.x += Math.cos(angle) * 5;
            g.y += Math.sin(angle) * 5;

            // If reached mouth, consume!
            if (dist < 14) {
              g.state = 'eaten';
              this.score += 200;
              this.addFloatingScore(g.x, g.y, 'VÓRTICE! +200');
              this.playSfx('eat_ghost');
              this.onGhostDefeated();
              this.updateHUD();
            }
          }
        }
      }
    }

    // Laser timer
    if (this.sniperLaser) {
      this.sniperLaser.timer--;
      if (this.sniperLaser.timer <= 0) this.sniperLaser = null;
    }

    // Big Bang expansion
    if (this.bigBangFX) {
      this.bigBangFX.radius += 18;
      if (this.bigBangFX.radius >= this.bigBangFX.maxRadius) {
        this.bigBangFX = null;
      }
    }

    this.updatePacman();
    this.updateGhosts();
    this.checkCollisions();
    this.updateFloatingScores();
  }

  isWallTile(tileX, tileY) {
    if (tileY < 0 || tileY >= this.rows || tileX < 0 || tileX >= this.cols) return false;
    const tile = this.map[tileY][tileX];
    return tile === 1 || tile === 4;
  }

  canMove(x, y, dirX, dirY) {
    if (dirX === 0 && dirY === 0) return true;
    const testX = x + dirX * this.pacman.speed;
    const testY = y + dirY * this.pacman.speed;

    const r = this.pacman.radius - 1;
    const corners = [
      { x: testX - r, y: testY - r },
      { x: testX + r, y: testY - r },
      { x: testX - r, y: testY + r },
      { x: testX + r, y: testY + r }
    ];

    for (const pt of corners) {
      const tileX = Math.floor(pt.x / this.tileSize);
      const tileY = Math.floor(pt.y / this.tileSize);
      if (tileX >= 0 && tileX < this.cols && tileY >= 0 && tileY < this.rows) {
        if (this.isWallTile(tileX, tileY)) return false;
      }
    }
    return true;
  }

  updatePacman() {
    if (this.pacman.nextDirX !== 0 || this.pacman.nextDirY !== 0) {
      if (this.canMove(this.pacman.x, this.pacman.y, this.pacman.nextDirX, this.pacman.nextDirY)) {
        this.pacman.dirX = this.pacman.nextDirX;
        this.pacman.dirY = this.pacman.nextDirY;
      }
    }

    if (this.canMove(this.pacman.x, this.pacman.y, this.pacman.dirX, this.pacman.dirY)) {
      this.pacman.x += this.pacman.dirX * this.pacman.speed;
      this.pacman.y += this.pacman.dirY * this.pacman.speed;

      this.pacman.mouthAngle += this.pacman.mouthSpeed * this.pacman.mouthDir;
      if (this.pacman.mouthAngle >= 0.35 || this.pacman.mouthAngle <= 0.03) {
        this.pacman.mouthDir *= -1;
      }
    }

    // Tunnels wrap
    if (this.pacman.x < 0) this.pacman.x = this.cols * this.tileSize - 2;
    if (this.pacman.x >= this.cols * this.tileSize) this.pacman.x = 2;

    if (this.pacman.dirX === 1) this.pacman.angle = 0;
    else if (this.pacman.dirX === -1) this.pacman.angle = Math.PI;
    else if (this.pacman.dirY === 1) this.pacman.angle = Math.PI / 2;
    else if (this.pacman.dirY === -1) this.pacman.angle = -Math.PI / 2;

    // Eat dots and superpellets (corrected centered tile coordinates)
    const currTileX = Math.floor(this.pacman.x / this.tileSize);
    const currTileY = Math.floor(this.pacman.y / this.tileSize);

    if (currTileX >= 0 && currTileX < this.cols && currTileY >= 0 && currTileY < this.rows) {
      const tile = this.map[currTileY][currTileX];
      if (tile === 2) {
        this.map[currTileY][currTileX] = 0;
        this.score += 10;
        this.dotsEaten++;
        this.playSfx('pacman_waka');
        this.updateHUD();
      } else if (tile === 3) {
        // SUPERPELLET EATEN -> ROLL SPECIAL POWER!
        this.map[currTileY][currTileX] = 0;
        this.score += 50;
        this.dotsEaten++;
        this.rollSuperPelletPower();
        this.updateHUD();
      }

      if (this.dotsEaten >= this.totalDots) {
        this.levelClearTimer = 80;
        this.playSfx('game_start');
      }
    }
  }

  /* -----------------------------------------------------------
     Adaptive Hunter Ghosts Pursuit
     ----------------------------------------------------------- */
  updateGhosts() {
    this.ghosts.forEach(ghost => {
      if (ghost.state === 'home') {
        ghost.exitDelay--;
        if (ghost.exitDelay <= 0) {
          ghost.x = 13.5 * this.tileSize;
          ghost.y = 11.5 * this.tileSize;
          ghost.state = 'chase';
          ghost.dirX = -1;
          ghost.dirY = 0;
        }
        return;
      }

      if (ghost.state === 'eaten') {
        const homeX = 13.5 * this.tileSize;
        const homeY = 11.5 * this.tileSize;
        const dist = Math.hypot(homeX - ghost.x, homeY - ghost.y);
        if (dist < 12) {
          ghost.state = 'chase';
        }
      }

      // Calculate ghost dynamic speed with 5+ acceleration ramp (tuned for balanced retro play)
      const currentSpeed = (ghost.state === 'frightened')
        ? ghost.baseSpeed * 0.48
        : (ghost.state === 'eaten' ? 3.6 : ghost.baseSpeed * this.ghostSpeedMult);

      // Current tile coordinates and center
      const currentTileX = Math.floor(ghost.x / this.tileSize);
      const currentTileY = Math.floor(ghost.y / this.tileSize);
      const centerTileX = (currentTileX + 0.5) * this.tileSize;
      const centerTileY = (currentTileY + 0.5) * this.tileSize;

      // Lock perpendicular coordinate to corridor center to avoid clipping
      if (ghost.dirX !== 0) {
        ghost.y = centerTileY;
      } else if (ghost.dirY !== 0) {
        ghost.x = centerTileX;
      }

      // Detect if ghost is reaching the center of the current tile or facing a wall
      const willPassCenterX = (ghost.dirX > 0 && ghost.x <= centerTileX && ghost.x + currentSpeed >= centerTileX) ||
                              (ghost.dirX < 0 && ghost.x >= centerTileX && ghost.x - currentSpeed <= centerTileX);
      const willPassCenterY = (ghost.dirY > 0 && ghost.y <= centerTileY && ghost.y + currentSpeed >= centerTileY) ||
                              (ghost.dirY < 0 && ghost.y >= centerTileY && ghost.y - currentSpeed <= centerTileY);

      const nextTileX = currentTileX + ghost.dirX;
      const nextTileY = currentTileY + ghost.dirY;
      const isWallAhead = this.isWallTile(nextTileX, nextTileY);

      const atDecisionPoint = willPassCenterX || willPassCenterY || isWallAhead || (ghost.dirX === 0 && ghost.dirY === 0);

      if (atDecisionPoint) {
        // Snap to center of tile
        ghost.x = centerTileX;
        ghost.y = centerTileY;

        // Find all non-wall directions
        const cardinalDirs = [
          { x: 0, y: -1 }, // UP
          { x: -1, y: 0 }, // LEFT
          { x: 0, y: 1 },  // DOWN
          { x: 1, y: 0 }   // RIGHT
        ];

        let validDirs = cardinalDirs.filter(d => {
          const nx = currentTileX + d.x;
          const ny = currentTileY + d.y;
          // Out of bounds tunnels wrap
          if (ny < 0 || ny >= this.rows || nx < 0 || nx >= this.cols) return true;
          const tile = this.map[ny][nx];
          if (ghost.state === 'eaten' && tile === 4) return true;
          return tile !== 1 && tile !== 4;
        });

        if (validDirs.length === 0) {
          validDirs = [{ x: -ghost.dirX, y: -ghost.dirY }];
        } else if (validDirs.length > 1) {
          // Avoid 180 degree reverse unless dead end
          const nonReverse = validDirs.filter(d => !(d.x === -ghost.dirX && d.y === -ghost.dirY));
          if (nonReverse.length > 0) {
            validDirs = nonReverse;
          }
        }

        let chosenDir = validDirs[0];

        if (ghost.state === 'frightened') {
          // Frightened mode: flee away from Pacman
          let maxDist = -1;
          validDirs.forEach(d => {
            const nx = centerTileX + d.x * this.tileSize;
            const ny = centerTileY + d.y * this.tileSize;
            const dist = Math.hypot(nx - this.pacman.x, ny - this.pacman.y);
            if (dist > maxDist) {
              maxDist = dist;
              chosenDir = d;
            }
          });
        } else {
          // Chase mode: Calculate targeted strategy for each virus
          let targetX = this.pacman.x;
          let targetY = this.pacman.y;

          if (ghost.state === 'eaten') {
            targetX = 13.5 * this.tileSize;
            targetY = 11.5 * this.tileSize;
          } else if (ghost.pattern === 'anticipate') {
            // Pinky (Phishing): leads 4 tiles ahead of Pacman
            const pdirX = this.pacman.dirX || 1;
            const pdirY = this.pacman.dirY || 0;
            targetX = this.pacman.x + pdirX * 4 * this.tileSize;
            targetY = this.pacman.y + pdirY * 4 * this.tileSize;
          } else if (ghost.pattern === 'pincer') {
            // Inky (Spyware): coordinates pinza attack with Blinky
            const blinky = this.ghosts[0] || { x: 13.5 * this.tileSize, y: 11.5 * this.tileSize };
            targetX = this.pacman.x * 2 - blinky.x;
            targetY = this.pacman.y * 2 - blinky.y;
          } else if (ghost.pattern === 'feint') {
            // Clyde (Trojan): chases when far, retreats to corner when close
            const distToPacman = Math.hypot(ghost.x - this.pacman.x, ghost.y - this.pacman.y);
            if (distToPacman < 8 * this.tileSize) {
              targetX = 2 * this.tileSize;
              targetY = 28 * this.tileSize;
            }
          } else if (ghost.pattern === 'diagonal') {
            // Shadow / Sue (Malware): chaotic diagonal pressure
            targetX = this.pacman.x + ((ghost.jitterTimer % 120 < 60) ? 3 : -3) * this.tileSize;
            targetY = this.pacman.y + ((ghost.jitterTimer % 120 < 60) ? -3 : 3) * this.tileSize;
          }

          // Pick direction that minimizes Euclidean distance to target
          let minDist = Infinity;
          validDirs.forEach(d => {
            const nx = centerTileX + d.x * this.tileSize;
            const ny = centerTileY + d.y * this.tileSize;
            const dist = Math.hypot(nx - targetX, ny - targetY);
            if (dist < minDist) {
              minDist = dist;
              chosenDir = d;
            }
          });
        }

        ghost.dirX = chosenDir.x;
        ghost.dirY = chosenDir.y;
      }

      // Move ghost
      ghost.x += ghost.dirX * currentSpeed;
      ghost.y += ghost.dirY * currentSpeed;

      // Wrap around screen borders (Tunnels)
      if (ghost.x < 0) ghost.x = this.cols * this.tileSize - 2;
      if (ghost.x >= this.cols * this.tileSize) ghost.x = 2;
    });
  }

  checkCollisions() {
    for (const ghost of this.ghosts) {
      const dist = Math.hypot(this.pacman.x - ghost.x, this.pacman.y - ghost.y);
      if (dist < this.tileSize * 0.8) {
        if (ghost.state === 'frightened') {
          ghost.state = 'eaten';
          this.score += 200;
          this.addFloatingScore(ghost.x, ghost.y, '+200');
          this.playSfx('eat_ghost');
          this.onGhostDefeated();
          this.updateHUD();
        } else if (ghost.state === 'chase') {
          this.isDying = true;
          this.deathTimer = 0;
          this.playSfx('death');
          break;
        }
      }
    }
  }

  addFloatingScore(x, y, text) {
    this.floatingScores.push({ x, y, text, life: 50 });
  }

  updateFloatingScores() {
    for (let i = this.floatingScores.length - 1; i >= 0; i--) {
      this.floatingScores[i].life--;
      this.floatingScores[i].y -= 0.5;
      if (this.floatingScores[i].life <= 0) {
        this.floatingScores.splice(i, 1);
      }
    }
  }

  updateHUD() {
    if (this.score > this.highScore) this.highScore = this.score;
    if (this.onScoreUpdate) {
      this.onScoreUpdate({
        score: this.score,
        highScore: this.highScore,
        level: `${this.level} / 100`,
        lives: this.lives
      });
    }
  }

  updateStatus() {
    let powerText = 'NINGUNO';
    if (this.activePower === 'classic') {
      powerText = `COME-FANTASMAS (${Math.ceil(this.powerTimer / 60)}s)`;
    } else if (this.activePower === 'sniper') {
      powerText = `🎯 SNIPER [${this.sniperAmmo} TIROS]`;
    } else if (this.activePower === 'vortex') {
      powerText = `🌀 VÓRTICE (${Math.ceil(this.powerTimer / 60)}s)`;
    } else if (this.activePower === 'bigbang') {
      powerText = `💥 BIG BANG!`;
    }

    const ghostSpdPercent = Math.round(this.ghostSpeedMult * 100);
    const eventText = `👻 5+ VELOCIDAD: ${ghostSpdPercent}% | MUTACIÓN: ${this.eatenGhostsCounter}/2`;

    if (this.onStatusUpdate) {
      this.onStatusUpdate(powerText, eventText);
    }
  }

  /* -----------------------------------------------------------
     Canvas Rendering
     ----------------------------------------------------------- */
  render() {
    // Screen Flash on mutation or Big Bang
    if (this.screenFlashTimer > 0) {
      this.ctx.fillStyle = '#ffffff';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      return;
    }

    this.ctx.fillStyle = '#000000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.save();
    this.ctx.translate(this.offsetX, this.offsetY);

    // 1. Draw Maze
    this.drawMaze();

    // 2. Draw Sniper Range Box & Aiming Reticle
    if (this.activePower === 'sniper') {
      this.drawSniperOverlay();
    }

    // 3. Draw Vortex Aura
    if (this.activePower === 'vortex') {
      this.drawVortexAura();
    }

    // 4. Draw Laser Beam
    if (this.sniperLaser) {
      this.drawLaserBeam();
    }

    // 5. Draw Pac-Man
    if (this.isDying) {
      this.drawDyingPacman();
    } else {
      this.drawPacman();
    }

    // 6. Draw 5+ Ghosts
    this.ghosts.forEach(ghost => this.drawGhost(ghost));

    // 7. Draw Big Bang Expansion
    if (this.bigBangFX) {
      this.drawBigBangFX();
    }

    // 8. Draw Floating Scores
    this.floatingScores.forEach(fs => {
      this.ctx.fillStyle = '#ffe600';
      this.ctx.font = '10px "Press Start 2P", monospace';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(fs.text, fs.x, fs.y);
    });

    this.ctx.restore();
  }

  drawMaze() {
    // Unique color palette per 10-level tier for variety
    const wallColors = [
      '#1919a6', '#0099ff', '#00bb66', '#ff0077', '#ff6600',
      '#aa00ff', '#00ddcc', '#dddd00', '#ff3333', '#ffffff'
    ];
    const colorIdx = Math.floor((this.level - 1) / 10) % wallColors.length;
    const wallColor = wallColors[colorIdx];

    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const tile = this.map[r][c];
        const x = c * this.tileSize;
        const y = r * this.tileSize;

        if (tile === 1) {
          this.ctx.fillStyle = wallColor;
          this.ctx.fillRect(x + 2, y + 2, this.tileSize - 4, this.tileSize - 4);
          this.ctx.strokeStyle = '#00f0ff';
          this.ctx.lineWidth = 1;
          this.ctx.strokeRect(x + 2, y + 2, this.tileSize - 4, this.tileSize - 4);
        } else if (tile === 2) {
          this.ctx.fillStyle = '#ffb8ae';
          this.ctx.beginPath();
          this.ctx.arc(x + this.tileSize / 2, y + this.tileSize / 2, 2.5, 0, Math.PI * 2);
          this.ctx.fill();
        } else if (tile === 3) {
          if (Math.floor(Date.now() / 200) % 2 === 0) {
            this.ctx.fillStyle = '#ffe600';
            this.ctx.beginPath();
            this.ctx.arc(x + this.tileSize / 2, y + this.tileSize / 2, 6, 0, Math.PI * 2);
            this.ctx.fill();
          }
        } else if (tile === 4) {
          this.ctx.strokeStyle = '#ffb8ae';
          this.ctx.lineWidth = 3;
          this.ctx.beginPath();
          this.ctx.moveTo(x, y + this.tileSize / 2);
          this.ctx.lineTo(x + this.tileSize, y + this.tileSize / 2);
          this.ctx.stroke();
        }
      }
    }
  }

  drawSniperOverlay() {
    const rangePx = 10 * this.tileSize;
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
    this.ctx.lineWidth = 1.5;
    this.ctx.setLineDash([4, 4]);
    this.ctx.strokeRect(this.pacman.x - rangePx / 2, this.pacman.y - rangePx / 2, rangePx, rangePx);

    // Aim crosshair
    this.ctx.setLineDash([]);
    this.ctx.strokeStyle = '#ff0055';
    this.ctx.beginPath();
    this.ctx.arc(this.pacman.x, this.pacman.y, 14, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.restore();
  }

  drawVortexAura() {
    const vortexRadius = 3.5 * this.tileSize;
    this.ctx.save();
    this.ctx.translate(this.pacman.x, this.pacman.y);
    this.ctx.rotate(this.vortexAngle);

    this.ctx.strokeStyle = 'rgba(180, 0, 255, 0.6)';
    this.ctx.lineWidth = 2.5;
    this.ctx.setLineDash([8, 6]);
    this.ctx.beginPath();
    this.ctx.arc(0, 0, vortexRadius, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.restore();
  }

  drawLaserBeam() {
    this.ctx.save();
    this.ctx.strokeStyle = '#ff0033';
    this.ctx.lineWidth = 5;
    this.ctx.shadowColor = '#ff0055';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.moveTo(this.sniperLaser.x1, this.sniperLaser.y1);
    this.ctx.lineTo(this.sniperLaser.x2, this.sniperLaser.y2);
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawBigBangFX() {
    this.ctx.save();
    this.ctx.fillStyle = 'rgba(255, 230, 0, 0.4)';
    this.ctx.beginPath();
    this.ctx.arc(this.canvas.width / 2, this.canvas.height / 2, this.bigBangFX.radius, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.strokeStyle = '#ffffff';
    this.ctx.lineWidth = 4;
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawPacman() {
    this.ctx.save();
    this.ctx.translate(this.pacman.x, this.pacman.y);
    this.ctx.rotate(this.pacman.angle);

    this.ctx.fillStyle = this.activePower === 'sniper' ? '#00f0ff' : (this.activePower === 'vortex' ? '#bf00ff' : '#ffe600');
    this.ctx.beginPath();
    const openAngle = this.pacman.mouthAngle * Math.PI;
    this.ctx.arc(0, 0, this.pacman.radius, openAngle, Math.PI * 2 - openAngle);
    this.ctx.lineTo(0, 0);
    this.ctx.closePath();
    this.ctx.fill();

    this.ctx.restore();
  }

  drawDyingPacman() {
    this.ctx.save();
    this.ctx.translate(this.pacman.x, this.pacman.y);
    const progress = this.deathTimer / 70;
    const openAngle = Math.min(Math.PI, progress * Math.PI);

    this.ctx.fillStyle = '#ffe600';
    this.ctx.beginPath();
    this.ctx.arc(0, 0, this.pacman.radius * (1 - progress * 0.5), -Math.PI / 2 + openAngle, 1.5 * Math.PI - openAngle);
    this.ctx.lineTo(0, 0);
    this.ctx.fill();
    this.ctx.restore();
  }

  drawGhost(ghost) {
    this.ctx.save();
    this.ctx.translate(ghost.x, ghost.y);

    const r = this.pacman.radius;

    if (ghost.state === 'frightened') {
      const isFlashing = this.powerTimer < 180 && Math.floor(this.powerTimer / 15) % 2 === 0;
      this.ctx.fillStyle = isFlashing ? '#ffffff' : '#0000bb';
    } else if (ghost.state === 'eaten') {
      this.ctx.fillStyle = 'transparent';
    } else {
      this.ctx.fillStyle = ghost.color;
    }

    if (ghost.state !== 'eaten') {
      this.ctx.beginPath();
      this.ctx.arc(0, -2, r, Math.PI, 0, false);
      this.ctx.lineTo(r, r);
      this.ctx.lineTo(r * 0.6, r - 3);
      this.ctx.lineTo(r * 0.2, r);
      this.ctx.lineTo(-r * 0.2, r - 3);
      this.ctx.lineTo(-r * 0.6, r);
      this.ctx.lineTo(-r, r - 3);
      this.ctx.closePath();
      this.ctx.fill();
    }

    const eyeOffsetX = ghost.dirX * 3;
    const eyeOffsetY = ghost.dirY * 3;

    if (ghost.state === 'frightened') {
      this.ctx.fillStyle = '#ffcc00';
      this.ctx.fillRect(-4, -4, 2, 2);
      this.ctx.fillRect(2, -4, 2, 2);
    } else {
      this.ctx.fillStyle = '#ffffff';
      this.ctx.beginPath();
      this.ctx.arc(-4 + eyeOffsetX * 0.5, -3 + eyeOffsetY * 0.5, 4, 0, Math.PI * 2);
      this.ctx.arc(4 + eyeOffsetX * 0.5, -3 + eyeOffsetY * 0.5, 4, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.fillStyle = '#0000ff';
      this.ctx.beginPath();
      this.ctx.arc(-4 + eyeOffsetX, -3 + eyeOffsetY, 2, 0, Math.PI * 2);
      this.ctx.arc(4 + eyeOffsetX, -3 + eyeOffsetY, 2, 0, Math.PI * 2);
      this.ctx.fill();
    }

    this.ctx.restore();
  }

  loop() {
    if (!this.isRunning) return;
    if (!this.isPaused) {
      this.update();
      this.render();
    }
    this.animationFrameId = requestAnimationFrame(() => this.loop());
  }
  stop() {
    this.isRunning = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }
}

window.CyberPacketGame = CyberPacketGame;
window.PacmanGame = CyberPacketGame;
window.SysArcade = window.SysArcade || {};
window.SysArcade.CyberPacketGame = CyberPacketGame;
window.SysArcade.PacmanGame = CyberPacketGame;
