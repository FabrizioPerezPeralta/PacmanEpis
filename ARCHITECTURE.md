# 🏛️ ARQUITECTURA DE SOFTWARE MVC & STREAMLIT
## SYS-ENGINEER ARCADE 198X // CYBER PACKET (PAC-MAN)

Este proyecto implementa formalmente el patrón arquitectónico **Modelo-Vista-Controlador (MVC)** para el despliegue web reactivo utilizando **Streamlit**, enfocado exclusivamente en la simulación interactiva **Cyber Packet** (Pac-Man de Ciberseguridad & Redes TCP/IP).

---

## 1. DIAGRAMA ARQUITECTÓNICO MVC

```
                    +------------------------------------+
                    |             USUARIO /              |
                    |        NAVEGADOR STREAMLIT         |
                    +-----------------+------------------+
                                      |
                      Acciones y      | Visualización y
                      Controles       | Telemetría
                                      v
+------------------------------------------------------------------------+
|                      CONTROLADOR (controllers/)                        |
|  - GameController: Orquesta el ciclo de vida, estado de sesión de     |
|    Streamlit (st.session_state), créditos, dificultad y persistencia.  |
+---------------------+----------------------------+---------------------+
                      |                            |
       Consulta y     | Sincronización             | Envío de datos
       Actualización  v                            v para Renderizado
+------------------------------------+  +--------------------------------+
|          MODELO (models/)          |  |         VISTA (views/)         |
|                                    |  |                                |
|  • GameModel:                      |  |  • ArcadeView:                 |
|    - Récords y Leaderboard         |  |    - Mueble Arcade CRT         |
|    - Persistencia (highscores.json)|  |    - Shader Scanlines 60 FPS   |
|    - Presets de Dificultad SecOps  |  |    - D-Pad Táctil y Teclado    |
|    - Tips de Vocación en Sistemas  |  |    - Motor CyberPacketGame     |
|                                    |  |                                |
|  • ThreatModel:                    |  |  • DashboardView:              |
|    - Catálogo de 5 Virus Cazadores |  |    - Métricas de Seguridad     |
|    - Tokens de Firewall (Poderes)  |  |    - Matriz de Amenazas Ofens. |
|    - Consejos Reales de Mitigación |  |    - Arsenal de Contramedidas  |
|                                    |  |    - Salón de la Fama          |
+------------------------------------+  +--------------------------------+
```

---

## 2. ESTRUCTURA LIMPIA DEL PROYECTO

```
GameConsole/
├── .streamlit/
│   ├── config.toml          # Configuración de tema oscuro y servidor Streamlit
│   └── secrets.toml.example # Plantilla de secretos para Supabase
├── models/
│   ├── __init__.py          # Exporta GameModel, ThreatModel y clientes Supabase
│   ├── supabase_client.py   # Gestor de conexión y diagnóstico de Supabase
│   ├── game_model.py        # Modelo híbrido: Supabase Cloud + Fallback local JSON
│   ├── threat_model.py      # Catálogo dinámico de ciberamenazas y tokens
│   └── api_server.py        # Servidor REST local multihilo (puerto 8502)
├── views/
│   ├── __init__.py          # Exporta ArcadeView y DashboardView
│   ├── arcade_view.py       # Renderizado del mueble Arcade CRT (HTML5/Canvas + Sync Supabase)
│   └── dashboard_view.py    # Renderizado de telemetría y tarjetas educativas
├── controllers/
│   ├── __init__.py          # Exporta GameController
│   └── game_controller.py   # Controlador principal y gestión de sesión
├── static/
│   ├── css/
│   │   └── arcade.css       # Estilos retro CRT, scanlines y bisel de gabinete
│   └── js/
│       ├── BaseGame.js       # Template Method para Game Loops en Canvas
│       ├── AudioService.js   # Síntesis chiptune de sonido con Web Audio API
│       └── CyberPacketGame.js# Motor Pac-Man: 100 laberintos, 5 virus, superpoderes
├── app.py                   # Punto de entrada principal para Streamlit
├── requirements.txt         # Dependencias (streamlit, supabase, python-dotenv)
├── supabase_schema.sql      # Script SQL completo (Tablas, RLS, RPCs, Índices y Seed)
├── .env.example             # Variables de entorno de ejemplo para Supabase
├── highscores.json          # Almacén de respaldo local (fallback sin conexión)
└── ARCHITECTURE.md          # Documentación formal de la arquitectura
```

---

## 3. COMPONENTES DEL MODELO-VISTA-CONTROLADOR

### 🧠 MODELO (`models/`)
- **Desacoplamiento Total:** No contiene ninguna referencia a Streamlit ni a elementos de interfaz gráfica.
- **`supabase_client.py`:**
  - Instancia Singleton segura del cliente de Supabase.
  - Soporta lectura desde `.streamlit/secrets.toml` y variables de entorno `.env`.
  - Fallback automático si las claves no están presentes.
- **`game_model.py`:**
  - Persistencia Híbrida: Conexión con Supabase (`scores`, `players`, `v_top_5`) y respaldo en `highscores.json`.
  - Provee presets de dificultad: *Novato (Junior Dev)*, *Normal (SecOps Standard)* y *Hardcore (Red Team Attack)*.
  - Ofrece cápsulas de conocimiento vocacional sobre Ingeniería de Sistemas.
- **`threat_model.py`:**
  - Cataloga las 5 amenazas cibernéticas: *Ransomware, Phishing, Spyware, Trojan y Malware Polimórfico*.
  - Cataloga los 4 tokens de firewall: *Antivirus Endpoint, Cyber Sniper, DDoS Sinkhole y Hard Reset*.

### 🖥️ VISTA (`views/`)
- **`arcade_view.py`:**
  - Construye el componente web interactivo e inyecta la pantalla retro CRT dentro de Streamlit mediante `st.components.v1.html`.
  - Sincroniza puntajes en tiempo real tanto con Supabase PostgREST RPC como con el servidor API local.
  - Dispone de controles adaptados a teclado físico y a pantallas táctiles mediante un D-Pad virtual.
- **`dashboard_view.py`:**
  - Renderiza paneles de métricas de red, la matriz de amenazas ofensivas con su contraparte defensiva, y la tabla de clasificación.

### 🎮 CONTROLADOR (`controllers/`)
- **`game_controller.py`:**
  - Maneja `st.session_state` para mantener el estado de la aplicación durante re-renderizados reactivos de Streamlit.
  - Monitorea el estado de persistencia (Supabase Cloud 🟢 o Local JSON 🟡).
  - Gestiona la inserción de créditos/fichas virtuales.
  - Aplica los ajustes de dificultad sobre el motor de juego.
  - Procesa el registro de nuevos récords mundiales en el modelo.

---

## 4. CÓMO EJECUTAR Y CONFIGURAR SUPABASE

### Paso 1: Configurar la Base de Datos en Supabase
1. Ingresa a [supabase.com](https://supabase.com) y crea un nuevo proyecto.
2. Ve a la sección **SQL Editor**.
3. Pega el contenido íntegro del archivo [`supabase_schema.sql`](file:///C:/Users/chara/Documents/GameConsole/supabase_schema.sql) y presiona **Run**.
4. Esto creará automáticamente las tablas (`players`, `scores`, `threats`, `firewall_tokens`, `vocational_tips`), las vistas (`v_top_5`, `v_leaderboard`), las políticas RLS y los datos iniciales.

### Paso 2: Configurar las Credenciales
Crea el archivo `.streamlit/secrets.toml` o copia `.env.example` a `.env`:
```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-anon-key-aqui"
```

### Paso 3: Ejecutar en Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Paso 4: Despliegue en la Nube (Streamlit Community Cloud):
1. Sube el repositorio a GitHub.
2. Despliega en [share.streamlit.io](https://share.streamlit.io).
3. En la configuración de la app en Streamlit Cloud, ve a **Settings > Secrets** y pega las mismas variables `SUPABASE_URL` y `SUPABASE_KEY`.
