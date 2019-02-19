# bocadillo.middleware

## Middleware
```python
Middleware(self, app: bocadillo.app_types.HTTPApp, **kwargs)
```
Base class for middleware classes.

__Parameters__

- __app__: a callable that may as well be another `Middleware` instance.
- __kwargs (any)__:
    Keyword arguments passed when registering the
    middleware on the application.

### before_dispatch
```python
Middleware.before_dispatch(self, req: bocadillo.request.Request, res: bocadillo.response.Response) -> Union[bocadillo.response.Response, NoneType]
```
Perform processing before a request is dispatched.

If the `Response` object is returned, it will be used
and no further processing will be performed.

__Parameters__

- __req (Request)__: a Request object.
- __res (Response)__: a Response object.

__Returns__

`res (Response or None)`: an optional response object.

### after_dispatch
```python
Middleware.after_dispatch(self, req: bocadillo.request.Request, res: bocadillo.response.Response) -> Union[bocadillo.response.Response, NoneType]
```
Perform processing after a request has been dispatched.

__Parameters__

- __req (Request)__: a Request object.
- __res (Response)__: a Response object.

__Returns__

`res (Response or None)`: an optional response object.

### process
```python
Middleware.process(self, req: bocadillo.request.Request, res: bocadillo.response.Response) -> bocadillo.response.Response
```
Process an incoming request.

- Call `before_dispatch()`. If a response is returned here, no
further processing is performed.
- Call the underlying HTTP `app`.
- Call `after_dispatch()`.
- Return the response.

Note: this is aliased to `__call__()`, which means middleware
instances are callable.

__Parameters__

- __req (Request)__: a Request object.
- __res (Response)__: a Response object.

__Returns__

`res (Response)`: a Response object.

