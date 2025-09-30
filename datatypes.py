"""Defines data types used in submodule"""

#!/usr/bin/exec-suid --real -- /usr/bin/python -I

import sys

sys.path.append("/challenge")

from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass
class Statement(ABC):
    """Base class for all statements.

    Args:
        ABC (class): Helper class that provides a standard way to create an Abstract
        Base Class (ABC) using inheritance.
    """


@dataclass
class ImportStatement(Statement):
    """Dataclass for import statements.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        name (List[str]): Module name.
        alias (Optional[str]): Optional alias for module. Defaults to None.
    """

    names: List[str]
    alias: Optional[str] = None


@dataclass
class ImportFromStatement(Statement):
    """Dataclass for import-from statements.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        module (str): Module name.
        names (List[str]): List of submodule names.
        alias (Optional[str]): Optional alias for module. Defaults to None.
        level (int): Relative import level (0 absolute). Defaults to 0.
    """

    module: str
    names: List[str]
    alias: Optional[str] = None
    level: int = 0


@dataclass
class ClassDefStatement(Statement):
    """Dataclass for class definitions.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        name (str): Name of the class.
        bases (List[str]): List of classes it inherits from.
        body (List[Statement]): List of Statements for the body of the class.
    """

    name: str
    bases: List[str]
    body: List["Statement"]


@dataclass
class FunctionDefStatement(Statement):
    """Dataclass for function definitions.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        name (str): Name of the function. Defaults to an empty string.
        body (List[Statement]): List of Statements for the body of the function.
        args (List[str]): List of function arguments. Defaults to an empty list.
    """

    name: str
    body: List["Statement"]
    args: List[str] = field(default_factory=list)


@dataclass
class ForStatement(Statement):
    """Dataclass for For loops.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        target (str): Target variable in loop.
        iter (str): Iterable to loop to.
        body (List[Statement]): List of Statements for the body of the for loop.
        orelse (Optional[List[Statement]]): List of Statements in the else clause,
            if any. Defaults to an empty list and is optional.
    """

    target: str
    iter: str
    body: List["Statement"]
    orelse: Optional[List["Statement"]] = field(default_factory=list)


@dataclass
class WithStatement(Statement):
    """Dataclass for With statements

    Args:
        Statement (class): Base class for statements.

    Attributes:
        items (List[Tuple[str, Optional[str]]]): Items of the with statement.
        body (List[Statement]): List of Statements in the with statement.
    """

    items: List[Tuple[str, Optional[str]]]
    body: List["Statement"]


@dataclass
class IfStatement(Statement):
    """Dataclass for If statements

    Args:
        Statement (class): Base class for statements.

    Attributes:
        test (str): Conditional for the if statement.
        body (List[Statement]): List of Statements for body of the if statement.
        orelse (Optional[List[Statement]]): Optional list of Statements for else
            statement. Defaults to an empty list.
    """

    test: str
    body: List["Statement"]
    orelse: Optional[List["Statement"]] = field(default_factory=list)


@dataclass
class FunctionCallStatement(Statement):
    """Dataclass for function call statements.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        func (str): Name of the function called.
        args (List[str]): List of parameters passed to the function.
    """

    func: str
    args: List[str] = field(default_factory=list)


@dataclass
class AssignStatement(Statement):
    """Dataclass for assignment statements.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        targets (List[str]): List of target variables to store value in.
        value (Union[str, FunctionCallStatement]): Value to store in variables.
    """

    targets: List[str]
    value: Union[str, FunctionCallStatement]


@dataclass
class ExprStatement(Statement):
    """Dataclass for other expression statements such as comments or docstrings.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        value (str): Value of the expression.
    """

    value: str


@dataclass
class GenericStatement(Statement):
    """Dataclass for other statement types such as break or try-except.

    Args:
        Statement (class): Base class for statements.

    Attributes:
        type_name (str): Generic statement type.
    """

    type_name: str
