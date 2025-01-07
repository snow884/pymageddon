import ast
import operator as op

from common_utils.common_enums import Actions
from sandboxed_language.utils import find_nearest_xy, get_index, set_index

# supported operators
binary_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}

comparison_operators = {
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Lt: op.lt,
    ast.LtE: op.le,
    ast.Gt: op.gt,
    ast.GtE: op.ge,
    ast.Is: op.is_,
    ast.IsNot: op.is_not,
    ast.In: op.contains,
}

function_operators = {
    "find_nearest": find_nearest_xy,
    "get_index": get_index,
    "set_index": set_index,
}

my_variables = {}
steps = 0


def evaluate_expression(expression, variables):
    """Evaluates a Python expression with given variable substitutions."""

    class ExpressionEvaluator(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in variables:
                return ast.Constant(value=variables[node.id])
            return node

    tree = ast.parse(expression, mode="eval")
    tree = ExpressionEvaluator().visit(tree)
    substituted_expression = str(ast.unparse(tree))
    print(f"Substituting {expression} -> {substituted_expression}")
    return eval_math(substituted_expression)


class CodeVisitor(ast.NodeVisitor):
    def __init__(self, user_variables={}, max_steps=1000, code_in=""):
        self.max_steps = max_steps
        self.step_num = 0
        self.user_variables = user_variables
        self.code_in = code_in.split("\n")

        super(CodeVisitor).__init__()

    def check_steps(self):

        if self.step_num >= self.max_steps:
            raise ValueError(
                f"Max number of execution steps ({self.max_steps}) was exceeded"
            )

        self.step_num = self.step_num + 1

        print(self.step_num)

    def visit_If(self, node):

        self.check_steps()

        print("If statement found:")
        print("  Condition:", ast.unparse(node.test))
        print("  Body:", ast.unparse(node.body[0]))

        if node.orelse:
            print("  Else body:", ast.unparse(node.orelse[0]))

        expression = ast.unparse(node.test)

        result = evaluate_expression(expression, self.user_variables)

        print(f"Condition {expression} evaluates to {result}")

        if result:
            for body_none in node.body:

                self.visit(body_none)
        else:
            if node.orelse:

                for orelse_none in node.orelse:

                    self.visit(orelse_none)

        # self.generic_visit(node)

    def visit_Assign(self, node):

        self.check_steps()

        print("Assignment found:")

        print("  Target:", ast.unparse(node.targets[0]))
        print("  Value:", ast.unparse(node.value))

        expression = ast.unparse(node.value)

        result = evaluate_expression(expression, self.user_variables)

        self.user_variables[ast.unparse(node.targets[0])] = result

        # print(my_variables)

    def generic_visit(self, node):

        self.check_steps()

        print("generic visit")

        if type(node).__name__ != "Module":

            raise Exception(
                f"Unknown expression {self.code_in[node.lineno-1]} on line"
                f" {node.lineno}"
            )

        ast.NodeVisitor.generic_visit(self, node)


class MathVisitor(ast.NodeVisitor):
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op

        for op_ast_type, funct in binary_operators.items():

            if isinstance(op, op_ast_type):
                return funct(left, right)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])

        op = node.ops[0]

        # if isinstance(op, ast.Add):
        #     return left + right
        # elif isinstance(op, ast.Sub):
        #     return left - right
        # elif isinstance(op, ast.Mult):
        #     return left * right
        # elif isinstance(op, ast.Div):
        #     return left / right

        for op_ast_type, funct in comparison_operators.items():

            print(op_ast_type)
            print(op)
            print(left)
            print(right)
            if isinstance(op, op_ast_type):

                return funct(left, right)

        raise ValueError("Unknown operator")

    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def visit_NameConstant(self, node):
        return node.value

    def visit_List(self, node):
        return [self.visit(elt) for elt in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(elt) for elt in node.elts)

    def visit_Dict(self, node):
        return {
            self.visit(key): self.visit(value)
            for key, value in zip(node.keys, node.values)
        }

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Call(self, node):

        print("Calling function " + node.func.id)

        if node.func.id in function_operators.keys():
            # Evaluate literal expressions within the eval call

            args_evaluated = [self.visit(arg) for arg in node.args]
            print(args_evaluated)

            return function_operators[node.func.id](*args_evaluated)

    def generic_visit(self, node):

        self.check_steps()

        print("generic visit")

        if type(node).__name__ != "Module":

            raise Exception(f"Unknown expression {node.value} on line {node.lineno}")

        ast.NodeVisitor.generic_visit(self, node)


def eval_math(expr):
    tree = ast.parse(expr, mode="eval")
    visitor = MathVisitor()
    return visitor.visit(tree.body)


def evaluate_code(code_in, user_variables={}, current_object=None):

    tree = ast.parse(code_in)
    current_object_dict = {current_object.x, current_object.y}
    visitor = CodeVisitor(
        {
            "user_vars": user_variables,
            "intent": "",
            "current_object": current_object_dict,
        },
        code_in=code_in,
    )
    visitor.visit(tree)

    if visitor.user_variables["intent"]:

        if visitor.user_variables["intent"] == "ROTATE_UP":
            return Actions.ROTATE_UP
        elif visitor.user_variables["intent"] == "ROTATE_RIGHT":
            return Actions.ROTATE_RIGHT
        elif visitor.user_variables["intent"] == "ROTATE_DOWN":
            return Actions.ROTATE_DOWN
        elif visitor.user_variables["intent"] == "ROTATE_LEFT":
            return Actions.ROTATE_LEFT
        elif visitor.user_variables["intent"] == "MOVE_FORWARD":
            return Actions.MOVE_FORWARD
        else:
            if visitor.user_variables["intent"]:
                raise Exception(
                    f"Incorrect intent returned '{visitor.user_variables['intent']}'"
                )


# code = """

# a = "a"
# b = "b"
# x = 1
# z = {'x':1,'y':3}

# #s = find_nearest(8, 2,'Cow')
# m = get_index(z,'x')

# if (x < 10 ):
#     y = x + (x*2)

#     if x==1:
#         a = 3
# else:
#     y = 20

# c = 'c'

# """
# # print(eval_math('3 == 0'))
# evaluate_code(code)
