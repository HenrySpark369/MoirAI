"""
Middleware de Rate Limiting Global
Protección contra abuso y control de acceso a recursos
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from collections import defaultdict
from threading import Lock
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from app.core.config import settings

logger = logging.getLogger(__name__)
from app.core.config import settings


class RateLimitConfig:
    """Configuración de límites de tasa por rol de usuario"""

    # Límites por rol (requests / hora)
    # Límites por rol (requests / hora)
    LIMITS_PER_ROLE = {
        "admin": settings.RATE_LIMIT_ADMIN,
        "company": settings.RATE_LIMIT_COMPANY,
        "student": settings.RATE_LIMIT_STUDENT,
        "anonymous": settings.RATE_LIMIT_ANONYMOUS,
    }

    # Límites específicos por endpoint (requests / minuto)
    ENDPOINT_LIMITS = {
        # Auth endpoints - muy restrictivos
        "POST /api/v1/auth/login": 200,  # Aumentado de 5 a 10
        "POST /api/v1/auth/register": 100,
        "POST /api/v1/auth/api-keys": 400,

        # Matching endpoints - moderado
        "POST /api/v1/matching/recommendations": 600,
        "POST /api/v1/matching/filter-by-criteria": 300,
        "GET /api/v1/matching/featured-students": 100,

        # Student endpoints
        "GET /api/v1/students": 200,
        "POST /api/v1/students": 100,
        "POST /api/v1/students/upload_resume": 500,  # Límite específico para upload de CV
        "PUT /api/v1/students/{id}": 200,
        "DELETE /api/v1/students/{id}": 500,

        # Job scraping - respetar límites de OCC
        "GET /api/v1/jobs/search": 200,
        "POST /api/v1/jobs/apply": 300,

        # Companies
        "GET /api/v1/companies": 200,
        "POST /api/v1/companies": 500,

        # Default para otros endpoints
        "DEFAULT": 200,
    }

    # Ventanas de tiempo
    HOURLY_WINDOW = settings.RATE_LIMIT_WINDOW_SECONDS  # segundos
    MINUTE_WINDOW = 60    # segundos


class RateLimiter:
    """
    Limitador de tasa global basado en memoria.
    
    **Características:**
    - ✅ Límites por rol de usuario
    - ✅ Límites específicos por endpoint
    - ✅ Límites por IP para usuarios anónimos
    - ✅ Ventanas deslizantes (sliding window)
    - ✅ Sincronización thread-safe
    
    **Nota:** Para producción con múltiples servidores, usar Redis.
    """

    def __init__(self):
        """Inicializar el limitador de tasa"""
        # Almacenar requests: {key: [(timestamp, method), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
        logger.info("🔒 Rate Limiter inicializado")

    def _get_rate_limit_key(self, request: Request, user_role: Optional[str]) -> str:
        """
        Generar clave única para el limitador.

        Args:
            request: Objeto de request de FastAPI
            user_role: Rol del usuario (None para anónimo)

        Returns:
            Clave única identificando el cliente
        """
        if user_role and user_role != "anonymous":
            # Para usuarios autenticados: usar IP + rol
            client_ip = self._get_client_ip(request)
            return f"{client_ip}:{user_role}"
        else:
            # Para anónimos: solo IP
            return self._get_client_ip(request)

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        Obtener IP del cliente considerando proxies.

        Args:
            request: Objeto de request

        Returns:
            IP del cliente
        """
        # Considerar headers de proxy
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            return request.headers["x-real-ip"]
        else:
            return request.client.host if request.client else "unknown"

    def _get_endpoint_key(self, request: Request) -> str:
        """
        Generar clave del endpoint para límites específicos.

        Args:
            request: Objeto de request

        Returns:
            Clave del endpoint (e.g., "GET /api/v1/students")
        """
        method = request.method
        path = request.url.path

        # Intentar coincidir con patrones definidos
        for pattern in RateLimitConfig.ENDPOINT_LIMITS.keys():
            if pattern == "DEFAULT":
                continue
            # Patrón simple: method + path prefix
            pattern_parts = pattern.split(" ")
            if len(pattern_parts) == 2:
                pattern_method, pattern_path = pattern_parts
                if method == pattern_method and path.startswith(pattern_path.rstrip("/")):
                    return pattern

        return "DEFAULT"

    def _get_limit_for_role(self, user_role: Optional[str]) -> int:
        """
        Obtener límite horario para un rol.

        Args:
            user_role: Rol del usuario

        Returns:
            Límite de requests por hora
        """
        return RateLimitConfig.LIMITS_PER_ROLE.get(
            user_role or "anonymous",
            RateLimitConfig.LIMITS_PER_ROLE["anonymous"]
        )

    def _get_limit_for_endpoint(self, endpoint_key: str) -> int:
        """
        Obtener límite por minuto para un endpoint.

        Args:
            endpoint_key: Clave del endpoint

        Returns:
            Límite de requests por minuto
        """
        return RateLimitConfig.ENDPOINT_LIMITS.get(
            endpoint_key,
            RateLimitConfig.ENDPOINT_LIMITS.get("DEFAULT", 200)
        )

    def _clean_old_requests(self, key: str, now: datetime) -> None:
        """
        Limpiar requests antiguos de la ventana de tiempo.

        Args:
            key: Clave del cliente
            now: Timestamp actual
        """
        cutoff_hourly = now - timedelta(seconds=RateLimitConfig.HOURLY_WINDOW)
        cutoff_minute = now - timedelta(seconds=RateLimitConfig.MINUTE_WINDOW)

        # Mantener solo requests recientes
        self._requests[key] = [
            (ts, method) for ts, method in self._requests[key]
            if ts > cutoff_hourly or ts > cutoff_minute
        ]

    def check_rate_limit(
        self,
        request: Request,
        user_role: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        Verificar si se ha excedido el límite de tasa.

        Args:
            request: Objeto de request de FastAPI
            user_role: Rol del usuario (None para anónimo)

        Returns:
            Tupla (permitido, mensaje_error, info_limite)
        """
        with self._lock:
            now = datetime.utcnow()

            # Generar claves
            rate_limit_key = self._get_rate_limit_key(request, user_role)
            endpoint_key = self._get_endpoint_key(request)

            # Limpiar requests antiguos
            self._clean_old_requests(rate_limit_key, now)

            # Contar requests en ventanas de tiempo
            hourly_requests = len(self._requests[rate_limit_key])

            minute_requests = len([
                (ts, method) for ts, method in self._requests[rate_limit_key]
                if ts > (now - timedelta(seconds=RateLimitConfig.MINUTE_WINDOW))
            ])

            # Obtener límites
            hourly_limit = self._get_limit_for_role(user_role)
            minute_limit = self._get_limit_for_endpoint(endpoint_key)

            # Convertir límite horario a límite por minuto promedio
            hourly_to_minute_limit = max(1, hourly_limit // 60)

            # Registrar request actual
            self._requests[rate_limit_key].append((now, request.method))

            # Verificar límites
            info = {
                "rate_limit_key": rate_limit_key,
                "endpoint": f"{request.method} {request.url.path}",
                "hourly_limit": hourly_limit,
                "hourly_requests": hourly_requests,
                "minute_limit": minute_limit,
                "minute_requests": minute_requests,
                "user_role": user_role or "anonymous",
            }

            # Verificación 1: Límite por minuto para el endpoint
            if minute_requests > minute_limit:
                return False, (
                    f"Límite de {minute_limit} requests/minuto excedido para este endpoint. "
                    f"Intentos actuales: {minute_requests}"
                ), info

            # Verificación 2: Límite por hora para el rol
            if hourly_requests > hourly_limit:
                return False, (
                    f"Límite de {hourly_limit} requests/hora excedido para tu rol. "
                    f"Intentos actuales: {hourly_requests}"
                ), info

            return True, None, info

    def get_remaining_requests(
        self,
        request: Request,
        user_role: Optional[str] = None
    ) -> Dict:
        """
        Obtener información de requests restantes.

        Args:
            request: Objeto de request
            user_role: Rol del usuario

        Returns:
            Diccionario con información de límite
        """
        rate_limit_key = self._get_rate_limit_key(request, user_role)
        now = datetime.utcnow()

        hourly_requests = len([
            ts for ts, _ in self._requests[rate_limit_key]
            if ts > (now - timedelta(seconds=RateLimitConfig.HOURLY_WINDOW))
        ])

        minute_requests = len([
            ts for ts, _ in self._requests[rate_limit_key]
            if ts > (now - timedelta(seconds=RateLimitConfig.MINUTE_WINDOW))
        ])

        hourly_limit = self._get_limit_for_role(user_role)
        endpoint_key = self._get_endpoint_key(request)
        minute_limit = self._get_limit_for_endpoint(endpoint_key)

        return {
            "hourly": {
                "limit": hourly_limit,
                "used": hourly_requests,
                "remaining": max(0, hourly_limit - hourly_requests),
            },
            "per_minute": {
                "limit": minute_limit,
                "used": minute_requests,
                "remaining": max(0, minute_limit - minute_requests),
            }
        }

    def reset_for_user(self, rate_limit_key: str) -> None:
        """
        Resetear contadores para un usuario específico (admin).

        Args:
            rate_limit_key: Clave del usuario
        """
        with self._lock:
            if rate_limit_key in self._requests:
                del self._requests[rate_limit_key]
            logger.info(f"🔓 Límites reseteados para: {rate_limit_key}")

    def reset_all(self) -> None:
        """Resetear todos los contadores (admin)"""
        with self._lock:
            self._requests.clear()
            logger.info("🔓 Todos los límites de tasa han sido reseteados")

    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del rate limiter.

        Returns:
            Diccionario con estadísticas
        """
        with self._lock:
            total_keys = len(self._requests)
            total_requests = sum(len(reqs) for reqs in self._requests.values())

            return {
                "total_tracked_clients": total_keys,
                "total_requests_tracked": total_requests,
                "average_requests_per_client": (
                    total_requests // total_keys if total_keys > 0 else 0
                ),
            }


# Instancia global del rate limiter
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """
    Obtener instancia global del rate limiter.

    Returns:
        Instancia de RateLimiter

    **Uso:**
    ```python
    from app.middleware.rate_limit import get_rate_limiter

    limiter = get_rate_limiter()
    is_allowed, error_msg, info = limiter.check_rate_limit(request, user_role)
    ```
    """
    return rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware global para rate limiting.
    Intercepta todos los requests y verifica límites según rol e IP.
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Determinar rol del usuario
        user_role = "anonymous"
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
                user_role = payload.get("role", "anonymous")
            except JWTError:
                # Token inválido -> tratar como anónimo
                pass
        
        # 2. Verificar límite
        limiter = get_rate_limiter()
        is_allowed, error_msg, info = limiter.check_rate_limit(request, user_role)
        
        if not is_allowed:
            # Retornar 429 Too Many Requests
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": error_msg,
                    "details": {
                        "retry_after": 60,  # Sugerencia simple
                        "limit_info": info
                    }
                }
            )
            
        # 3. Continuar si es permitido
        response = await call_next(request)
        return response
