#!/usr/bin/exec-suid -- /usr/bin/python3.12 -I

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import sys


@dataclass
class FunctionCallSpec:
    """Specification for validating a function call."""
    function_name: str
    expected_args: List[str]
    expected_kwargs: Dict[str, str]
    expected_variable_count: Optional[int] = None
    allow_assignment: bool = True
    max_calls: int = 1


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class CodeValidator:
    """Validates user-submitted Python code for specific function calls and parameters."""

    def __init__(self, script_path: str, variables: List[str]):
        self.script_path = script_path
        self.variables: Dict[str, None] = dict.fromkeys(variables, None)
        self.steps = []
        self.lines = self._extract_python_details()
    
    def _extract_python_details(self) -> List[Dict]:
        """Extracts Python function call details from the script."""
        try:
            from .verify_helpers import extract_python_details
            return extract_python_details(self.script_path)
        except ImportError:
            raise ValidationError("Failed to import verification helpers.")
    
    def _read_flag(self) -> str:
        """Reads the flag from the file."""
        try:
            with open('/flag', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return 'Error: Flag file not found.'
    
    def _find_function_call(self, function_name: str) -> List[Dict]:
        """Finds function calls in the parsed code."""
        try:
            from .verify_helpers import find_function_call
            return find_function_call(self.lines, function_name)
        except ImportError:
            raise ValidationError(f'Failed to find function calls for {function_name}.')
    
    def _update_user_variable_names(self, function_call: Dict) -> None:
        """Update variables if applicable."""
        if isinstance(function_call['variable'], tuple):
            for var in function_call['variable']:
                self.variables[var] = var
        elif isinstance(function_call['variable'], str):
            self.variables[function_call['variable']] = function_call['variable']

    def _validate_function_call(self, step: str, spec: FunctionCallSpec) -> Tuple[bool, str]:
        """Validates a single funciton call against its specification."""
        function_calls = self._find_function_call(spec.function_name)

        if not function_calls:
            return False, f'{spec.function_name}() is not called in {step}.'
        if len(function_calls) > spec.max_calls:
            return False, f'{spec.function_name}() should be called only once in {step}.'
        
        call = function_calls[0]

        # Validate variable assignment
        if spec.expected_variable_count is not None:
            if call['variable'] is None:
                return False, f'{spec.function_name}() result must be assigned in {step}.'
            if isinstance(call['variable'], tuple) and len(call['variable']) != spec.expected_variable_count:
                return False, f'{spec.function_name}() should assign to {spec.expected_variable_count} variables in {step}.'
            if isinstance(call['variable'], str) and spec.expected_variable_count != 1:
                return False, f'{spec.function_name}() should assign to a single variable in {step}.'
        
        if not spec.allow_assignment and call['variable'] is not None:
            return False, f'{spec.function_name}() should not be assigned to a variable in {step}.'
        
        # Validate arguments
        if call['args'] != spec.expected_args and not (call['args'] == [] and call['kwargs'] == spec.expected_kwargs):
            return False, f'Incorrect parameters for {spec.function_name}() in {step}.'

        self._update_user_variable_names(function_call=call)
        
        return True, ''

    def _print_result(self, step_name: str, is_correct: bool, error_msg: str) -> None:
        """Prints the result of a validation step with colored output."""
        RED = '\033[31m'
        GREEN = '\033[32m'
        RESET = '\033[0m'
        color = GREEN if is_correct else RED
        status = 'Passed' if is_correct else 'Failed'
        print(f'{color}{step_name} {status}{RESET}')
        if error_msg:
            print(error_msg)

    def validate_steps(self) -> None:
        """Runs all validation steps and prints results."""
        for step_name, spec in self.steps:
            is_correct, error_msg = self._validate_function_call(step_name, spec)
            self._print_result(step_name, is_correct, error_msg)
            if not is_correct:
                sys.exit(1)
        
        print('Congratulations! You have passed this challenge! Here is your flag:')
        print(self._read_flag())