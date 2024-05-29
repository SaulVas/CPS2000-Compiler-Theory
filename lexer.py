import re

class Lexer:
    def __init__(self):
        self.transition_table = self.create_transition_table()
        self.state = 'S0'
        self.tokens = []
        self.current_token = ''
        self.token_patterns = self.define_token_patterns()

    def create_transition_table(self):
        return {
            'S0': {'letter': 'S1', 'digit': 'S2', 'operator': 'S3', 'delimiter': 'S4', 'whitespace': 'S0', 'invalid': 'S5'},
            'S1': {'letter': 'S1', 'digit': 'S1', 'whitespace': 'S4', 'operator': 'S4', 'delimiter': 'S4', 'invalid': 'S4'},
            'S2': {'digit': 'S2', 'operator': 'S4', 'delimiter': 'S4', 'whitespace': 'S4', 'invalid': 'S4'},
            'S3': {'operator': 'S3', 'letter': 'S4', 'digit': 'S4', 'whitespace': 'S4', 'delimiter': 'S4', 'invalid': 'S4'},
            'S4': {'any': 'S0'},
            'S5': {'invalid': 'S5', 'letter': 'S5', 'digit': 'S5', 'operator': 'S5', 'delimiter': 'S5', 'whitespace': 'S4'}
        }

    def define_token_patterns(self):
        patterns = {
            'KEYWORD': r'\b(fun|let|return|if|else|for|while|as|int|float|bool|colour)\b',
            'OPERATOR': r'(\+|\-|\*|\/|<|>|<=|>=|==|!=|and|or|not|=)',
            'DELIMITER': r'(\{|\}|\(|\)|\[|\]|,|;|:)',
            'ARROW': r'->',
            'LITERAL': r'(\d+\.\d+|\d+|true|false|#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?)',
            'IDENTIFIER': r'[A-Za-z_][A-Za-z0-9_]*',
            'SPECIAL_FUNCTION': r'\b(__print|__delay|__write|__write_box|__random_int|__width|__height|__read|__randi)\b',
            'WHITESPACE': r'\s+'
        }
        return patterns

    def get_input_type(self, char):
        if char.isalpha() or char == '_':
            return 'letter'
        elif char.isdigit():
            return 'digit'
        elif char.isspace():
            return 'whitespace'
        elif char in '+-*/<>=!&|':
            return 'operator'
        elif char in '{}()[],;:':
            return 'delimiter'
        elif char == '#':
            return 'hash'
        else:
            return 'invalid'

    def tokenize(self, input_string):
        self.state = 'S0'
        self.tokens = []
        self.current_token = ''
        i = 0
        while i < len(input_string):
            char = input_string[i]
            input_type = self.get_input_type(char)
            next_state = self.transition_table[self.state].get(input_type, 'S4')

            if next_state in ['S1', 'S2', 'S3', 'S5']:
                self.current_token += char
            elif next_state == 'S4':
                if self.state in ['S1', 'S2', 'S3']:
                    self.tokens.append((self.classify_token(self.current_token), self.current_token))
                    self.current_token = ''
                elif self.state == 'S5':
                    self.tokens.append(('LEXICAL_ERROR', self.current_token))
                    self.current_token = ''
                if input_type == 'operator' and self.state != 'S3':
                    self.current_token = char
                    next_state = 'S3'
                elif input_type == 'delimiter':
                    if self.current_token:
                        self.tokens.append((self.classify_token(self.current_token), self.current_token))
                        self.current_token = ''
                    self.tokens.append((self.classify_token(char), char))
                elif input_type == 'invalid':
                    self.current_token = char
                    next_state = 'S5'
                elif input_type == 'hash':
                    self.current_token += char
                    next_state = 'S1'
                elif input_type != 'whitespace':
                    self.current_token = char
                    next_state = self.transition_table['S0'].get(input_type, 'S4')
                else:
                    self.current_token = ''
            self.state = next_state
            i += 1

        if self.current_token:
            if self.state == 'S5':
                self.tokens.append(('LEXICAL_ERROR', self.current_token))
            else:
                self.tokens.append((self.classify_token(self.current_token), self.current_token))
        return self.tokens

    def classify_token(self, token):
        # Prioritize special functions before identifiers
        if re.fullmatch(self.token_patterns['SPECIAL_FUNCTION'], token):
            return 'SPECIAL_FUNCTION'
        for token_type, pattern in self.token_patterns.items():
            if token_type == 'SPECIAL_FUNCTION':
                continue
            if re.fullmatch(pattern, token):
                return token_type
        return 'LEXICAL_ERROR'

if __name__ == '__main__':
    # Example usage
    lexer = Lexer()
    input_code = '''
    fun Max(x:int, y:int) -> int {
        let m:int = x;
        if (y>=m) { m / y; }
        return m;
        let color = #000fff;
    }
    '''
    tokens = lexer.tokenize(input_code)
    for token in tokens:
        print(token)
