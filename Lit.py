from sly import Lexer, Parser

class LitLexer(Lexer):
    tokens = { NAME, NUMBER, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, LPAREN, RPAREN,
               EQ, LT, LE, GT, GE, NE,
               KINTAMASIS, JEIGU, KITAIP, SPAUSDINTI}

    ignore = ' \t'

    # Tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NAME['KINTAMASIS'] = KINTAMASIS
    NAME['JEIGU'] = JEIGU
    NAME['KITAIP'] = KITAIP
    NAME['SPAUSDINTI'] = SPAUSDINTI

    NUMBER = r'\d+'

    # Special symbols
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    EQ      = r'=='
    ASSIGN  = r'='
    LE      = r'<='
    LT      = r'<'
    GE      = r'>='
    GT      = r'>'
    NE      = r'!='
    LPAREN = r'\('
    RPAREN = r'\)'

    # Ignored pattern
    ignore_comment = r'\#.*'
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Uždraustas simbolis '%s'" % t.value[0])
        self.index += 1

class LitParser(Parser):
    tokens = LitLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS),
        )

    def __init__(self):
        self.names = { }

    @_('KINTAMASIS NAME ASSIGN expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    @_('expr')
    def statement(self, p):
        print(p.expr)

    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        return int(p.NUMBER)

    @_('NAME')
    def expr(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            print(f'Neatpažintas kintamasis {p.NAME!r}')
            return 0

if __name__ == '__main__':
    lexer = LitLexer()
    parser = LitParser()
    while True:
        try:
            text = input('Lit-- > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))