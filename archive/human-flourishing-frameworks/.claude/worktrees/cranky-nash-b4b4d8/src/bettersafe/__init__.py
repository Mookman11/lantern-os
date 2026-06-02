"""BetterSafe pilot package.

Contains bounded modules that support the BetterSafe pilot work
(``sensor_policy`` evaluator, ``release_gate`` evaluator).

This package marker exists so ``import bettersafe`` works once ``src/`` is
on ``sys.path``. ``tests/__init__.py`` performs that path adjustment for
``python -m unittest`` runs.
"""
