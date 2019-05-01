import pytest

from bocadillo import App


@pytest.mark.parametrize("path", ["/other", "/other/", "/other/foo"])
def test_mount(app: App, client, path):
    other = App()

    @other.route("/")
    async def index(req, res):
        pass

    @other.route("/foo")
    async def foo(req, res):
        pass

    app.mount("/other", other)

    r = client.get(path)
    assert r.status_code == 200
