-- ==============================================================================
-- SYS-ENGINEER ARCADE 198X // CYBER PACKET (PAC-MAN)
-- ESQUEMA DE BASE DE DATOS PARA SUPABASE (POSTGRESQL)
-- ==============================================================================
-- Este script crea todas las tablas, relaciones, vistas, funciones almacenadas,
-- políticas de seguridad (RLS) y datos semilla iniciales para el proyecto.
-- Compatible 100% con el SQL Editor de Supabase.
-- ==============================================================================

-- 1. Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================================
-- 2. TABLAS PRINCIPALES
-- ==============================================================================

-- 2.1 TABLA: PLAYERS (Perfiles y Estadísticas de los Operadores)
CREATE TABLE IF NOT EXISTS public.players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_tag VARCHAR(20) UNIQUE NOT NULL,
    total_games INT NOT NULL DEFAULT 0 CHECK (total_games >= 0),
    highest_score INT NOT NULL DEFAULT 0 CHECK (highest_score >= 0),
    highest_level VARCHAR(30) DEFAULT 'Nivel 1',
    credits INT NOT NULL DEFAULT 5 CHECK (credits >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.players IS 'Catálogo y resumen de rendimiento de los operadores de la consola arcade.';

-- 2.2 TABLA: SCORES (Historial de Partidas y Puntuaciones)
CREATE TABLE IF NOT EXISTS public.scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_tag VARCHAR(20) NOT NULL REFERENCES public.players(player_tag) ON UPDATE CASCADE ON DELETE CASCADE,
    score INT NOT NULL CHECK (score >= 0),
    level VARCHAR(30) NOT NULL DEFAULT 'Nivel 1',
    difficulty VARCHAR(30) NOT NULL DEFAULT 'normal',
    dots_eaten INT DEFAULT 0,
    ghosts_eaten INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.scores IS 'Registro histórico de todas las partidas finalizadas para el Salón de la Fama.';

-- 2.3 TABLA: THREATS (Catálogo Dinámico de Ciberamenazas / Virus)
CREATE TABLE IF NOT EXISTS public.threats (
    id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color_hex VARCHAR(10) NOT NULL,
    icon VARCHAR(10) NOT NULL,
    ai_strategy TEXT NOT NULL,
    real_world_impact TEXT NOT NULL,
    defense_advice TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.threats IS 'Catálogo educativo de virus con sus algoritmos de persecución e impacto real.';

-- 2.4 TABLA: FIREWALL_TOKENS (Catálogo de Tokens de Mitigación / Superpellets)
CREATE TABLE IF NOT EXISTS public.firewall_tokens (
    id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    spawn_rate VARCHAR(10) NOT NULL,
    icon VARCHAR(10) NOT NULL,
    effect TEXT NOT NULL,
    tactical_tip TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.firewall_tokens IS 'Poderes de firewall recolectables en las esquinas de la subred.';

-- 2.5 TABLA: VOCATIONAL_TIPS (Píldoras Educativas y Vocación en Sistemas)
CREATE TABLE IF NOT EXISTS public.vocational_tips (
    id SERIAL PRIMARY KEY,
    tip_text TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'Ciberseguridad',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.vocational_tips IS 'Píldoras vocacionales para fomentar la carrera de Ingeniería de Sistemas.';


-- ==============================================================================
-- 3. ÍNDICES DE ALTO RENDIMIENTO (OPTIMIZACIÓN DE CONSULTAS EN MILISEGUNDOS)
-- ==============================================================================

CREATE INDEX IF NOT EXISTS idx_scores_score_desc ON public.scores (score DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_scores_player_tag ON public.scores (player_tag);
CREATE INDEX IF NOT EXISTS idx_scores_created_at ON public.scores (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_players_highest_score ON public.players (highest_score DESC);


-- ==============================================================================
-- 4. VISTAS SQL (CONSULTAS PRECOMPILADAS PARA LEADERBOARD Y TOP 5)
-- ==============================================================================

-- 4.1 VISTA: v_top_5 (Los 5 mejores registros globales)
CREATE OR REPLACE VIEW public.v_top_5 AS
SELECT 
    s.id,
    s.player_tag AS player,
    s.score,
    s.level,
    s.difficulty,
    s.created_at,
    ROW_NUMBER() OVER (ORDER BY s.score DESC, s.created_at ASC) AS rank
FROM public.scores s
ORDER BY s.score DESC, s.created_at ASC
LIMIT 5;

-- 4.2 VISTA: v_leaderboard (Los 50 mejores registros del Salón de la Fama)
CREATE OR REPLACE VIEW public.v_leaderboard AS
SELECT 
    s.id,
    s.player_tag AS player,
    s.score,
    s.level,
    s.difficulty,
    s.created_at,
    ROW_NUMBER() OVER (ORDER BY s.score DESC, s.created_at ASC) AS rank
FROM public.scores s
ORDER BY s.score DESC, s.created_at ASC
LIMIT 50;

-- 4.3 VISTA: v_player_hall_of_fame (Mejor puntuación individual por cada jugador)
CREATE OR REPLACE VIEW public.v_player_hall_of_fame AS
SELECT 
    p.player_tag,
    p.highest_score AS score,
    p.highest_level AS level,
    p.total_games,
    p.updated_at,
    DENSE_RANK() OVER (ORDER BY p.highest_score DESC) AS rank
FROM public.players p
WHERE p.highest_score > 0
ORDER BY p.highest_score DESC;


-- ==============================================================================
-- 5. PROCEDIMIENTOS ALMACENADOS / RPC (REGISTRO ATÓMICO DE PARTIDAS)
-- ==============================================================================

CREATE OR REPLACE FUNCTION public.submit_score(
    p_player_tag TEXT,
    p_score INT,
    p_level TEXT DEFAULT 'Nivel 1',
    p_difficulty TEXT DEFAULT 'normal'
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_clean_tag VARCHAR(20);
    v_prev_high INT := 0;
    v_is_record BOOLEAN := FALSE;
    v_current_global_high INT := 0;
BEGIN
    -- Sanitizar y formatear tag a mayúsculas
    v_clean_tag := UPPER(TRIM(SUBSTRING(p_player_tag FROM 1 FOR 20)));
    IF v_clean_tag IS NULL OR v_clean_tag = '' THEN
        v_clean_tag := 'OPERADOR_ANON';
    END IF;

    -- Obtener el récord global actual antes de insertar
    SELECT COALESCE(MAX(score), 0) INTO v_current_global_high FROM public.scores;

    -- Upsert del jugador (crear si no existe, actualizar estadísticas)
    INSERT INTO public.players (player_tag, total_games, highest_score, highest_level, updated_at)
    VALUES (v_clean_tag, 1, p_score, p_level, timezone('utc'::text, now()))
    ON CONFLICT (player_tag) DO UPDATE SET
        total_games = public.players.total_games + 1,
        highest_score = GREATEST(public.players.highest_score, EXCLUDED.highest_score),
        highest_level = CASE 
            WHEN EXCLUDED.highest_score >= public.players.highest_score THEN EXCLUDED.highest_level 
            ELSE public.players.highest_level 
        END,
        updated_at = timezone('utc'::text, now())
    RETURNING highest_score INTO v_prev_high;

    -- Insertar el registro de la partida
    INSERT INTO public.scores (player_tag, score, level, difficulty)
    VALUES (v_clean_tag, p_score, p_level, p_difficulty);

    -- Determinar si es nuevo récord mundial
    IF p_score > v_current_global_high THEN
        v_is_record := TRUE;
    END IF;

    RETURN jsonb_build_object(
        'success', true,
        'player', v_clean_tag,
        'score', p_score,
        'level', p_level,
        'is_new_global_record', v_is_record,
        'player_best_score', v_prev_high
    );
END;
$$;

COMMENT ON FUNCTION public.submit_score IS 'Registra una partida finalizada, actualiza estadísticas del jugador y determina récords de forma atómica.';


-- ==============================================================================
-- 6. SEGURIDAD DE ACCESO: ROW LEVEL SECURITY (RLS)
-- ==============================================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.threats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.firewall_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocational_tips ENABLE ROW LEVEL SECURITY;

-- 6.1 POLÍTICAS PARA PLAYERS
CREATE POLICY "Lectura pública de jugadores" 
    ON public.players FOR SELECT 
    USING (true);

CREATE POLICY "Inserción o actualización pública de jugadores" 
    ON public.players FOR ALL 
    USING (true)
    WITH CHECK (true);

-- 6.2 POLÍTICAS PARA SCORES
CREATE POLICY "Lectura pública del leaderboard y partidas" 
    ON public.scores FOR SELECT 
    USING (true);

CREATE POLICY "Inserción pública de nuevos récords" 
    ON public.scores FOR INSERT 
    WITH CHECK (true);

-- 6.3 POLÍTICAS PARA TABLAS DE CATÁLOGO (THREATS, TOKENS, TIPS) - Solo Lectura Pública
CREATE POLICY "Lectura pública de amenazas" 
    ON public.threats FOR SELECT 
    USING (true);

CREATE POLICY "Lectura pública de tokens" 
    ON public.firewall_tokens FOR SELECT 
    USING (true);

CREATE POLICY "Lectura pública de tips vocacionales" 
    ON public.vocational_tips FOR SELECT 
    USING (true);

-- Permisos de ejecución en RPC para usuarios anónimos y autenticados
GRANT EXECUTE ON FUNCTION public.submit_score(TEXT, INT, TEXT, TEXT) TO anon, authenticated, service_role;


-- ==============================================================================
-- 7. DATOS SEMILLA (MIGRACIÓN INICIAL DESDE HIGHSCORES.JSON Y CATÁLOGOS)
-- ==============================================================================

-- 7.1 Semilla de Jugadores Iniciales
INSERT INTO public.players (player_tag, total_games, highest_score, highest_level) VALUES
    ('TEST_USER', 5, 16500, 'Nivel 9'),
    ('KEVIN_M',   8, 14800, 'Nivel 8'),
    ('ALAN_T',    6, 12200, 'Nivel 7'),
    ('ADA_L',     4, 10450, 'Nivel 5'),
    ('LINUS_T',   7,  8900, 'Nivel 4'),
    ('GRACE_H',   3,  7200, 'Nivel 3')
ON CONFLICT (player_tag) DO UPDATE SET
    highest_score = EXCLUDED.highest_score,
    highest_level = EXCLUDED.highest_level;

-- 7.2 Semilla de Puntuaciones Históricas (Leaderboard Original)
INSERT INTO public.scores (player_tag, score, level, difficulty, created_at) VALUES
    ('TEST_USER', 16500, 'Nivel 9', 'normal', NOW() - INTERVAL '1 hour'),
    ('KEVIN_M',   14800, 'Nivel 8', 'normal', NOW() - INTERVAL '5 hours'),
    ('ALAN_T',    12200, 'Nivel 7', 'hardcore', NOW() - INTERVAL '1 day'),
    ('ADA_L',     10450, 'Nivel 5', 'normal', NOW() - INTERVAL '2 days'),
    ('LINUS_T',    8900, 'Nivel 4', 'normal', NOW() - INTERVAL '3 days'),
    ('GRACE_H',    7200, 'Nivel 3', 'novato', NOW() - INTERVAL '4 days');

-- 7.3 Semilla de Amenazas Cibernéticas (ThreatModel)
INSERT INTO public.threats (id, name, color_hex, icon, ai_strategy, real_world_impact, defense_advice) VALUES
    ('ransomware', 'Ransomware (Blinky)', '#ff0044', '🚨', 'Persecución Directa (Euclidiana al nodo)', 'Cifra bases de datos y secuestra archivos exigiendo rescate.', 'Mantén backups inmutables desconectados y segmenta la red.'),
    ('phishing', 'Phishing (Pinky)', '#ff77bb', '🎣', 'Emboscada Anticipada (Intercepción a 4 casillas)', 'Suplanta identidades para robar credenciales bancarias y tokens.', 'Implementa autenticación multifactor (MFA) y capacitación continua.'),
    ('spyware', 'Spyware (Inky)', '#00e5ff', '👁️', 'Flanqueo por Vector (Pinza coordinada con Ransomware)', 'Monitorea pulsaciones de teclado y extrae información confidencial.', 'Monitorea tráfico saliente anómalo y usa EDR avanzado.'),
    ('trojan', 'Trojan (Clyde)', '#ff9900', '🐴', 'Merodeo Tímido (Se camufla a distancia corta)', 'Abre puertas traseras ocultas en software aparentemente inofensivo.', 'Verifica firmas digitales y hashes SHA-256 de ejecutables.'),
    ('malware', 'Malware Polimórfico (Shadow)', '#aa00ff', '👾', 'Infección Caótica (Patrón diagonal impredecible)', 'Muta su código en cada infección para eludir firmas estáticas.', 'Emplea detección basada en heurística y análisis de comportamiento.')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    color_hex = EXCLUDED.color_hex,
    ai_strategy = EXCLUDED.ai_strategy;

-- 7.4 Semilla de Tokens de Firewall (FirewallTokens)
INSERT INTO public.firewall_tokens (id, name, spawn_rate, icon, effect, tactical_tip) VALUES
    ('antivirus', 'Antivirus Endpoint (65%)', '65%', '🛡️', 'Aísla y neutraliza a los virus en modo pánico por 10 segundos.', 'Aprovecha la ventana para contraatacar y absorber amenazas (+200 a +1600 pts).'),
    ('sniper', 'Cyber Sniper (20%)', '20%', '🎯', 'Cañón de pulso láser defensivo con alcance de 10x10 casillas.', 'Presiona [ESPACIO] o [K] para disparar y eliminar virus a distancia.'),
    ('vortex', 'Vórtice DDoS Sinkhole (10%)', '10%', '🌀', 'Singularidad electromagnética que absorbe virus en un radio de 7x7 casillas.', 'Atrae virus agrupados a una trampa de mitigación masiva.'),
    ('hardreset', 'Hard Reset Cósmico (5%)', '5%', '💥', 'Parche de seguridad global que aniquila instantáneamente todas las amenazas del mapa.', 'Limpia el nivel de golpe y otorga bonificación masiva de bytes.')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    effect = EXCLUDED.effect;

-- 7.5 Semilla de Píldoras Vocacionales
INSERT INTO public.vocational_tips (tip_text, category) VALUES
    ('🛡️ ¿Sabías que un Especialista en Ciberseguridad protege infraestructuras críticas como redes eléctricas, satélites y bancos?', 'Ciberseguridad'),
    ('🌐 El protocolo TCP/IP garantiza que los paquetes de datos lleguen íntegros a través de múltiples routers usando checksums y ACKs.', 'Redes'),
    ('🔒 La criptografía de clave pública (RSA / Curvas Elípticas) es la base que protege las compras y contraseñas de todo el planeta.', 'Criptografía'),
    ('🚨 En el modelo "Zero Trust" de ciberseguridad, nunca se confía en ningún dispositivo, incluso si está dentro de la red corporativa.', 'Ciberseguridad'),
    ('💡 La Ingeniería de Sistemas combina Arquitectura de Software, Cloud Computing, Ciberdefensa e Inteligencia Artificial.', 'Ingeniería');

-- ==============================================================================
-- FIN DEL ESQUEMA SUPABASE
-- ==============================================================================
