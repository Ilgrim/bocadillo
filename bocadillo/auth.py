import inspect
import typing

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse

from .config import settings
from .errors import HTTPError
from .plugins import plugin

AuthResult = typing.Optional[typing.Tuple[AuthCredentials, BaseUser]]


@plugin
def use_authentication(app: "App"):
    backend = MultiAuth()
    if not backend.backends:
        return
    app.add_asgi_middleware(AuthMiddleware, backend=backend)


async def authenticate(conn: HTTPConnection, **kwargs) -> AuthResult:
    backend = MultiAuth()
    return await backend.authenticate(conn, **kwargs)


class AuthMiddleware(AuthenticationMiddleware):
    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: AuthenticationError):
        return JSONResponse(
            HTTPError(401, detail=str(exc)).as_json(), status_code=401
        )


def _ensure_instance(obj: typing.Any, *args, **kwargs) -> typing.Any:
    return obj(*args, **kwargs) if inspect.isclass(obj) else obj


class MultiAuth(AuthenticationBackend):
    def __init__(self, backends: typing.Sequence[AuthenticationBackend] = None):
        if backends is None:
            backends = settings.get("AUTH_BACKENDS", [])
        self.backends = [_ensure_instance(backend) for backend in backends]

    async def authenticate(self, conn: HTTPConnection, **kwargs) -> AuthResult:
        for backend in self.backends:
            sig = inspect.signature(backend.authenticate)
            try:
                sig.bind(conn, **kwargs)
            except TypeError:
                continue

            try:
                auth_result = await backend.authenticate(conn, **kwargs)
            except AuthenticationError:
                break

            if auth_result is None:
                continue

            return auth_result

        raise AuthenticationError(
            "Could not authenticate with the provided credentials"
        )


class ModelAuth(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
        *,
        username: str = None,
        password: str = None,
        **kwargs: typing.Any
    ) -> AuthResult:
        if username is None:
            username = self.get_default_username(**kwargs)
        user = await self.get_user(username)
        if not self.check_password(user, password):
            return None
        return AuthCredentials(["authenticated"]), user

    def get_default_username(self, **kwargs: typing.Any):
        raise NotImplementedError

    async def get_user(self, username: str) -> BaseUser:
        raise NotImplementedError

    def check_password(self, user: BaseUser, password: str) -> bool:
        return user.check_password(password)
