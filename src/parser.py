from sly import Parser
import rules
from lexer import WtfLexer

class WtfParser(Parser):
    tokens = WtfLexer.tokens

    precedence = (
        ('nonassoc', 'CMP_EQ', 'CMP_NEQ', 'CMP_LE', 'CMP_GE', '<', '>'),
        ('left', '+', '-')
    )

    # overall program structure
    @_('command program')
    def program(self, p): return [p.command] + p.program
    @_('empty')
    def program(self, p): return []

    # code blocks
    @_('"{" program "}"')
    def code_block(self, p): return rules.CodeBlock(p.program)

    # commands
    @_('command_nosemi ";"', 'command_nosemi_val')
    def command(self, p): return p[0]
    @_('command_nosemi_inv') #TODO add support for all commands
    def command_nosemi(self, p): return p[0]

    # commands that are valid top-level only with a semicolon
    @_('assignment', 'declaration', 'func_call')
    def command_nosemi_inv(self, p): return p[0]
    # commands that are valid top-level even without a semicolon
    @_('control_stmt', 'code_block')
    def command_nosemi_val(self, p): return p[0]

    
    # control statements
    @_('KW_IF "(" expr ")" command')
    def control_stmt(self, p): return rules.ControlStmt('if', p.expr, (p.command, None))
    @_('KW_IF "(" expr ")" command KW_ELSE command')
    def control_stmt(self, p):
        return rules.ControlStmt('if', p.expr, (p.command0, p.command1))
    @_('KW_WHILE "(" expr ")" command')
    def control_stmt(self, p): return rules.ControlStmt('while', p.expr, p.command)
    @_('KW_FOR "(" command expr ";" command_nosemi ")" command')
    def control_stmt(self, p):
        return rules.ControlStmt('for', (p.command0, p.expr, p.command_nosemi), p.command1)
    @_('KW_REPEAT "(" expr ")" command')
    def control_stmt(self, p): return rules.ControlStmt('repeat', p.expr, p.command)

    # variable declaration and assignment
    @_('KW_VAR ID')
    def declaration(self, p): return rules.Declaration(p.ID, None)
    @_('KW_VAR ID "=" expr')
    def declaration(self, p): return rules.Declaration(p.ID, p.expr)
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
#    @_('expr bin_op expr')
    @_('expr "+" expr', 'expr "-" expr', 'expr CMP_EQ expr', 'expr CMP_NEQ expr',
        'expr "<" expr', 'expr ">" expr', 'expr CMP_LE expr', 'expr CMP_GE expr')
    def expr(self, p):
        return rules.BinaryOp(p[1], p.expr0, p.expr1)
    @_('term')
    def expr(self, p): return p.term

#    @_('"+"', '"-"', 'CMP_EQ', 'CMP_NEQ', 'CMP_LE', 'CMP_GE', '"<"', '">"')
#    def bin_op(self, p): return p[0]

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
