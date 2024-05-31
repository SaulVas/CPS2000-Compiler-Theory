from lexer import Lexer
from LLK_Parser import Parser
from parser_nodes import traverse

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, type):
        if name in self.scopes[-1]:
            raise Exception(f"Variable '{name}' already declared in the same scope")
        self.scopes[-1][name] = type

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable '{name}' not declared")

    def is_declared(self, name):
        for scope in self.scopes:
            if name in scope:
                return True
        return False

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_return_type = None

    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{node.__class__.__name__} method')

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_FunctionDeclNode(self, node):
        self.symbol_table.enter_scope()
        for param in node.params:
            self.visit(param)
        self.current_function_return_type = node.return_type
        self.visit(node.block)
        self.symbol_table.exit_scope()

    def visit_ParamNode(self, node):
        self.symbol_table.declare(node.identifier, node.param_type)

    def visit_BlockNode(self, node):
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_VariableDeclNode(self, node):
        expr_type = self.visit(node.expr)
        self.symbol_table.declare(node.identifier, node.var_type)
        if node.var_type != expr_type:
            raise Exception(f"Type mismatch: cannot assign {expr_type} to {node.var_type} in variable declaration of '{node.identifier}'")

    def visit_AssignmentNode(self, node):
        var_type = self.symbol_table.lookup(node.identifier)
        expr_type = self.visit(node.expr)
        if var_type != expr_type:
            raise Exception(f"Type mismatch: cannot assign {expr_type} to {var_type} in assignment to '{node.identifier}'")

    def visit_ReturnStatementNode(self, node):
        expr_type = self.visit(node.expr)
        if expr_type != self.current_function_return_type:
            raise Exception(f"Return type mismatch in function with return type {self.current_function_return_type}: got {expr_type}")

    def visit_IfStatementNode(self, node):
        self.visit(node.condition)
        self.visit(node.if_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_WhileStatementNode(self, node):
        self.visit(node.condition)
        self.visit(node.block)

    def visit_ForStatementNode(self, node):
        self.symbol_table.enter_scope()
        self.visit(node.init)
        self.visit(node.condition)
        self.visit(node.post)
        self.visit(node.block)
        self.symbol_table.exit_scope()

    def visit_PrintStatementNode(self, node):
        self.visit(node.expr)

    def visit_DelayStatementNode(self, node):
        self.visit(node.expr)

    def visit_WriteStatementNode(self, node):
        for arg in node.args:
            self.visit(arg)

    def visit_BinaryOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if node.operator in {'>', '<', '>=', '<=', '==', '!='}:
            if left_type != right_type:
                raise Exception(f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}")
            return 'bool'
        elif node.operator in {'+', '-', '*', '/'}:
            if left_type != right_type:
                raise Exception(f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}")
            return left_type
        elif node.operator in {'and', 'or'}:
            if left_type != 'bool' or right_type != 'bool':
                raise Exception(f"Logical operation requires boolean operands: {left_type} {node.operator} {right_type}")
            return 'bool'
        else:
            raise Exception(f"Unsupported binary operator: {node.operator}")


    def visit_UnaryOpNode(self, node):
        operand_type = self.visit(node.operand)
        return operand_type

    def visit_LiteralNode(self, node):
        if isinstance(node.value, bool):
            return 'bool'
        elif isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, float):
            return 'float'
        elif isinstance(node.value, str) and node.value.startswith("#"):
            return 'colour'
        else:
            raise Exception(f"Unknown literal type: {node.value}")

    def visit_IdentifierNode(self, node):
        return self.symbol_table.lookup(node.name)

    def visit_FunctionCallNode(self, node):
        # For simplicity, let's assume all function calls return int.
        # This would be expanded to check the function signature.
        for arg in node.args:
            self.visit(arg)
        return 'int'

    def visit_CastNode(self, node):
        return node.target_type



if __name__ == '__main__':
    input_code = '''
   fun AverageOfTwo(x:int, y:int) -> int {
    let t0:int = x + y;
    let t1:float = t0 / 2 as float;
    return t1;
}
    '''

    lexer = Lexer()
    tokens = lexer.GenerateTokens(input_code)
    parser = Parser(tokens)
    ast = parser.parse()

    # Perform semantic analysis
    analyzer = SemanticAnalyzer()
    analyzer.visit(ast)