from sly import Lexer

class WtfLexer(Lexer):
    # tokens
    tokens = {ID, LIT_CHAR, LIT_INT, LIT_STR, CMP_EQ, CMP_NEQ} 
    literals = {';', '=', '+', '-', '(', ')', ',', '!'}

    #@_(r'prints "[^"]*"')
    #def KW_PRINTS(self, t):
    #    t.value = t.value[7:-1]
    #    return t

    ID = '[a-zA-Z_][a-zA-Z0-9_]*'
    CMP_EQ = '=='
    CMP_NEQ = '!='

#    ID['read'] = KW_READ
#    ID['print'] = KW_PRINT

    @_(r'\d+')
    def LIT_INT(self, t):
        t.value = int(t.value)
        return t

    @_(r'\'(?:[^\\]|\\[abtnvfr\'\\])\'')
    def LIT_CHAR(self, t):
        # don't include the quotes and unescape the escape sequences
        t.value = t.value[1:-1].encode('utf-8').decode('unicode_escape')
        return t

    @_(r'"[^"]*"')
    def LIT_STR(self, t):
        t.value = t.value[1:-1]
        return t

    # line counter
    lineno = 1
    @_(r'\n+')
    def newline_counter(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print('Syntax error on line %d: invalid token %r' % (self.lineno, t.value))
        self.index += 1

    ignore = '\t '
    ignore_comment = r'\#.*'

if __name__ == '__main__':
    string = ''
    line = input() + '\n'
    while True: 
        string += line
        try:
            line = input() + '\n'
        except EOFError:
            break


    lex = WtfLexer()
    for token in lex.tokenize(string):
        print('type: %r, value: %r' % (token.type, token.value))