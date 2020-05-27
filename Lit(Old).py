from sly import Lexer
from sly import Parser

class LitLexer(Lexer):
    tokens = { NAME, NUMBER, STRING, JEIGU, TADA, KITAIP, CIKLAS, FUN, IKI, ARROW, EQEQ, GREATER, LESSER, GREATEROREQ, LESSEROREQ, KINTAMASIS, SPAUSDINTI }
    ignore = '\t ' # ignore tabs or spaces

    literals = { '=', '+', '-', '/', '*', '(', ')', '{', '}', ',', ';', '>', '<'} # one character tokens

    # actual tokens
    JEIGU = r'JEIGU'
    TADA = r'TADA'
    KITAIP = r'KITAIP'
    CIKLAS = r'CIKLAS'
    FUN = r'FUN'
    IKI = r'IKI'
    KINTAMASIS = r'KINTAMASIS'
    SPAUSDINTI = r'SPAUSDINTI'
    ARROW = r'->'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*' # first character must be a-Z and the rest a-9 or _
    STRING = r'\".*?\"' # define string between " " symbols

    EQEQ = r'=='
    GREATER = r'>'
    LESSER = r'<'
    GREATEROREQ = r'>='
    LESSEROREQ = r'<='

    @_(r'\d+') # one or more digits
    def NUMBER(self, t): # converting to python number
        t.value = int(t.value)
        return t # returning token

    @_(r'#.*') # comments starts with # symbol
    def COMMENT(self, t):
        pass # passing to ignore

    @_(r'\n+') # if we see new line, we increment line number variable
    def newline(self,t ):
        self.lineno = t.value.count('\n') # it's only to tell what line error accured on

class LitParser(Parser):
    tokens = BasicLexer.tokens # passing tokens from lexer to parser

    precedence = (
        ('left', GREATER, LESSER, GREATEROREQ, LESSEROREQ, EQEQ),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.env = { }

    @_('') # if empty, do nothing
    def statement(self, p):
        pass

    @_('CIKLAS "(" var_assign IKI expr ")" "{" statement "}"') # loop satement
    def statement(self, p):
        return ('for_loop', ('for_loop_setup', p.var_assign, p.expr), p.statement) # (root, first child, second child)

    @_('JEIGU "(" condition ")" TADA statement KITAIP statement') # if statement
    def statement(self, p):
        return ('if_stmt', p.condition, ('branch', p.statement0, p.statement1))

    @_('FUN NAME "(" ")" ARROW statement') # function statement
    def statement(self, p):
        return ('fun_def', p.NAME, p.statement)

    @_('NAME "(" ")"')
    def statement(self, p):
        return ('fun_call', p.NAME)

    @_('expr EQEQ expr') # equals condition
    def condition(self, p):
        return ('condition_eqeq', p.expr0, p.expr1)

    @_('expr GREATER expr') # greater condition
    def condition(self, p):
        return ('condition_greater', p.expr0, p.expr1)

    @_('expr LESSER expr') # less condition
    def condition(self, p):
        return ('condition_lesser', p.expr0, p.expr1)

    @_('expr GREATEROREQ expr') # greater or equal condition
    def condition(self, p):
        return ('condition_greateroreq', p.expr0, p.expr1)

    @_('expr LESSEROREQ expr') # less or equal condition
    def condition(self, p):
        return ('condition_lesseroreq', p.expr0, p.expr1)

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('KINTAMASIS NAME "=" expr') # assign expression
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('KINTAMASIS NAME "=" STRING') # assign string
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)

    @_('expr')
    def statement(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('SPAUSDINTI "(" NAME ")"')
    def expr(self, p):
        return ('var', p.NAME)

    @_('SPAUSDINTI "(" NUMBER ")"')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('SPAUSDINTI "(" STRING ")"')
    def expr(self, p):
        return ('str', p.STRING)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)



class LitExecute:

    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree) # recursively calling tree node
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'str':
            return node[1]

        if node[0] == 'if_stmt':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[2][1])
            return self.walkTree(node[2][2])

        if node[0] == 'condition_greater':
            return self.walkTree(node[1]) > self.walkTree(node[2])

        if node[0] == 'condition_lesser':
            return self.walkTree(node[1]) < self.walkTree(node[2])

        if node[0] == 'condition_greateroreq':
            return self.walkTree(node[1]) >= self.walkTree(node[2])

        if node[0] == 'condition_lesseroreq':
            return self.walkTree(node[1]) <= self.walkTree(node[2])

        if node[0] == 'condition_eqeq':
            return self.walkTree(node[1]) == self.walkTree(node[2])

        if node[0] == 'fun_def':
            self.env[node[1]] = node[2]

        if node[0] == 'fun_call':
            try:
                return self.walkTree(self.env[node[1]])
            except LookupError:
                print("Undefined function '%s'" % node[1])
                return 0

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0

        if node[0] == 'for_loop':
            if node[1][0] == 'for_loop_setup':
                loop_setup = self.walkTree(node[1])

                loop_count = self.env[loop_setup[0]]
                loop_limit = loop_setup[1]

                for i in range(loop_count+1, loop_limit+1):
                    res = self.walkTree(node[2])
                    if res is not None:
                        print(res)
                    self.env[loop_setup[0]] = i
                del self.env[loop_setup[0]]

        if node[0] == 'for_loop_setup':
            return (self.walkTree(node[1]), self.walkTree(node[2]))


if __name__ == '__main__':
    lexer = LitLexer()
    parser = LitParser()
    env = {}
    while True: # infinite loop
        try:
            text = input('Lit-- > ') # get input from the user
        except EOFError:
            break
        if text: # if input is ok
           tree = parser.parse(lexer.tokenize(text)) # passing input to the lexer
           LitExecute(tree, env)
           #print(tree)