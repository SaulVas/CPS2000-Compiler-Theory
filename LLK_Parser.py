from parser_nodes import *
from lexer import Lexer

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = ('EOF', '')

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        if self.current_token[0] == 'KEYWORD':
            if self.current_token[1] == 'fun':
                return self.parse_function_decl()
            elif self.current_token[1] == 'let':
                return self.parse_variable_decl()
            elif self.current_token[1] == 'return':
                return self.parse_return_statement()
            elif self.current_token[1] == 'if':
                return self.parse_if_statement()
            elif self.current_token[1] == 'for':
                return self.parse_for_statement()
            elif self.current_token[1] == 'while':
                return self.parse_while_statement()
            else:
                raise SyntaxError(f"Unexpected keyword {self.current_token[1]}")
        elif self.current_token[0] == 'IDENTIFIER':
            return self.parse_assignment()
        elif self.current_token[0] == 'DELIMITER' and self.current_token[1] == '{':
            return self.parse_block()
        elif self.current_token[0] == 'SPECIAL_FUNCTION':
            if self.current_token[1] == '__print':
                return self.parse_print_statement()
            elif self.current_token[1] == '__delay':
                return self.parse_delay_statement()
            elif self.current_token[1] == '__write' or self.current_token[1] == '__write_box':
                return self.parse_write_statement()
        else:
            raise SyntaxError(f"Unexpected token {self.current_token}")

    def parse_function_decl(self):
        self.advance()  # skip 'fun'
        identifier = self.current_token[1]
        self.advance()  # skip identifier
        self.expect('DELIMITER', '(')
        params = self.parse_formal_params()
        self.expect('DELIMITER', ')')
        self.expect('ARROW', '->')
        return_type = self.current_token[1]
        self.advance()  # skip return type
        block = self.parse_block()
        return FunctionDeclNode(identifier, params, return_type, block)

    def parse_formal_params(self):
        params = []
        if self.current_token[0] != 'DELIMITER' or self.current_token[1] != ')':
            params.append(self.parse_param())
            while self.current_token[0] == 'DELIMITER' and self.current_token[1] == ',':
                self.advance()  # skip ','
                params.append(self.parse_param())
        return params

    def parse_param(self):
        identifier = self.current_token[1]
        self.advance()  # skip identifier
        self.expect('DELIMITER', ':')
        param_type = self.current_token[1]
        self.advance()  # skip type
        return ParamNode(identifier, param_type)

    def parse_block(self):
        self.expect('DELIMITER', '{')
        statements = []
        while self.current_token[0] != 'DELIMITER' or self.current_token[1] != '}':
            statements.append(self.parse_statement())
        self.expect('DELIMITER', '}')
        return BlockNode(statements)

    def parse_variable_decl(self, expect_semicolon=True):
        self.advance()  # skip 'let'
        identifier = self.current_token[1]
        self.advance()  # skip identifier
        self.expect('DELIMITER', ':')
        var_type = self.current_token[1]
        self.advance()  # skip type
        expr = None
        if self.current_token[0] == 'OPERATOR' and self.current_token[1] == '=':
            self.advance()  # skip '='
            expr = self.parse_expression()
        if expect_semicolon:
            self.expect('DELIMITER', ';')
        return VariableDeclNode(identifier, var_type, expr)

    def parse_assignment(self, expect_semicolon=True):
        identifier = self.current_token[1]
        self.advance()  # skip identifier
        self.expect('OPERATOR', '=')
        expr = self.parse_expression()
        if expect_semicolon:
            self.expect('DELIMITER', ';')
        return AssignmentNode(identifier, expr)

    def parse_return_statement(self):
        self.advance()  # skip 'return'
        expr = self.parse_expression()
        self.expect('DELIMITER', ';')
        return ReturnStatementNode(expr)

    def parse_if_statement(self):
        self.advance()  # skip 'if'
        self.expect('DELIMITER', '(')
        condition = self.parse_expression()
        self.expect('DELIMITER', ')')
        if_block = self.parse_block()
        if self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'else':
            self.advance()  # skip 'else'
            else_block = self.parse_block()
            return IfStatementNode(condition, if_block, else_block)
        return IfStatementNode(condition, if_block)

    def parse_for_statement(self):
        self.advance()  # skip 'for'
        self.expect('DELIMITER', '(')
        init = self.parse_variable_decl(expect_semicolon=False) if self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'let' else self.parse_assignment(expect_semicolon=False)
        self.expect('DELIMITER', ';')
        condition = self.parse_expression()
        self.expect('DELIMITER', ';')
        post = self.parse_assignment(expect_semicolon=False)
        self.expect('DELIMITER', ')')
        block = self.parse_block()
        return ForStatementNode(init, condition, post, block)

    def parse_while_statement(self):
        self.advance()  # skip 'while'
        self.expect('DELIMITER', '(')
        condition = self.parse_expression()
        self.expect('DELIMITER', ')')
        block = self.parse_block()
        return WhileStatementNode(condition, block)

    def parse_print_statement(self):
        self.advance()  # skip '__print'
        expr = self.parse_expression()
        self.expect('DELIMITER', ';')
        return PrintStatementNode(expr)

    def parse_delay_statement(self):
        self.advance()  # skip '__delay'
        expr = self.parse_expression()
        self.expect('DELIMITER', ';')
        return DelayStatementNode(expr)

    def parse_write_statement(self):
        self.advance()  # skip '__write' or '__write_box'
        args = []
        while self.current_token[0] != 'DELIMITER' or self.current_token[1] != ';':
            args.append(self.parse_expression())
            if self.current_token[0] == 'DELIMITER' and self.current_token[1] == ',':
                self.advance()  # skip ','
        self.expect('DELIMITER', ';')
        return WriteStatementNode(args)

    def parse_expression(self):
        return self.parse_cast()

    def parse_cast(self):
        left = self.parse_or()
        while self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'as':
            self.advance()  # skip 'as'
            target_type = self.current_token[1]
            self.advance()  # skip type
            left = CastNode(left, target_type)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] == 'or':
            operator = self.current_token[1]
            self.advance()
            right = self.parse_and()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] == 'and':
            operator = self.current_token[1]
            self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] in ('==', '!='):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] in ('<', '>', '<=', '>='):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_term()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] in ('+', '-'):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.current_token[0] == 'OPERATOR' and self.current_token[1] in ('*', '/'):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(left, operator, right)
        return left

    def parse_unary(self):
        if self.current_token[0] == 'OPERATOR' and self.current_token[1] in ('-', 'not'):
            operator = self.current_token[1]
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token
        if token[0] == 'LITERAL':
            self.advance()
            if token[1] in {"true", "false"}:
                value = True if token[1] == "true" else False
                return LiteralNode(value)
            elif token[1].startswith("#"):
                return LiteralNode(token[1])
            elif token[1].isdigit() or (token[1].replace('.', '', 1).isdigit() and token[1].count('.') < 2):
                value = int(token[1]) if '.' not in token[1] else float(token[1])
                return LiteralNode(value)
            else:
                raise SyntaxError(f"Unexpected literal {token[1]}")
        elif token[0] == 'IDENTIFIER':
            identifier = token[1]
            self.advance()
            if self.current_token[0] == 'DELIMITER' and self.current_token[1] == '(':
                self.advance()  # skip '('
                args = []
                while self.current_token[0] != 'DELIMITER' or self.current_token[1] != ')':
                    args.append(self.parse_expression())
                    if self.current_token[0] == 'DELIMITER' and self.current_token[1] == ',':
                        self.advance()  # skip ','
                self.expect('DELIMITER', ')')
                return FunctionCallNode(identifier, args)
            return IdentifierNode(identifier)
        elif token[0] == 'DELIMITER' and token[1] == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect('DELIMITER', ')')
            return expr
        elif token[0] == 'SPECIAL_FUNCTION':
            func_name = token[1]
            self.advance()
            args = []
            while self.current_token[0] != 'DELIMITER' or self.current_token[1] != ';':
                args.append(self.parse_expression())
                if self.current_token[0] == 'DELIMITER' and self.current_token[1] == ',':
                    self.advance()  # skip ','
            return FunctionCallNode(func_name, args)
        raise SyntaxError(f"Unexpected token in expression: {token}")


    def expect(self, token_type, value=None):
        if self.current_token[0] != token_type or (value and self.current_token[1] != value):
            raise SyntaxError(f"Expected token {token_type} with value {value}, but got {self.current_token}")
        self.advance()

if __name__ == '__main__':
    # Example usage
    lexer = Lexer()
    input_code = '''
    fun MoreThan50(x:int) -> bool {
    let x:int = 23;
    if (x <= 50) {
        return false;
    }
    return true;
}
    '''
    token_input = lexer.GenerateTokens(input_code)
    parser = Parser(token_input)
    ast = parser.parse()
    traverse(ast)
