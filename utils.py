"""Functions used to assist with verifying challenge submissions for AI dojo."""

#!/usr/bin/exec-suid --real -- /usr/bin/python -I

import sys

sys.path.append("/challenge")

from typing import List, Optional

from .config import GREEN_TEXT_CODE, RED_TEXT_CODE, RESET_CODE
from .datatypes import (
    AssignStatement,
    ClassDefStatement,
    FunctionCallStatement,
    FunctionDefStatement,
    ImportStatement,
    ImportFromStatement,
    Statement,
)


def print_flag() -> None:
    """Prints flag upon successful completion of the challenge."""
    try:
        with open("/flag", "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("Error: Flag file not found.")


def run_verification(checks: List[callable]) -> None:
    """Runs a sequence of validation checks, prints results, and handles
    success/failure.

    Args:
        checks (list[callable]): List of check functions, each return
                                 (is_correct: bool, error_msg: str).
    """
    for step, check_func in enumerate(checks, 1):
        is_correct, error_msg = check_func()
        if not is_correct:
            print(f"{RED_TEXT_CODE}Step {step} Failed{RESET_CODE}")
            print(error_msg)
            sys.exit(1)
        print(f"{GREEN_TEXT_CODE}Step {step} Passed{RESET_CODE}")

    print("Congratulations! You have passed this challenge! Here is your flag:")
    print_flag()


def output_not_assigned_to_variable(function_call: FunctionCallStatement) -> bool:
    """Checks if output from a function call is assigned to a variable.

    Args:
        function_call (FunctionCall): Function call to check output of

    Returns:
        bool: True if the function call output is not assigned, False if it is
    """
    return function_call.variable is None


def function_not_called(function_calls: List[FunctionCallStatement]) -> bool:
    """Checks if function is called.

    Args:
        function_calls (List[Dict]): List of parsed Python statements for function call

    Returns:
        bool: True if function is not called, False otherwise
    """
    return len(function_calls) == 0


def find_function_calls(
    statements: List[Statement], function_name: str
) -> List[Statement]:
    """Searches through list of parsed Python statements and returns all lines that
    match given function name.

    Args:
        statements (List[Statement]): List of parsed Python statements.
        function_name (str): Name of function to search for.

    Returns:
        List[FunctionCallStatement]: List of parsed Python lines that match given
            function name.
    """
    function_calls = []
    for statement in statements:
        is_function_call_statement = (
            isinstance(statement, FunctionCallStatement)
            and statement.func == function_name
        )
        is_assign_statement = (
            isinstance(statement, AssignStatement)
            and isinstance(statement.value, FunctionCallStatement)
            and statement.value.func == function_name
        )
        if is_function_call_statement or is_assign_statement:
            function_calls.append(statement)
    return function_calls


def find_function_definition(
    statements: List[Statement], function_name: str
) -> Optional[FunctionDefStatement]:
    """
    Searches a list of statements for a function definition with the specified name.

    Args:
        statements (List[Statement]): A list of statements to search through.
        function_name (str): The name of the function to find.

    Returns:
        FunctionDefStatement: The function definition statement with the matching name,
            or None if not found.
    """
    for statement in statements:
        if (
            isinstance(statement, FunctionDefStatement)
            and statement.name == function_name
        ):
            return statement
    return None


def find_class_definition(
    statements: List[Statement], class_name: str
) -> Optional[ClassDefStatement]:
    """
    Searches a list of statements for a class definition with the specified name.

    Args:
        statements (List[Statement]): A list of statements to search through.
        class_name (str): The name of the class to find.

    Returns:
        ClassDefStatement: The class definition statement with the matching name, or
            None if not found.
    """
    for statement in statements:
        if isinstance(statement, ClassDefStatement) and statement.name == class_name:
            return statement
    return None


def find_import_statement(
    statements: List[Statement], module_name: str, alias: str = None
) -> Optional[ImportStatement]:
    """
    Searches a list of statements for an import statement with the specified name.

    Args:
        statements (List[Statement]): A list of statements to search through.
        module_name (str): The name of the import to find.
        alias (str): Alias for the import, defaults to None.

    Returns:
        Optional[ImportStatement]: The import statement with the matching name, or None
            if not found.
    """
    for statement in statements:
        if (
            isinstance(statement, ImportStatement)
            and module_name in statement.names
            and statement.alias == alias
        ):
            return statement
    return None


def find_import_from_statement(
    statements: List[Statement],
    module_name: str,
    submodules: List[str],
    alias: str = None,
) -> Optional[ImportFromStatement]:
    """
    Searches a list of statements for an import from statement with the specified name.

    Args:
        statements (List[Statement]): A list of statements to search through.
        module_name (str): The name of the import to find.
        submodules (List[str]): List of submodules imported from module.
        alias (str): Alias for the import, defaults to None.

    Returns:
        Optional[ImportFromStatement]: The import from statement with the matching name,
            or None if not found.
    """
    for statement in statements:
        if (
            isinstance(statement, ImportFromStatement)
            and statement.module == module_name
            and set(submodules) == set(statement.names)
            and statement.alias == alias
        ):
            return statement
    return None
