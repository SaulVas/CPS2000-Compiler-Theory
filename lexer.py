from enum import Enum

class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    WHITESPACE = "WHITESPACE"
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    VOID = "VOID"
    END = "END"
    SPECIAL_FUNCTION = "SPECIAL_FUNCTION"
    KEYWORD = "KEYWORD"
    ARROW = "ARROW"
    LEXICAL_ERROR = "LEXICAL_ERROR"

class Lexer:
    def __init__(self):
        self.lexeme_list = ["_", "letter", "digit", "ws", "eq", "sc", "other", "op", "delim", "dot", "hash", "gt", "minus"]
        self.states_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.states_accp = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12]

        self.rows = len(self.states_list)
        self.cols = len(self.lexeme_list)

        # Let's take integer -1 to represent the error state for this DFA
        self.Tx = [[-1 for j in range(self.cols)] for i in range(self.rows)]
        self.InitialiseTxTable()

    def InitialiseTxTable(self):
        # Update Tx to represent the state transition function of the DFA
        # Variables and Identifiers
        self.Tx[0][self.lexeme_list.index("letter")] = 1
        self.Tx[0][self.lexeme_list.index("_")] = 1
        self.Tx[1][self.lexeme_list.index("letter")] = 1
        self.Tx[1][self.lexeme_list.index("digit")] = 1
        self.Tx[1][self.lexeme_list.index("_")] = 1

        # White Space
        self.Tx[0][self.lexeme_list.index("ws")] = 2
        self.Tx[2][self.lexeme_list.index("ws")] = 2

        # Eq sign (=)
        self.Tx[0][self.lexeme_list.index("eq")] = 3

        # Integers and Literals
        self.Tx[0][self.lexeme_list.index("digit")] = 4
        self.Tx[4][self.lexeme_list.index("digit")] = 4
        self.Tx[4][self.lexeme_list.index("dot")] = 8  # Transition to state 8 for float numbers
        self.Tx[8][self.lexeme_list.index("digit")] = 8

        # Semicolon sign (;)
        self.Tx[0][self.lexeme_list.index("sc")] = 5

        # Operators
        self.Tx[0][self.lexeme_list.index("op")] = 6
        self.Tx[6][self.lexeme_list.index("eq")] = 6  # To handle operators like >=, <=, ==, !=
        self.Tx[0][self.lexeme_list.index("gt")] = 6  # To handle operators like >

        # Delimiters
        self.Tx[0][self.lexeme_list.index("delim")] = 7

        # Hexadecimal Literals (Colors)
        self.Tx[0][self.lexeme_list.index("hash")] = 9
        self.Tx[9][self.lexeme_list.index("digit")] = 10
        self.Tx[9][self.lexeme_list.index("letter")] = 10
        self.Tx[10][self.lexeme_list.index("digit")] = 10
        self.Tx[10][self.lexeme_list.index("letter")] = 10

        # Arrow (->)
        self.Tx[0][self.lexeme_list.index("minus")] = 11
        self.Tx[11][self.lexeme_list.index("gt")] = 12

    def AcceptingStates(self, state):
        return state in self.states_accp

    def GetTokenTypeByFinalState(self, state, lexeme):
        keywords = {"fun", "let", "return", "if", "else", "for", "while", "as", "int", "float", "bool", "colour"}
        special_functions = {"__print", "__delay", "__write", "__write_box", "__random_int", "__width", "__height", "__read", "__randi"}
        operators = {"and", "or", "not"}
        boolean_literals = {"true", "false"}

        if state == 1:
            if lexeme in keywords:
                return (TokenType.KEYWORD.value, lexeme)
            elif lexeme in special_functions:
                return (TokenType.SPECIAL_FUNCTION.value, lexeme)
            elif lexeme in operators:
                return (TokenType.OPERATOR.value, lexeme)
            elif lexeme in boolean_literals:
                return (TokenType.LITERAL.value, lexeme)
            return (TokenType.IDENTIFIER.value, lexeme)
        elif state == 2:
            return (TokenType.WHITESPACE.value, lexeme)
        elif state == 3:
            return (TokenType.OPERATOR.value, lexeme)
        elif state == 4:
            return (TokenType.LITERAL.value, lexeme)
        elif state == 5:
            return (TokenType.DELIMITER.value, lexeme)
        elif state == 6:
            return (TokenType.OPERATOR.value, lexeme)
        elif state == 7:
            return (TokenType.DELIMITER.value, lexeme)
        elif state == 8:
            return (TokenType.LITERAL.value, lexeme)
        elif state == 10:
            return (TokenType.LITERAL.value, lexeme)
        elif state == 12:
            return (TokenType.ARROW.value, lexeme)
        else:
            return (TokenType.LEXICAL_ERROR.value, lexeme)


    def CatChar(self, character):
        cat = "other"
        if character.isalpha(): cat = "letter"
        if character.isdigit(): cat = "digit"
        if character == "_": cat = "_"
        if character.isspace(): cat = "ws"
        if character == ";": cat = "sc"
        if character == "=": cat = "eq"
        if character in "+*/<>!": cat = "op"
        if character == ">": cat = "gt"
        if character == "-": cat = "minus"
        if character in "{}()[],;:": cat = "delim"
        if character == ".": cat = "dot"
        if character == "#": cat = "hash"
        return cat

    def EndOfInput(self, src_program_str, src_program_idx):
        return src_program_idx >= len(src_program_str)

    def NextChar(self, src_program_str, src_program_idx):
        if not self.EndOfInput(src_program_str, src_program_idx):
            return True, src_program_str[src_program_idx]
        else:
            return False, "."

    def NextToken(self, src_program_str, src_program_idx):
        state = 0  # initial state is 0 - check Tx
        stack = []
        lexeme = ""
        start_idx = src_program_idx
        stack.append(-2)  # insert the error state at the bottom of the stack.

        while state != -1:
            if self.AcceptingStates(state):
                stack.clear()
            stack.append(state)

            exists, character = self.NextChar(src_program_str, src_program_idx)
            if not exists:
                break  # Break out of loop if we're at the end of the string

            lexeme += character
            src_program_idx += 1

            cat = self.CatChar(character)
            if cat not in self.lexeme_list:
                state = -1
            else:
                state = self.Tx[state][self.lexeme_list.index(cat)]

        if lexeme:
            lexeme = lexeme[:-1]  # remove the last character added which sent the lexer to state -1

        syntax_error = False
        # rollback
        while len(stack) > 0:
            if stack[-1] == -2:  # report a syntax error
                syntax_error = True
                break

            # Pop this state if not an accepting state.
            if not self.AcceptingStates(stack[-1]):
                stack.pop()
                if lexeme:
                    lexeme = lexeme[:-1]
                src_program_idx -= 1

            # This is an accepting state ... return it.
            else:
                state = stack.pop()
                break

        if syntax_error:
            # Continue collecting characters until whitespace or semicolon is found
            while True:
                exists, character = self.NextChar(src_program_str, src_program_idx)
                if not exists or character.isspace() or character == ";":
                    break
                lexeme += character
                src_program_idx += 1
            return (TokenType.LEXICAL_ERROR.value, lexeme), lexeme

        if self.AcceptingStates(state):
            return self.GetTokenTypeByFinalState(state, lexeme), lexeme
        else:
            return (TokenType.LEXICAL_ERROR.value, lexeme), lexeme

    def GenerateTokens(self, src_program_str):
        tokens_list = []
        src_program_idx = 0

        while src_program_idx < len(src_program_str):
            token, lexeme = self.NextToken(src_program_str, src_program_idx)
            if token[0] != TokenType.WHITESPACE.value:
                tokens_list.append(token)
            if token[0] == TokenType.LEXICAL_ERROR.value:
                src_program_idx += len(lexeme)  # Skip the erroneous lexeme
            else:
                src_program_idx += len(lexeme)

            if src_program_idx >= (len(src_program_str) - 1):
                break  # Explicitly break the loop if we've reached the end of the input string

        return tokens_list

if __name__ == "__main__":
    lex = Lexer()
    input_code = '''
    fun MoreThan50(x:int) -> bool {
    let x:int = 23;
    if (x <= 50) {
        return false;
    }
    return true;
}
    '''
    toks = lex.GenerateTokens(input_code)
    with open("tokens.txt", "w") as f:
        for t in toks:
            f.write(f"{t}\n")

    for t in toks:
        print(t)
