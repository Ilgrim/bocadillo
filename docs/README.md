---
home: true
heroImage: /social-image.png
actionText: Get Started →
actionLink: /getting-started/
features:
  - title: Simple and productive
    details: A minimal setup and carefully chosen included batteries help you solve common (and more advanced) problems in no time.
  - title: Async-first
    details: Embrace modern Python asynchronous programming capabilities! Don't worry, though — it's all optional.
  - title: Performant
    details: Built on Starlette and Uvicorn, the lightning-fast Python ASGI toolkit and server.
footer: MIT Licensed | Copyright © 2018-present Florimond Manca
---

## Quick start

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# app.py
from bocadillo import App, Templates

app = App()
templates = Templates(app)

@app.route("/")
async def index(req, res):
    # Use a template from the ./templates directory
    res.html = await templates.render("index.html")

@app.route("/greet/{person}")
async def greet(req, res, person):
    res.media = {"message": f"Hi, {person}!"}

if __name__ == "__main__":
    app.run()
```

Launch:

```bash
python app.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? Head to our [Getting Started](./getting-started/README.md) guide!
