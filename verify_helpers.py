#!/usr/bin/exec-suid --real -- /usr/bin/python -I

import ast
from .datatypes import FunctionCall
from typing import List, Dict


def extract_python_details(filepath):
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read(), filename=filepath)

    lines = []
    for node in ast.walk(tree):
        # Handle assignment: variable = function(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            # Handle unpacked variables (tuple or list)
            if isinstance(node.targets[0], (ast.Tuple, ast.List)):
                variable = tuple(ast.unparse(var) for var in node.targets[0].elts)
            # Single variable assignment
            elif isinstance(node.targets[0], ast.Name):
                variable = node.targets[0].id if node.targets[0].id != '_' else None
            else:
                variable = None
            
            func = ast.unparse(node.value.func)
            args = [ast.unparse(arg) for arg in node.value.args]
            kwargs = {kw.arg: ast.unparse(kw.value) for kw in node.value.keywords}

            lines.append({
                'variable': variable,
                'function': func,
                'args': args,
                'kwargs': kwargs
            })

        # Handle standalone function calls like model.fit(...)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = ast.unparse(node.value.func)
            args = [ast.unparse(arg) for arg in node.value.args]
            kwargs = {kw.arg: ast.unparse(kw.value) for kw in node.value.keywords}

            lines.append({
                'variable': None,
                'function': func,
                'args': args,
                'kwargs': kwargs
            })

    return lines


def find_function_call(lines, function_name):
    function_calls = []
    for line in lines:
        if line['function'] == function_name:
            function_calls.append(line)
    return function_calls


def retrieve_variable_values(filepath: str) -> Dict:
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read(), filename=filepath)
    
    variables = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        value = ast.literal_eval(node.value)
                        variables[target.id] = value
                    except ValueError:
                        try:
                            expression_code = compile(ast.Expression(node.value), '<ast>', 'eval')
                            value = eval(expression_code, {}, variables)
                            variables[target.id] = value
                        except Exception:
                            variables[target.id] = "Unresolvable dynamic value"
    
    return variables


def output_not_assigned_to_variable(function_call: FunctionCall) -> bool:
    return function_call.variable is None


def function_not_called(function_calls: List[Dict]) -> bool:
    return len(function_calls) == 0