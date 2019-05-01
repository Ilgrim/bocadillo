import typing

from starlette.middleware.wsgi import WSGIMiddleware
from starlette.websockets import WebSocketClose

from .app_types import ASGIApp, Receive, Scope, Send
from .errors import HTTPError
from .redirection import Redirect
from .urlparse import Parser
from .views import View
from .websockets import WebSocket, WebSocketView

_V = typing.TypeVar("_V")


def _join(prefix: str, path: str) -> str:
    if path == "/":
        return prefix
    return prefix + path


class BaseRoute(typing.Generic[_V]):
    def matches(self, scope: dict) -> typing.Tuple[bool, dict]:
        raise NotImplementedError

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        raise NotImplementedError


class Patterned(typing.Generic[_V]):
    __slots__ = ("_pattern", "_parser", "view")

    def __init__(self, pattern: str, view: _V):
        self._parser = Parser(pattern)
        self.view = view

    @property
    def pattern(self) -> str:
        return self._parser.pattern


class HTTPRoute(BaseRoute, Patterned[View]):
    def matches(self, scope: Scope) -> typing.Tuple[bool, Scope]:
        if scope["type"] != "http":
            return False, {}
        params = self._parser.parse(scope["path"])
        if params is None:
            return False, {}
        return True, {"path_params": params}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req, res = scope["req"], scope["res"]
        await self.view(req, res, **scope["path_params"])


class WebSocketRoute(BaseRoute, Patterned[WebSocketView]):
    __slots__ = ("ws_kwargs",)

    def __init__(self, pattern: str, view: WebSocketView, **kwargs):
        super().__init__(pattern, view)
        self.ws_kwargs = kwargs

    def matches(self, scope: Scope) -> typing.Tuple[bool, Scope]:
        if scope["type"] != "websocket":
            return False, {}
        params = self._parser.parse(scope["path"])
        if params is None:
            return False, {}
        return True, {"path_params": params}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        ws = WebSocket(scope, receive, send, **self.ws_kwargs)
        await self.view(ws, **scope["path_params"])


class Mount(BaseRoute):
    def __init__(self, path: str, app: ASGIApp):
        if not path.startswith("/"):
            path = "/" + path
        path = path.rstrip("/")

        self.app = app
        self.path = path
        self._parser = Parser(self.path + "/{path}")

    def matches(self, scope: dict) -> typing.Tuple[bool, dict]:
        if scope["path"] in (self.path, self.path + "/"):
            return True, {"path": "/"}
        params = self._parser.parse(scope["path"])
        if params is not None:
            return True, {"path": "/" + params["path"]}
        return False, {}

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except TypeError:
            app = WSGIMiddleware(self.app)
            await app(scope, receive, send)
        finally:
            if not isinstance(self.app, (BaseRoute, Router)):
                scope["response_sent"] = True


class Router:
    __slots__ = ("routes",)

    def __init__(self):
        self.routes: typing.List[BaseRoute] = []

    def add_route(self, route: BaseRoute) -> None:
        self.routes.append(route)

    def include(self, other: "Router", prefix: str = ""):
        """Include the routes of another router."""
        for route in other.routes:
            assert isinstance(route, (HTTPRoute, WebSocketRoute, Mount))
            if prefix:
                if isinstance(route, HTTPRoute):
                    route = HTTPRoute(
                        pattern=_join(prefix, route.pattern), view=route.view
                    )
                elif isinstance(route, WebSocketRoute):
                    route = WebSocketRoute(
                        pattern=_join(prefix, route.pattern),
                        view=route.view,
                        **route.ws_kwargs,
                    )
                elif isinstance(route, Mount):
                    route = Mount(path=_join(prefix, route.path), app=route.app)
            self.add_route(route)

    def mount(self, path: str, app: ASGIApp):
        """Mount an ASGI or WSGI app at the given path."""
        return self.add_route(Mount(path, app))

    def route(self, pattern: str):
        """Register an HTTP route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.
        """

        def decorate(view: typing.Any) -> HTTPRoute:
            if not isinstance(view, View):
                view = View(view)
            route = HTTPRoute(pattern, view)
            self.add_route(route)
            return route

        return decorate

    def websocket_route(
        self,
        pattern: str,
        *,
        auto_accept: bool = True,
        value_type: str = None,
        receive_type: str = None,
        send_type: str = None,
        caught_close_codes: typing.Tuple[int] = None,
    ):
        """Register a WebSocket route by decorating a view.

        See #::bocadillo.websockets#WebSocket for a description of keyword
        parameters.

        # Parameters
        pattern (str): an URL pattern.
        """

        def decorate(view: typing.Any) -> WebSocketRoute:
            view = WebSocketView(view)
            route = WebSocketRoute(
                pattern,
                view,
                auto_accept=auto_accept,
                value_type=value_type,
                receive_type=receive_type,
                send_type=send_type,
                caught_close_codes=caught_close_codes,
            )
            self.add_route(route)
            return route

        return decorate

    def _find_route(self, scope: dict) -> typing.Optional[BaseRoute]:
        for route in self.routes:
            matches, child_scope = route.matches(scope)
            if matches:
                scope.update(child_scope)
                return route
        return None

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        route = self._find_route(scope)

        if route is not None:
            try:
                await route(scope, receive, send)
            except Redirect as exc:
                scope["res"] = exc.response

        elif scope["type"] == "websocket":
            await WebSocketClose(code=403)(receive, send)

        else:
            raise HTTPError(404)
