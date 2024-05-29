class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return f"ProgramNode(statements={self.statements})"

class FunctionDeclNode:
    def __init__(self, identifier, params, return_type, block):
        self.identifier = identifier
        self.params = params
        self.return_type = return_type
        self.block = block

    def __str__(self):
        return (f"FunctionDeclNode(identifier={self.identifier}, params={self.params}, "
                f"return_type={self.return_type}, block={self.block})")

class ParamNode:
    def __init__(self, identifier, param_type):
        self.identifier = identifier
        self.param_type = param_type

    def __str__(self):
        return f"ParamNode(identifier={self.identifier}, param_type={self.param_type})"

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return f"BlockNode(statements={self.statements})"

class VariableDeclNode:
    def __init__(self, identifier, var_type, expr=None):
        self.identifier = identifier
        self.var_type = var_type
        self.expr = expr

    def __str__(self):
        return (f"VariableDeclNode(identifier={self.identifier}, var_type={self.var_type}, "
                f"expr={self.expr})")

class AssignmentNode:
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def __str__(self):
        return f"AssignmentNode(identifier={self.identifier}, expr={self.expr})"

class ReturnStatementNode:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"ReturnStatementNode(expr={self.expr})"

class IfStatementNode:
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

    def __str__(self):
        return (f"IfStatementNode(condition={self.condition}, if_block={self.if_block}, "
                f"else_block={self.else_block})")

class ForStatementNode:
    def __init__(self, init, condition, post, block):
        self.init = init
        self.condition = condition
        self.post = post
        self.block = block

    def __str__(self):
        return (f"ForStatementNode(init={self.init}, condition={self.condition}, "
                f"post={self.post}, block={self.block})")

class WhileStatementNode:
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def __str__(self):
        return f"WhileStatementNode(condition={self.condition}, block={self.block})"

class PrintStatementNode:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"PrintStatementNode(expr={self.expr})"

class DelayStatementNode:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"DelayStatementNode(expr={self.expr})"

class WriteStatementNode:
    def __init__(self, args):
        self.args = args

    def __str__(self):
        return f"WriteStatementNode(args={self.args})"

class BinaryOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"BinaryOpNode(left={self.left}, operator={self.operator}, right={self.right})"

class UnaryOpNode:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __str__(self):
        return f"UnaryOpNode(operator={self.operator}, operand={self.operand})"

class LiteralNode:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"LiteralNode(value={self.value})"

class IdentifierNode:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"IdentifierNode(name={self.name})"

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return f"FunctionCallNode(name={self.name}, args={self.args})"
    
class CastNode:
    def __init__(self, expr, target_type):
        self.expr = expr
        self.target_type = target_type

    def __str__(self):
        return f"CastNode(expr={self.expr}, target_type={self.target_type})"
    
def traverse(node, indent=0):
    ind = '  ' * indent
    if isinstance(node, ProgramNode):
        print(f"{ind}ProgramNode:")
        for stmt in node.statements:
            traverse(stmt, indent + 1)
    elif isinstance(node, FunctionDeclNode):
        print(f"{ind}FunctionDeclNode: {node.identifier}")
        print(f"{ind}  Params:")
        for param in node.params:
            traverse(param, indent + 2)
        print(f"{ind}  ReturnType: {node.return_type}")
        traverse(node.block, indent + 1)
    elif isinstance(node, ParamNode):
        print(f"{ind}ParamNode: {node.identifier}: {node.param_type}")
    elif isinstance(node, BlockNode):
        print(f"{ind}BlockNode:")
        for stmt in node.statements:
            traverse(stmt, indent + 1)
    elif isinstance(node, VariableDeclNode):
        print(f"{ind}VariableDeclNode: {node.identifier}: {node.var_type}")
        if node.expr:
            traverse(node.expr, indent + 1)
    elif isinstance(node, AssignmentNode):
        print(f"{ind}AssignmentNode: {node.identifier}")
        traverse(node.expr, indent + 1)
    elif isinstance(node, ReturnStatementNode):
        print(f"{ind}ReturnStatementNode:")
        traverse(node.expr, indent + 1)
    elif isinstance(node, IfStatementNode):
        print(f"{ind}IfStatementNode:")
        print(f"{ind}  Condition:")
        traverse(node.condition, indent + 2)
        print(f"{ind}  IfBlock:")
        traverse(node.if_block, indent + 2)
        if node.else_block:
            print(f"{ind}  ElseBlock:")
            traverse(node.else_block, indent + 2)
    elif isinstance(node, ForStatementNode):
        print(f"{ind}ForStatementNode:")
        if node.init:
            print(f"{ind}  Init:")
            traverse(node.init, indent + 2)
        print(f"{ind}  Condition:")
        traverse(node.condition, indent + 2)
        if node.post:
            print(f"{ind}  Post:")
            traverse(node.post, indent + 2)
        print(f"{ind}  Block:")
        traverse(node.block, indent + 2)
    elif isinstance(node, WhileStatementNode):
        print(f"{ind}WhileStatementNode:")
        print(f"{ind}  Condition:")
        traverse(node.condition, indent + 2)
        print(f"{ind}  Block:")
        traverse(node.block, indent + 2)
    elif isinstance(node, PrintStatementNode):
        print(f"{ind}PrintStatementNode:")
        traverse(node.expr, indent + 1)
    elif isinstance(node, DelayStatementNode):
        print(f"{ind}DelayStatementNode:")
        traverse(node.expr, indent + 1)
    elif isinstance(node, WriteStatementNode):
        print(f"{ind}WriteStatementNode:")
        for arg in node.args:
            traverse(arg, indent + 1)
    elif isinstance(node, BinaryOpNode):
        print(f"{ind}BinaryOpNode: {node.operator}")
        traverse(node.left, indent + 1)
        traverse(node.right, indent + 1)
    elif isinstance(node, UnaryOpNode):
        print(f"{ind}UnaryOpNode: {node.operator}")
        traverse(node.operand, indent + 1)
    elif isinstance(node, LiteralNode):
        print(f"{ind}LiteralNode: {node.value}")
    elif isinstance(node, IdentifierNode):
        print(f"{ind}IdentifierNode: {node.name}")
    elif isinstance(node, FunctionCallNode):
        print(f"{ind}FunctionCallNode: {node.name}")
        for arg in node.args:
            traverse(arg, indent + 1)
    elif isinstance(node, CastNode):
        print(f"{ind}CastNode:")
        print(f"{ind}  Expr:")
        traverse(node.expr, indent + 2)
        print(f"{ind}  TargetType: {node.target_type}")
    else:
        print(f"{ind}Unknown node: {node}")

