from sly import Parser
import rules
from lexer import WtfLexer

class WtfParser(Parser):
    tokens = WtfLexer.tokens

    precedence = (
        ('nonassoc', 'CMP_EQ', 'CMP_NEQ'),
        ('left', '+', '-')
    )

    # overall program structure
    @_('command ";" program')
    def program(self, p): return [p.command] + p.program
    @_('code_block program')
    def program(self, p): return [p.code_block] + p.program
    @_('empty')
    def program(self, p): return []

    # code blocks
    @_('"{" program "}"')
    def code_block(self, p): return rules.CodeBlock(p.program)

    # regular commands
    @_('assignment')
    def command(self, p): return p.assignment
    @_('func_call')
    def command(self, p): return p.func_call

    # assignment
    @_('ID "=" expr')
    def assignment(self, p): return rules.Assignment('=', p.ID, p.expr)

    # function calls
    @_('ID "(" func_call_params ")"')
    def func_call(self, p): return rules.FuncCall(p.ID, p.func_call_params)

    @_('func_call_params "," expr')
    def func_call_params(self, p): return p[0] + [p.expr]
    @_('expr')
    def func_call_params(self, p): return [p.expr]
    @_('empty')
    def func_call_params(self, p): return []

    # expressions
    @_('expr "+" expr', 'expr "-" expr',
        'expr CMP_EQ expr', 'expr CMP_NEQ expr')
    def expr(self, p):
        return rules.BinaryOp(p[1], p.expr0, p.expr1)
    @_('term')
    def expr(self, p): return p.term

    # `term` is for future use
    @_('factor')
    def term(self, p): return p.factor

    # TODO convert factors and terms to exprs and use a precedence table?
    # maybe merge all of these into a single function?
    @_('LIT_INT')
    def factor(self, p): return rules.Literal('int', p[0])
    @_('LIT_CHAR')
    def factor(self, p): return rules.Literal('char', p[0])
    @_('LIT_STR')
    def factor(self, p): return rules.Literal('str', p[0])
    @_('ID')
    def factor(self, p): return rules.Literal('id', p[0])
    @_('func_call')
    def factor(self, p): return p.func_call

    @_('"(" expr ")"')
    def expr(self, p): return p.expr

    @_('')
    def empty(self, p): pass

if __name__ == '__main__':
    string = ''
    line = input() + '\n'
    while True: 
        string += line
        try:
            line = input() + '\n'
        except EOFError:
            break

    tree = WtfParser().parse(WtfLexer().tokenize(string))

    for cmd in tree:
        print(cmd)
