import sys

# --- Token types ---
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
)
TRUE, FALSE, AND, OR, NOT = 'TRUE', 'FALSE', 'AND', 'OR', 'NOT'
EQ, NEQ, LT, GT, LE, GE = 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'
STRING, IDENTIFIER, ASSIGN, PRINT = 'STRING', 'IDENTIFIER', 'ASSIGN', 'PRINT'

# --- Token class ---
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()

# --- Lexer ---
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return Token(INTEGER, float(result))

    def identifier(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        if result == 'true': return Token(TRUE, True)
        if result == 'false': return Token(FALSE, False)
        if result == 'and': return Token(AND, 'and')
        if result == 'or': return Token(OR, 'or')
        if result == 'print': return Token(PRINT, 'print')
        return Token(IDENTIFIER, result)

    def string(self):
        self.advance()
        result = ''
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        if self.current_char != '"':
            raise Exception('Unterminated string literal')
        self.advance()
        return Token(STRING, result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha():
                return self.identifier()

            if self.current_char == '"':
                return self.string()

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQ, '==')
                return Token(ASSIGN, '=')

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NEQ, '!=')
                return Token(NOT, '!')

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LE, '<=')
                return Token(LT, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GE, '>=')
                return Token(GT, '>')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)

# --- Parser ---
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f'Expected {token_type}, got {self.current_token}')

    def parse(self):
        if self.current_token.type == PRINT:
            self.eat(PRINT)
            expr = self.expr()
            return ('print', expr)

        elif self.current_token.type == IDENTIFIER:
            name = self.current_token.value
            self.eat(IDENTIFIER)
            if self.current_token.type == ASSIGN:
                self.eat(ASSIGN)
                value = self.expr()
                return ('assign', name, value)
            else:
                raise Exception(f'Invalid assignment: {name}')

        else:
            return self.expr()

    def expr(self):
        return self.logic_or()

    def logic_or(self):
        node = self.logic_and()
        while self.current_token.type == OR:
            self.eat(OR)
            node = ('or', node, self.logic_and())
        return node

    def logic_and(self):
        node = self.equality()
        while self.current_token.type == AND:
            self.eat(AND)
            node = ('and', node, self.equality())
        return node

    def equality(self):
        node = self.comparison()
        while self.current_token.type in (EQ, NEQ):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.comparison())
        return node

    def comparison(self):
        node = self.additive()
        while self.current_token.type in (LT, GT, LE, GE):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.additive())
        return node

    def additive(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == MINUS:
            self.eat(MINUS)
            return ('neg', self.factor())
        elif token.type == NOT:
            self.eat(NOT)
            return ('not', self.factor())
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif token.type == STRING:
            self.eat(STRING)
            return token.value
        elif token.type == TRUE:
            self.eat(TRUE)
            return True
        elif token.type == FALSE:
            self.eat(FALSE)
            return False
        elif token.type == IDENTIFIER:
            name = token.value
            self.eat(IDENTIFIER)
            return name
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            raise Exception(f"Unexpected token: {token}")

# --- Global variable environment ---
global_env = {}

# --- Evaluator ---
def evaluate(node):
    if isinstance(node, tuple) and node[0] == 'neg':
        return -evaluate(node[1])
    elif isinstance(node, tuple) and node[0] == 'not':
        return not evaluate(node[1])
    elif isinstance(node, tuple):
        if node[0] == 'assign':
            _, name, expr = node
            global_env[name] = evaluate(expr)
            return None
        if node[0] == 'print':
            val = evaluate(node[1])
            print(val)
            return None

        op, left, right = node
        lval = evaluate(left)
        rval = evaluate(right)

        if op == '+': return lval + rval
        if op == '-': return lval - rval
        if op == '*': return lval * rval
        if op == '/':
            if rval == 0: raise Exception("Division by zero")
            return lval / rval
        if op == '==': return lval == rval
        if op == '!=': return lval != rval
        if op == '<': return lval < rval
        if op == '>': return lval > rval
        if op == '<=': return lval <= rval
        if op == '>=': return lval >= rval
        if op == 'and': return lval and rval
        if op == 'or': return lval or rval

    elif isinstance(node, str):
        if node in global_env:
            return global_env[node]
        return node

    else:
        return node

# --- Run file ---
def run_file(filepath):
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lexer = Lexer(line)
                parser = Parser(lexer)
                tree = parser.parse()
                result = evaluate(tree)
                if result is not None:
                    if isinstance(result, str):
                        print(f'{line} = "{result}"')
                    else:
                        print(f'{line} = {result}')
            except Exception as e:
                print(f'Error in line "{line}": {e}')

# --- Entry point ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <filename.txt>")
    else:
        run_file(sys.argv[1])
