---
title: "Bocadillo 0.14 released!"
description: "TypeSystem for JSON data, route and query parameter validation, standard app configuration, Bocadillo CLI, plugin framework, and more!"
date: 2019-04-XX
author: Florimond Manca
layout: Post
---

We're excited to anounce that Bocadillo v0.14 is out! This release contains important changes to how applications are structured and run, as well as exciting new features that make working with Bocadillo even more productive.

::: warning IMPORTANT
Note: this release is **incompatible with 0.13 and earlier**. Implementing the new features required breaking some of the main API. You'll find tips on migrating from 0.13.x in this post.
:::

[[toc]]

## All async

What. Why. Which items are impacted. Link to docs.

## Application settings

Settings module. Plugins and removed app parameters. You must now call configure(). Before/after (app parameters vs settings). Use Bocadillo CLI to simplify your workflow. Accessing settings. Link to docs.

## Use uvicorn to serve apps

`app.run()` and debug mode gone. Just use uvicorn. Before/after.

## Data validation

Use TypeSystem to validate JSON. Working example. Works well with `orm` too. Link to docs.

## Route and query parameters

Validation using type annotations. Useful shortcuts, but any Typesystem field will do. Format specifier not supported anymore.

Query parameter injection. Define a view parameter with a default to get it from the query string. Validation works just like route parameters.

## Removed features

Why. Media is gone. Use `res.json` instead. Named routes and URL reversion (`url_for()`) are gone. Before/after. `app.client` is gone (deprecated in 0.13).

## Error handling

Re-raising errors in error handlers is now supported.

## Redirects

Redirect using the `Redirect` exception. Before/after.

## Performance

Slots. Benchmarks?

If you have any questions, feel free to [get in touch](/faq/#getting-in-touch)!
