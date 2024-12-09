#!/opt/pwn.college/python

import ast


def unparse(node):
    """A backport of ast.unparse for Python 3.8."""
    import ast

    class _Unparser(ast.NodeVisitor):
        def __init__(self):
            self.result = ""

        def visit_Module(self, node):
            for stmt in node.body:
                self.visit(stmt)

        def visit_Expr(self, node):
            self.visit(node.value)
            self.result += "\n"

        def visit_Assign(self, node):
            for target in node.targets:
                self.visit(target)
                self.result += " = "
            self.visit(node.value)
            self.result += "\n"

        def visit_Name(self, node):
            self.result += node.id

        def visit_Constant(self, node):
            self.result += repr(node.value)

        def visit_BinOp(self, node):
            self.visit(node.left)
            self.result += f" {self.operator(node.op)} "
            self.visit(node.right)

        def visit_Attribute(self, node):
            # Handles attribute access like model.fit
            self.visit(node.value)  # Visit the base (e.g., model)
            self.result += f".{node.attr}"  # Append the attribute name (e.g., fit)

        def visit_Call(self, node):
            # Handles function/method calls like model.fit()
            self.visit(node.func)  # Visit the function being called
            self.result += "("
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.result += ", "
                self.visit(arg)  # Visit each argument
            self.result += ")"

        def visit_arguments(self, node):
            # Handle arguments for function definitions (not relevant here)
            pass

        def operator(self, op):
            if isinstance(op, ast.Add):
                return "+"
            if isinstance(op, ast.Sub):
                return "-"
            if isinstance(op, ast.Mult):
                return "*"
            if isinstance(op, ast.Div):
                return "/"
            raise NotImplementedError(f"Operator {op} not implemented")

    unparser = _Unparser()
    unparser.visit(node)
    return unparser.result


def extract_python_details(filepath):
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read(), filename=filepath)

    lines = []
    variables = []
    for node in ast.walk(tree):
        # Handle assignment: variable = function(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            # Handle unpacked variables (tuple or list)
            if isinstance(node.targets[0], (ast.Tuple, ast.List)):
                variable = tuple(unparse(var) for var in node.targets[0].elts)
            # Single variable assignment
            elif isinstance(node.targets[0], ast.Name):
                variable = node.targets[0].id if node.targets[0].id != '_' else None
            else:
                variable = None
            
            func = unparse(node.value.func)
            args = [unparse(arg) for arg in node.value.args]
            kwargs = {kw.arg: unparse(kw.value) for kw in node.value.keywords}

            lines.append({
                'variable': variable,
                'function': func,
                'args': args,
                'kwargs': kwargs
            })

        # Handle standalone function calls like model.fit(...)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = unparse(node.value.func)
            args = [unparse(arg) for arg in node.value.args]
            kwargs = {kw.arg: unparse(kw.value) for kw in node.value.keywords}

            lines.append({
                'variable': None,
                'function': func,
                'args': args,
                'kwargs': kwargs
            })
    
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Handle Constant values
                    if isinstance(node.value, ast.Constant):  
                        value = node.value.value  # Directly get the value
                    else:
                        value = None  # Handle non-Constant cases
                    
                    variables.append({
                        'variable': target.id,
                        'value': value
                    })

    return lines, variables


def find_function_call(lines, function_name):
    function_calls = []
    for line in lines:
        if line['function'] == function_name:
            function_calls.append(line)
    return function_calls


def retrieve_variable_values(filepath):
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
    

# create function that can do a LIKE check
# such as specifying 'np' and it grabs all lines that are like 'np.random.rand' and 'np.random.randint'
