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
        self.InitialiseTxTable();     

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

        if state == 1:
            if lexeme in keywords:
                return (TokenType.KEYWORD.value, lexeme)
            elif lexeme in special_functions:
                return (TokenType.SPECIAL_FUNCTION.value, lexeme)
            elif lexeme in operators:
                return (TokenType.OPERATOR.value, lexeme)
            return (TokenType.IDENTIFIER.value, lexeme)
        elif state == 2:
            return (TokenType.WHITESPACE.value, lexeme)
        elif state == 3:
            return (TokenType.OPERATOR.value, lexeme)
        elif state == 4:
            if "." in lexeme:
                return (TokenType.LITERAL.value, lexeme)
            elif lexeme in {"true", "false"}:
                return (TokenType.LITERAL.value, lexeme)
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
        stack.append(-2);  # insert the error state at the bottom of the stack.
        
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
            print(f"Syntax error at index {start_idx}: {src_program_str[start_idx]}")
            src_program_idx = start_idx + 1  # Move to the next character after error
            return (TokenType.LEXICAL_ERROR.value, src_program_str[start_idx]), src_program_str[start_idx]

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
                src_program_idx += 1  # Skip the erroneous character
            else:
                src_program_idx += len(lexeme)
            print(f"Processed token: {token}, lexeme: {lexeme}, next index: {src_program_idx}")

            if src_program_idx >= (len(src_program_str) - 1):
                break  # Explicitly break the loop if we've reached the end of the input string

        return tokens_list


lex = Lexer()
toks = lex.GenerateTokens("""
fun Race(p1_c:colour , p2_c:colour , score_max:int) -> int {
    let p1_score:int = 0;
    let p2_score:int = 0;
    while ((p1_score < score_max) and (p2_score < score_max)) {
        let p1_toss:int = __randi 1000;
        let p2_toss:int = __randi 1000;
        if (p1_toss > p2_toss) {
            p1_score = p1_score + 1;
            __write 1, p1_score, p1_c;
        } else {
            p2_score = p2_score + 1;
            __write 2, p2_score, p2_c;
        }
        __delay 100;
    }
    if (p2_score > p1_score) {
        return 2;
    }
    return 1;
}

let c1:colour = #00ff00;
let c2:colour = #0000ff;
let m:int = __height;
let w:int = Race(c1, c2, m);
__print w;
""")
with open ("tokens.txt", "w") as f:
    for t in toks:
        f.write(f"{t}\n")

for t in toks:
    print(t)
