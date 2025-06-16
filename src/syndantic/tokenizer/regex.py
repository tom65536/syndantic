"""Tokenizer using the ``regex`` library.

The API is heavily inspired by the lexer behind
[JavaCC](https://javacc.github.io/javacc/).

Note, that this implementation has not been optimized
for speed.
"""

import abc
import re
from collections.abc import Collection, Iterator
from enum import StrEnum, auto
from typing import (
    Annotated,
    Any,
    Doc,
    Literal,
    TypeAlias,
)

import regex
from pydantic import (
    BaseModel,
    Field,
    ImportString,
    PlainValidator,
)

from ..token import Token


def regex_validator(_value: Any) -> str:
    try:
        pat = str(_value)
        _ = regex.compile(pat)
        return pat
    except Exception:
        raise ValueError(f"Not a valid pattern {pat!r}.")


StateName: TypeAlias = str
Priority: TypeAlias = int


class StateTransition(StrEnum):
    """Supported State Trnsitions."""

    SWITCH = auto()
    PUSH = auto()
    POP = auto()
    STASH = auto()
    SWAP = auto()

    def apply(
        self,
        state: str,
        to: str | None,
        stack: list[str],
    ) -> str:
        """Apply the transition.

        Return the new state, modifies the stack.
        """
        match self:
            case StateTransition.SWITCH:
                return state if to is None else to
            case StateTransition.PUSH:
                stack.append(state)
                return state if to is None else to
            case StateTransition.POP:
                return stack.pop()
            case StateTransition.STASH:
                stack.append(state if to is None else to)
                return state
            case StateTransition.SWAP:
                current = stack.pop()
                stack.append(state if to is None else to)
                return current


class BaseTokenizerDefinition(BaseModel, abc.ABC):
    """Common model for all token definitions."""

    regexp_spec: Annotated[
        str,
        PlainValidator(regex_validator),
    ]  # REQUIRED

    kind: Annotated[
        str | None,
        Field(
            title="Token Kind",
            description="the `kind` field of the token",
        ),
    ] = None

    states: Annotated[
        list[StateName] | None,
        Field(
            title="States",
            description="""
            List of lexical states
            where this definition applies.
            The initial state is denoted by the
            string `"DEFAULT"`.
            - `None`: all states
            - `[]`: no states
            - `['DEFAULT']`: initial state only
            """,
        ),
    ] = None

    transition: Annotated[
        StateTransition,
        Field(
            title="Transition Kind",
            description="""
            Defines the way the state transition
            should be carried out.

            -   SWTCH to the next state,
                discard the current state
            -   PUSH the current state before switching
            -   POP the next state from the stack
                (ignore `to`)
            -   STASH the state `to` to the stack,
                do not change the current state
            -   SWAP stack element with current state
                (current=pop, push `to`)
            """,
        ),
    ] = StateTransition.SWITCH

    to: Annotated[
        StateName | None,
        Field(
            title="State for Transition",
            description="""
            Use the given state as argument of the
            transition of the current state if set
            to `None`.
            """,
        ),
    ] = None

    factory: Annotated[
        ImportString,
        Field(
            title="Token Factory",
            description="""
            a class or function returning a `Token`
            and accepting the following
            arguments:
            - `image` (str, mandatory)
            - `kind` (str or None)
            - `special` (Token or None)
            - `position` (int or None)
            - `begin_line` (int or None)
            - `end_line` (int or None)
            - `begin_column` (int or None)
            - `end_column` (int or None)

            Change this, for example, to provide
            a custom `get_value` method or to implement
            custom lexer actions.

            Returning None means that the token
            construction failed (e.g. due to
            programmatic constraints).
            """,
        ),
    ] = "syndantic.token:SimpleToken"

    ignore_case: bool = False

    priority: Annotated[
        Priority,
        Field(
            title="Rule Priority",
            description="""
            Rules with higher (bigger) priority
            are matched first.
            Rules with the same priority try to
            match the longest match.
            """,
        ),
    ] = 0

    force_run_factory: Annotated[
        bool,
        Field(
            title="Force Factory Run",
            description="run the factor method",
        ),
        Doc("""
        For SKIP and MORE token definitions the
        factory function is not invoked unless rhis
        flag is set to true.
        """),
    ] = False


class Skip(BaseTokenizerDefinition):
    """Token definition for tokens to be skipped."""

    is_a: Literal["SKIP"] = "SKIP"


class More(BaseTokenizerDefinition):
    """Token definition for tokens to be skipped."""

    is_a: Literal["MORE"] = "MORE"


class Special(BaseTokenizerDefinition):
    """Token definition for tokens to be skipped."""

    is_a: Literal["SPECIAL"] = "SPECIAL"


class Tok(BaseTokenizerDefinition):
    """Token definition for tokens to be skipped."""

    is_a: Literal["TOKEN"] = "TOKEN"


TokenizerDefinition: TypeAlias = Annotated[
    Skip | More | Special | Tok,
    Field(discriminator="is_a"),
]


class RegexTokenizer:
    """Tokenizer based on regular expressions."""

    def __init__(
        self,
        *definitions: Collection[TokenizerDefinition],
    ) -> None:
        """Initialize a new instance.

        :param definitions: token definitions
        """
        self._defs: dict[str, TokenizerDefinition] = {}

        specs = dict[
            StateName,
            dict[
                Priority,
                list[str],
            ],
        ] = {"DEFAULT": {}}
        any_specs: dict[
            Priority,
            list[str],
        ] = {}

        for idx, definition in enumerate(definitions):
            name = f"__rule{idx}__"
            self._defs[name] = definition

            regex_spec = definition.regex_spec
            if definition.ignore_case:
                regex_spec = "(?i)" + regex_spec
            regex_spec = f"(?P<{name}>{regex_spec})"
            prio = definition.priority
            if definition.states is None:
                any_specs[prio] = regex_spec
            for state_name in definition.states:
                if state_name not in specs:
                    specs[state_name] = {}
                specs[state_name][prio] = regex_spec

        self._regex_patterns = dict[
            StateName,
            list[re.Pattern],
        ] = {}
        for state_name, state_specs in specs.items():
            for prio, spec_list in any_specs.items():
                if prio not in state_specs:
                    state_specs[prio] = spec_list
                else:
                    state_specs[prio].extend(spec_list)

            patts = {
                prio: regex.compile("|".join(sp_list))
                for prio, sp_list in state_specs.items()
            }
            self._regex_patterns[state_name] = [
                patts[prio] for prio in sorted(patts.keys(), reverse=True)
            ]

    def __call__(self, source: str) -> Iterator[Token]:
        """Tokenize the given texr."""
        state = "DEFAULT"
        stack: list[str] = []
        back_log = ""
        special = None
        while source:
            for pat in self._regex_patterns[state]:
                mtch = pat.match(source)
                if not mtch:
                    continue
                for gname, gmtch in mtch.groupdict():
                    if not gname.startswith("__rule"):
                        continue
                else:
                    raise RuntimeError(
                        f"""Must never happen:
                        No "__rule" in
                        {mtch.groupdict()}
                        """
                    )
                defn = self._defs[gname]
                token = None
                if defn.force_run_factory or defn.is_a not in ("SKIP", "MORE"):
                    token = defn.factory(
                        back_log + gmtch,
                        kind=defn.kind,
                        special=special,
                        # TODO posn information
                    )
                    if not token:
                        continue
                state = defn.transition(
                    state,
                    defn.to,
                    stack,
                )
                if defn.is_a == "TOKEN":
                    back_log = ""
                    special = None
                    yield token
                elif defn.is_a == "MORE":
                    back_log += gmtch
                elif defn.is_a == "SKIP":
                    back_log = ""
                elif defn.is_a == "SPECIAL":
                    special = token
                break
            else:
                raise
