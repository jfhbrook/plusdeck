# Development

This section has some *very* light notes on how I'm managing development for this library.

I use `uv` for managing dependencies, but also compile `requirements.txt` and `requirements_dev.txt` files that one can use instead. I also use `just` for task running, but if you don't have it installed you can run the commands manually.

This library has somewhat comprehensive unit test coverage through `pytest`. Additionally, it has an interactive integration test suite, using a bespoke test framework, which can be run with `just integration`.
