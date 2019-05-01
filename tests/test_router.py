import pytest

from bocadillo import App, Router


def test_index_returns_404_by_default(app: App, client):
    assert client.get("/").status_code == 404


def test_if_route_not_registered_then_404(app: App, client):
    assert client.get("/test").status_code == 404


def test_if_route_registered_then_not_404(app: App, client):
    @app.route("/")
    async def index(req, res):
        pass

    assert client.get("/").status_code != 404


def test_default_status_code_is_200_on_routes(app: App, client):
    @app.route("/")
    async def index(req, res):
        pass

    assert client.get("/").status_code == 200


def test_leading_slash_is_added_if_not_present(app: App, client):
    @app.route("foo")
    async def index(req, res):
        pass

    assert client.get("/foo").status_code == 200


def test_trailing_slash_not_redirected(app, client):
    @app.route("/foo")
    async def foo(req, res):
        pass

    assert client.get("/foo/").status_code == 404


@pytest.mark.parametrize(
    "path, status",
    [
        ("/", 404),
        ("/1", 404),
        ("/tacos", 200),
        ("/tacos/", 200),
        ("/tacos/1", 200),
    ],
)
def test_mount_router(app, client, path, status):
    router = Router()

    @router.route("/")
    async def get_tacos(req, res):
        pass

    @router.route("/{pk}")
    async def get_taco(req, res, pk):
        pass

    app.mount("/tacos", router)
    assert client.get(path).status_code == status
