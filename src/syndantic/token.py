"""Interface of the token."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, TypeAlias


@dataclass
class Token:
    """Token as returned by a tokenizer."""

    image: str  # REQUIRED

    def get_kind(self) -> str | None:
        """The token kind.

        The return value ``None`` indicates
        that no kind has been determined.
        """

    def get_value(self) -> Any | None:
        """The token value.

        The return value ``None`` indicates
        that no token value has been determined.

        The value may be a semantic or at least
        simplified or normalized value corresponding
        to the token.
        """

    def get_begin_line(self) -> int | None:
        """The line number of the first character.

        The return value ``None`` indicates
        that the line number of the token position
        has not been tracked.

        If an integer is returned it should start
        with line number ``1``.
        """

    def get_end_line(self) -> int | None:
        """The line number of the last character.

        The return value ``None`` indicates
        that the line number of the token position
        has not been tracked.

        If an integer is returned it should start
        with line number ``1``.
        """

    def get_begin_column(self) -> int | None:
        """The column number of the first character.

        The return value ``None`` indicates
        that the column number of the token position
        has not been tracked.

        If an integer is returned it should start
        with column number ``1``.
        """

    def get_end_column(self) -> int | None:
        """The column number of the last character.

        The return value ``None`` indicates
        that the column number of the token position
        has not been tracked.

        If an integer is returned it should start
        with column number ``1``.
        """

    def get_position(self) -> int | None:
        """The character number of the first character.

        The return value ``None`` indicates
        that the character number of the token position
        has not been tracked.

        If an integer is returned it should start
        with character number ``0``.
        """

    def get_special(self) -> "Token" | None:
        """Points to the previous special token.

        Special tokens are scanned but not yielded
        by the tokenizer directly.
        Instead, special tokens are collected as
        a linked list together with the following
        regular token.
        """


@dataclass
class SimpleToken(Token):
    """Token as returned by a tokenizer."""

    kind: str | None = None
    begin_line: int | None = None
    begin_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None
    position: int | None = None
    special: Token | None = None

    def get_kind(self) -> str | None:
        """The token kind.

        The return value ``None`` indicates
        that no kind has been determined.
        """
        return self.kind

    def get_begin_line(self) -> int | None:
        """The line number of the first character.

        The return value ``None`` indicates
        that the line number of the token position
        has not been tracked.

        If an integer is returned it should start
        with line number ``1``.
        """
        return self.begin_line

    def get_begin_column(self) -> int | None:
        """The column number of the first character.

        The return value ``None`` indicates
        that the column number of the token position
        has not been tracked.

        If an integer is returned it should start
        with column number ``1``.
        """
        return self.begin_column

    def get_end_line(self) -> int | None:
        """The line number of the last character.

        The return value ``None`` indicates
        that the line number of the token position
        has not been tracked.

        If an integer is returned it should start
        with line number ``1``.
        """
        return self.end_line

    def get_end_column(self) -> int | None:
        """The column number of the last character.

        The return value ``None`` indicates
        that the column number of the token position
        has not been tracked.

        If an integer is returned it should start
        with column number ``1``.
        """
        return self.end_column

    def get_position(self) -> int | None:
        """The character number of the first character.

        The return value ``None`` indicates
        that the character number of the token position
        has not been tracked.

        If an integer is returned it should start
        with character number ``0``.
        """
        return self.position

    def get_special(self) -> "Token" | None:
        """Points to the previous special token.

        Special tokens are scanned but not yielded
        by the tokenizer directly.
        Instead, special tokens are collected as
        a linked list together with the following
        regular token.
        """
        return self.special


Tokenizer: TypeAlias = Iterator[Token]
