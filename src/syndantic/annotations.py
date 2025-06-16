"""Annotations for productions.

Grammar productions are represented as
data-classes or ``pydantic`` models.
In this module we define additional metadata
annotations for things we cannot simply express
through type annotations or ``pydantic`` fields.
"""

from collections.abc import Collection
from dataclasses import dataclass
from typing import Annotated, Doc

__all__: list[str] = [
    "ByValue",
    "Expected",
]


@dataclass(frozen=True)
class ByValue:
    """Validate a token's value rather than its image."""

    strict: Annotated[
        bool,
        Doc("""
        If ``False`` apply value only if not ``None``,
        if ``True`` pass value in any case.
        """),
    ] = False


@dataclass(frozen=True)
class Expected:
    """Specify expectations about the token to match."""

    kind: Annotated[
        Collection[str | None] | None,
        Doc("""List of all allowed token kinds."""),
    ] = None
