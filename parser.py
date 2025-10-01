"""Statement parser for parsing Python code into custom datatypes for verification."""

#!/usr/bin/exec-suid --real -- /usr/bin/python -I

import sys

sys.path.append("/challenge")

import ast
from typing import Dict, List, Optional

from .datatypes import (
    Statement,
    ImportStatement,
    ImportFromStatement,
    ClassDefStatement,
    FunctionDefStatement,
    ForStatement,
    WithStatement,
    IfStatement,
    AssignStatement,
    FunctionCallStatement,
    ExprStatement,
    GenericStatement,
)


class StatementParser(ast.NodeVisitor):
    """Parser to convert Python code to custom dataclasses.

    Args:
        ast.NodeVisitor (class): Node visitor base class.
    """

    def __init__(self, filepath: str) -> None:
        super(StatementParser).__init__()
        self.filepath = filepath
        self.tree = self._get_file_contents()

    def parse(self) -> List[Statement]:
        """Parses a Python source file into a list of Statement objects.

        This method constructs an Abstract Syntax Tree (AST), and processes each
        top-level node to create corresponding Statement dataclasses. Each node is
        processed using the `_process_statement` method, and the resulting statements
        are collected if they are not None. The method also traverses the AST using
        the `visit` method for further processing.

        Args:
            filepath (str): The path to the Python source file to parse.

        Raises:
            FileNotFoundError: If the specified file at `filepath` does not exist.

        Returns:
            List[Statement]: A list of Statement objects representing the parsed
                top-level statements in the source file. If a statement cannot be parsed
                into a specific Statement type, a GenericStatement may be included.
        """

        parsed_statements = []
        for node in self.tree.body:
            stmt = self._process_statement(node)
            if stmt:
                parsed_statements.append(stmt)
            self.visit(node)
        return parsed_statements

    def retrieve_variable_values(self) -> Dict:
        """Retrieves all variables defined in Python file and their values.

        Returns:
            Dict: Key value pairs of variable names and their values
        """

        variables = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        try:
                            value = ast.literal_eval(node.value)
                            variables[target.id] = value
                        except ValueError:
                            try:
                                expression_code = compile(
                                    ast.Expression(node.value), "<ast>", "eval"
                                )
                                value = eval(expression_code, {}, variables)
                                variables[target.id] = value
                            except Exception:
                                variables[target.id] = "Unresolvable dynamic value"

        return variables

    def _process_statement(self, node: ast.AST) -> Optional[Statement]:
        statement_parsers = {
            ast.Import: self._parse_import_statement,
            ast.ImportFrom: self._parse_importfrom_statement,
            ast.ClassDef: self._parse_class_definition,
            ast.FunctionDef: self._parse_function_definition,
            ast.For: self._parse_for_loop,
            ast.With: self._parse_with_statement,
            ast.If: self._parse_if_statement,
            ast.Assign: self._parse_assign_statement,
        }

        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            return self._parse_function_call(node)

        if isinstance(node, ast.Expr):
            return self._parse_expression_statement(node)

        parser = statement_parsers.get(type(node))
        if parser:
            return parser(node)

        return GenericStatement(type_name=node.__class__.__name__)

    def generic_visit(self, node):
        if hasattr(node, "body"):
            for stmt in node.body:
                self.visit(stmt)
            if hasattr(node, "orelse"):
                for stmt in node.orelse:
                    self.visit(stmt)

    @staticmethod
    def _parse_import_statement(node: ast.AST) -> ImportStatement:
        names = [name.name for name in node.names]
        # Use the first alias if available, otherwise None
        alias = node.names[0].asname if node.names and node.names[0].asname else None
        return ImportStatement(names=names, alias=alias)

    @staticmethod
    def _parse_importfrom_statement(node: ast.AST) -> ImportFromStatement:
        names = [name.name for name in node.names]
        # Use the first alias if available, otherwise None
        alias = node.names[0].asname if node.names and node.names[0].asname else None
        return ImportFromStatement(
            module=node.module or "", names=names, alias=alias, level=node.level
        )

    def _parse_class_definition(self, node: ast.AST) -> ClassDefStatement:
        bases = [ast.unparse(base) for base in node.bases]
        body = [self._process_statement(stmt) for stmt in node.body]
        return ClassDefStatement(
            name=node.name, bases=bases, body=[stmt for stmt in body if stmt]
        )

    def _parse_function_definition(self, node: ast.AST) -> FunctionDefStatement:
        args = [arg.arg for arg in node.args.args]
        body = [self._process_statement(stmt) for stmt in node.body]
        return FunctionDefStatement(
            name=node.name, args=args, body=[stmt for stmt in body if stmt]
        )

    def _parse_for_loop(self, node: ast.AST) -> ForStatement:
        target = ast.unparse(node.target) if node.target else ""
        iter_expr = ast.unparse(node.iter) if node.iter else ""
        body = [self._process_statement(stmt) for stmt in node.body]
        orelse = [self._process_statement(stmt) for stmt in node.orelse]
        return ForStatement(
            target=target,
            iter=iter_expr,
            body=[stmt for stmt in body if stmt],
            orelse=[stmt for stmt in orelse if stmt],
        )

    def _parse_with_statement(self, node: ast.AST) -> WithStatement:
        items = [
            (
                ast.unparse(item.context_expr),
                ast.unparse(item.optional_vars) if item.optional_vars else None,
            )
            for item in node.items
        ]
        body = [self._process_statement(stmt) for stmt in node.body]
        return WithStatement(items=items, body=[stmt for stmt in body if stmt])

    def _parse_if_statement(self, node: ast.AST) -> IfStatement:
        test = ast.unparse(node.test) if node.test else ""
        body = [self._process_statement(stmt) for stmt in node.body]
        orelse = [self._process_statement(stmt) for stmt in node.orelse]
        return IfStatement(
            test=test,
            body=[stmt for stmt in body if stmt],
            orelse=[stmt for stmt in orelse if stmt],
        )

    def _parse_assign_statement(self, node: ast.AST) -> AssignStatement:
        targets = []
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        targets.append(elt.id)
                    else:
                        targets.append(ast.unparse(elt))
            else:
                targets.append(ast.unparse(target))

        if isinstance(node.value, ast.Call):
            value = self._parse_function_call(ast.Expr(value=node.value))
        else:
            value = ast.unparse(node.value) if node.value else ""
        return AssignStatement(targets=targets, value=value)

    @staticmethod
    def _parse_function_call(node: ast.AST) -> FunctionCallStatement:
        func = ast.unparse(node.value.func)
        args = [ast.unparse(arg) for arg in node.value.args]
        kwargs = {kw.arg: ast.unparse(kw.value) for kw in node.value.keywords}
        return FunctionCallStatement(func=func, args=args, kwargs=kwargs)

    @staticmethod
    def _parse_expression_statement(node: ast.AST) -> ExprStatement:
        value = ast.unparse(node.value) if node.value else ""
        return ExprStatement(value=value)

    def _get_file_contents(self) -> ast.Module:
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                return ast.parse(file.read(), filename=self.filepath)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {self.filepath}") from e
