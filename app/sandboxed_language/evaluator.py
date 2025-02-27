import ast
import operator as op
import random

from common_utils.common_enums import Actions, Rotations
from sandboxed_language.utils import find_nearest_xy, get_index, set_index

DEBUG = False

# supported operators
binary_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}

unary_operators = {
    ast.Not: op.not_,
}


def not_in(left, right):
    return left not in right


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
    ast.NotIn: not_in,
}

bool_operators = {ast.And: op.and_, ast.Or: op.or_, ast.Not: op.not_}

function_operators = {
    "find_nearest_xy": find_nearest_xy,
    "get_index": get_index,
    "set_index": set_index,
    "random_randint": random.randint,
    "random_choice": random.choice,
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
    if DEBUG:
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
        if DEBUG:
            print(self.step_num)

    def visit_If(self, node):

        self.check_steps()
        if DEBUG:
            print("If statement found:")
            print("  Condition:", ast.unparse(node.test))
            print("  Body:", ast.unparse(node.body[0]))

        if node.orelse:
            if DEBUG:
                print("  Else body:", ast.unparse(node.orelse[0]))

        expression = ast.unparse(node.test)

        result = evaluate_expression(expression, self.user_variables)
        if DEBUG:
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
        if DEBUG:
            print("Assignment found:")

            print("  Target:", ast.unparse(node.targets[0]))
            print("  Value:", ast.unparse(node.value))

        expression = ast.unparse(node.value)

        result = evaluate_expression(expression, self.user_variables)

        self.user_variables[ast.unparse(node.targets[0])] = result

        # print(my_variables)

    def visit_Global(self, node):

        for var_name in node.names:

            if var_name not in self.user_variables:

                self.user_variables[var_name] = None

    def generic_visit(self, node):

        self.check_steps()
        if DEBUG:
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

    def visit_UnaryOp(self, node):

        operand = self.visit(node.operand)
        op = node.op

        for op_ast_type, funct in unary_operators.items():

            if isinstance(op, op_ast_type):
                return funct(operand)

    def visit_BoolOp(self, node):

        operand1 = self.visit(node.values[0])
        operand2 = self.visit(node.values[1])
        op = node.op

        for op_ast_type, funct in bool_operators.items():

            if isinstance(op, op_ast_type):
                return funct(operand1, operand2)

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
            if DEBUG:
                print(op_ast_type)
                print(op)
                print(left)
                print(right)
            if isinstance(op, op_ast_type):

                return funct(left, right)

        raise ValueError(f"Unknown operator {op_ast_type}")

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

    def visit_Subscript(self, node):
        return self.visit(node.value)[self.visit(node.slice)]

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Call(self, node):
        if DEBUG:
            print("Calling function " + node.func.id + " with args " + str(node.args))

        if node.func.id in function_operators.keys():
            # Evaluate literal expressions within the eval call

            args_evaluated = [self.visit(arg) for arg in node.args]

            return function_operators[node.func.id](*args_evaluated)

        else:

            raise Exception(
                f"Unknown function {node.func.id}  called on line {node.lineno}"
            )

    def generic_visit(self, node):
        if DEBUG:
            print("generic visit")

        if type(node).__name__ != "Module":
            if DEBUG:
                print(node.__class__)
                print(node.__dict__)

            raise Exception(f"Unknown expression {node} on line {node.lineno}")

        ast.NodeVisitor.generic_visit(self, node)


def eval_math(expr):
    tree = ast.parse(expr, mode="eval")
    visitor = MathVisitor()
    return visitor.visit(tree.body)


def evaluate_code(code_in, user_variables={}, parent_object=None):

    error = ""

    try:
        tree = ast.parse(code_in)
    except Exception as e:
        error = "Error: " + str(e)
        intent = None
        user_variables_out = {}
        return intent, user_variables_out, error

    if parent_object:

        if parent_object.rotation == Rotations.UP:
            rotation = "UP"
        elif parent_object.rotation == Rotations.RIGHT:
            rotation = "RIGHT"
        elif parent_object.rotation == Rotations.DOWN:
            rotation = "DOWN"
        elif parent_object.rotation == Rotations.LEFT:
            rotation = "LEFT"

        parent_object_dict = {
            "x": parent_object.x,
            "y": parent_object.y,
            "rotation": rotation,
        }
    else:
        parent_object_dict = {}

    user_variables_in = user_variables
    user_variables_in["intent"] = None
    user_variables_in["parent_object"] = parent_object_dict

    visitor = CodeVisitor(
        user_variables=user_variables_in,
        code_in=code_in,
    )

    try:
        visitor.visit(tree)
    except Exception as e:
        error = "Error: " + str(e)

    if visitor.user_variables["intent"]:

        if visitor.user_variables["intent"] == "ROTATE_UP":
            intent = Actions.ROTATE_UP
        elif visitor.user_variables["intent"] == "ROTATE_RIGHT":
            intent = Actions.ROTATE_RIGHT
        elif visitor.user_variables["intent"] == "ROTATE_DOWN":
            intent = Actions.ROTATE_DOWN
        elif visitor.user_variables["intent"] == "ROTATE_LEFT":
            intent = Actions.ROTATE_LEFT
        elif visitor.user_variables["intent"] == "MOVE_FORWARD":
            intent = Actions.MOVE_FORWARD
        else:
            if visitor.user_variables["intent"]:
                raise Exception(
                    f"Incorrect intent returned '{visitor.user_variables['intent']}'"
                )
    else:
        intent = None

    user_variables_out = {
        k: v
        for k, v in visitor.user_variables.items()
        if k not in ["user_vars", "intent", "parent_object"]
    }

    return intent, user_variables_out, error


# code = """

# global a

# if not a:
#     a = 10
# else:
#     a = 13

# # b = "b"
# # x = 1
# # z = {'x':1,'y':3}

# # # s = find_nearest(x, 2,'Cow')
# # m = get_index(z,'x')

# # if (x < 10 ):
# #     y = x + (x*2)

# #     if x==1:
# #         a = 3
# # else:
# #     y = 20

# # c = 'c'

# """
# # print(eval_math('3 == 0'))
# intent, vars = evaluate_code(code)
# print(vars)
# intent, vars = evaluate_code(code,user_variables=vars)
# print(vars)
