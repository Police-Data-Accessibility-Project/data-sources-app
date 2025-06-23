"""
Dynamic utility functions
"""

from typing import Optional, Any, Callable

from middleware.custom_dataclasses import DeferredFunction


def call_if_not_none(obj: Optional[Any], func: Callable, **kwargs):
    if obj is not None:
        func(**kwargs)


def execute_if_not_none(deferred_function: Optional[DeferredFunction] = None):
    if deferred_function is not None:
        deferred_function.execute()
