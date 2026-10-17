"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
MODEL: supabase_client.py
Gestor centralizado de conexión y cliente de Supabase (PostgreSQL / PostgREST).
Soporta tanto claves JWT heredadas como el nuevo formato 'sb_publishable_...'.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List

# Carga de variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Importación segura de Streamlit para leer st.secrets
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Importación de Supabase Client oficial si está disponible
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False
    Client = Any


class SupabaseResponse:
    """Encapsula la respuesta emulando la interfaz de supabase-py."""
    def __init__(self, data: Any):
        self.data = data


class RestQueryBuilder:
    """Constructor fluido de consultas PostgREST REST."""

    def __init__(self, base_url: str, table: str, key: str):
        self.base_url = base_url.rstrip("/")
        self.table = table
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.params: List[tuple] = []
        self._action = "SELECT"
        self._payload: Optional[bytes] = None
        self._extra_headers: Dict[str, str] = {}

    def select(self, cols: str = "*"):
        self._action = "SELECT"
        self.params.append(("select", cols))
        return self

    def order(self, col: str, desc: bool = False):
        direction = "desc" if desc else "asc"
        self.params.append(("order", f"{col}.{direction}"))
        return self

    def limit(self, n: int):
        self.params.append(("limit", str(n)))
        return self

    def eq(self, col: str, val: Any):
        val_str = str(val).lower() if isinstance(val, bool) else str(val)
        self.params.append((col, f"eq.{val_str}"))
        return self

    def insert(self, values: Any):
        self._action = "INSERT"
        self._payload = json.dumps(values).encode("utf-8")
        self._extra_headers["Prefer"] = "return=representation"
        return self

    def upsert(self, values: Any, on_conflict: Optional[str] = None):
        self._action = "UPSERT"
        self._payload = json.dumps(values).encode("utf-8")
        prefer_val = "resolution=merge-duplicates,return=representation"
        self._extra_headers["Prefer"] = prefer_val
        if on_conflict:
            self.params.append(("on_conflict", on_conflict))
        return self

    def execute(self) -> SupabaseResponse:
        query_str = urllib.parse.urlencode(self.params)
        url = f"{self.base_url}/rest/v1/{self.table}"
        if query_str:
            url += f"?{query_str}"

        headers = {**self.headers, **self._extra_headers}
        req = urllib.request.Request(url, data=self._payload, headers=headers)
        if self._action in ("INSERT", "UPSERT"):
            req.method = "POST"

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw) if raw else []
                return SupabaseResponse(data)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            raise Exception(f"HTTP {e.code}: {err_msg}")


class SupabaseRestClient:
    """Cliente PostgREST compatible con el nuevo formato sb_publishable_."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def table(self, table_name: str) -> RestQueryBuilder:
        return RestQueryBuilder(self.url, table_name, self.key)

    def rpc(self, fn_name: str, params: Dict[str, Any]):
        class RpcCaller:
            def __init__(self, client, fn, p):
                self.client = client
                self.fn = fn
                self.p = p

            def execute(self) -> SupabaseResponse:
                body = json.dumps(self.p).encode("utf-8")
                url = f"{self.client.url}/rest/v1/rpc/{self.fn}"
                req = urllib.request.Request(url, data=body, headers=self.client.headers)
                req.method = "POST"
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = resp.read().decode("utf-8")
                        data = json.loads(raw) if raw else None
                        return SupabaseResponse(data)
                except urllib.error.HTTPError as e:
                    err_msg = e.read().decode("utf-8")
                    raise Exception(f"HTTP {e.code}: {err_msg}")

        return RpcCaller(self, fn_name, params)


_supabase_instance: Optional[Any] = None
_connection_attempted: bool = False
_connection_error: Optional[str] = None


def get_supabase_credentials() -> tuple[Optional[str], Optional[str]]:
    """Obtiene la URL y KEY de Supabase desde st.secrets o variables de entorno / .env."""
    url = None
    key = None

    # 1. Intentar desde st.secrets si estamos en contexto Streamlit
    if HAS_STREAMLIT:
        try:
            if "SUPABASE_URL" in st.secrets:
                url = str(st.secrets["SUPABASE_URL"]).strip()
            if "SUPABASE_KEY" in st.secrets:
                key = str(st.secrets["SUPABASE_KEY"]).strip()
        except Exception:
            pass

    # 2. Si no están en st.secrets, buscar en variables de entorno / .env
    if not url:
        raw_url = os.getenv("SUPABASE_URL")
        url = raw_url.strip() if raw_url else None
    if not key:
        raw_key = os.getenv("SUPABASE_KEY")
        key = raw_key.strip() if raw_key else None

    return url, key


def get_supabase_client() -> Optional[Any]:
    """
    Retorna la instancia Singleton del cliente de Supabase.
    Compatible tanto con claves JWT como con las nuevas publishable keys.
    """
    global _supabase_instance, _connection_attempted, _connection_error

    if _supabase_instance is not None:
        return _supabase_instance

    if _connection_attempted and _supabase_instance is None:
        return None

    _connection_attempted = True

    url, key = get_supabase_credentials()
    if not url or not key or "tu-proyecto" in url or "tu-clave" in key:
        _connection_error = "Credenciales SUPABASE_URL y SUPABASE_KEY no configuradas."
        return None

    # Intentar primero con el cliente oficial de Supabase
    if HAS_SUPABASE_LIB:
        try:
            _supabase_instance = create_client(url, key)
            # Prueba de consulta rápida
            _supabase_instance.table("scores").select("id").limit(1).execute()
            _connection_error = None
            return _supabase_instance
        except Exception:
            # Si supabase-py falla (p.ej. por regex estricto de JWT vs publishable key), usar el cliente REST nativo
            _supabase_instance = None

    # Cliente REST nativo de alto rendimiento
    try:
        rest_client = SupabaseRestClient(url, key)
        # Verificar conexión
        rest_client.table("scores").select("id").limit(1).execute()
        _supabase_instance = rest_client
        _connection_error = None
        return _supabase_instance
    except Exception as e:
        _connection_error = str(e)
        _supabase_instance = None
        return None


def is_supabase_connected() -> bool:
    """Verifica si el cliente de Supabase está activo y conectado exitosamente."""
    return get_supabase_client() is not None


def get_supabase_status() -> Dict[str, Any]:
    """Retorna información de diagnóstico sobre la conexión a Supabase."""
    url, key = get_supabase_credentials()
    client = get_supabase_client()
    return {
        "connected": client is not None,
        "has_library": HAS_SUPABASE_LIB,
        "has_url": bool(url),
        "has_key": bool(key),
        "url_masked": f"{url[:16]}..." if url else None,
        "error": _connection_error
    }
