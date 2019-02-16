# Responses

Bocadillo passes the request and the response object to each view, much like
Falcon does.
To send a response, the idiomatic process is to mutate the `res` object directly.

## Sending content

Bocadillo has built-in support for common types of responses:

```python
res.text = 'My awesome post'  # text/plain
res.html = '<h1>My awesome post</h1>'  # text/html
res.media = {'title': 'My awesome post'}  # application/json
```

Setting a response type attribute automatically sets the
appropriate `Content-Type`, as depicted above.

::: tip
The `res.media` attribute serializes values based on the `media_type` configured on the API, which is `application/json` by default. Refer to [Media] for more information.
:::

[media]: media.md

If you need to send another content type, use `.content` and set
the `Content-Type` header yourself:

```python
res.content = 'h1 { color; gold; }'
res.headers['Content-Type'] = 'text/css'
```

## Status codes

You can set the numeric status code on the response using `res.status_code`:

```python{8}
from bocadillo import API

api = API()

@api.route("/jobs")
class Jobs:
    async def post(self, req, res):
        res.status_code = 201
```

::: tip
Bocadillo does not provide an enum of HTTP status codes. If you prefer to
use one, you'd be safe enough going for `HTTPStatus`, located in the standard
library's `http` module.

```python
from http import HTTPStatus
res.status_code = HTTPStatus.CREATED.value
```

:::

## Headers

You can access and modify a response's headers using `res.headers`, which is
a standard Python dictionary object:

```python
res.headers['Cache-Control'] = 'no-cache'
```

## Streaming

Similar to [request streaming](./requests.md#streaming), response content can be streamed to prevent loading a full (potentially large) response body in memory. An example use case may be sending results of a massive database query.

A stream response can be defined by decorating a no-argument [asynchronous generator function][async generators] with `@res.stream`. The generator returned by that function will be used to compose the full response. It should only yield **strings or bytes** (i.e. [media][media] streaming is not supported).

[async generators]: https://www.python.org/dev/peps/pep-0525/#asynchronous-generators

```python{7,8,9,10}
from bocadillo import API

api = API()

@api.route("/range/{n}")
async def number_range(req, res, n):
    @res.stream
    async def large_response():
        for num in range(n):
            yield str(num)
```

::: warning
A stream response is not chunk-encoded by default, which means that clients will still receive the response in one piece. To send the response in chunks, follow the instructions described in [Chunked responses](#chunked-responses).
:::

::: tip
All attributes of the `Response` object — including [res.background](./background-tasks.md) but excluding [content attributes](#sending-content) — can be used along with a stream response.
:::

## Chunked responses

The HTTP/1.1 [Transfer-Encoding] header allows to send an HTTP response in chunks.

This is useful to send large responses, or when the response's total size cannot be known until processing is finished. Plus, it allows the client to process the results as soon as possible.

This is typically combined with [response streaming](#streaming).

```python
res.chunked = True
# equivalent to:
res.headers["transfer-encoding"] = "chunked"
```

[transfer-encoding]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding

## Files and attachments

Sometimes, the response content should be populated from a file and / or you may want to enable the client's browser to trigger a "Save As…" box when receiving it.

This can be achieved via `res.attach()`, a helper method that sets the [Content-Disposition] header for you.

For example, let's create a simple CSV file containing random data:

```python
import csv
from random import random

data = [{"id": i, "value": random()} for i in range(100)]

with open("random.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "value"])

    write.writeheader()
    for item in data:
        writer.writerow(item)
```

Let's send it to the client so that they can download it:

```python
from bocadillo import API

api = API()

@api.route("/random.csv")
async def send_csv(req, res):
    res.attach("random.csv")

if __name__ == "__main__":
    api.run()
```

Run the script and visit `/random.csv`, and your browser should download the CSV file and put it in your downloads folder — or open a "Save As…" dialog, depending on which browser you're using.
