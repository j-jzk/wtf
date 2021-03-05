from parser import WtfParser
from lexer import WtfLexer
import rules

class Machine:
    """
    This class represents a machine that would execute the brainfuck code to do certain
    operations (but it saves it saves the code into a string)

    There is space at the beginning of the tape allocated for variables and the rest acts
    as a kind of a stack.
    Functions like eval_* and others do not actually return anything - again, the class
    doesn't execute any of the code, it just creates the brainfuck code that would be
    necessary to execute the instructions. The functions instead save the resulting value
    to the current cell.
    It is important that the functions must return the tape pointer to the position where
    it was at the start of the function.
    Functions do not clean up after themselves by default.
    """

    def __init__(self):
        self.bf_program = ''
        self.tape_pos = 0
        self.stack_ptr = 0
        self.variables = {}
        self.enableDebug = True
    
    def goto_pos(self, pos):
        """Goes to a specified position on the tape"""
        delta = pos - self.tape_pos
        
        if delta > 0:
            self.bf_program += '>' * delta
        else:
            self.bf_program += '<' * (-delta)

        self.tape_pos = pos

    def debug(self, msg):
        if self.enableDebug:
            self.bf_program += '\nDEBUG: tape@%d ' % self.tape_pos
            self.bf_program += msg.replace('[', '(').replace(']', ')') \
                .replace(',', ';').replace('.', '/') \
                .replace('!', '(?)') # beef (brainfuck interpreter) ignores everything after !
            self.bf_program += '\n'

    def eval_expr(self, expr):
        self.debug('<eval_expr>: %s' % expr)

        if type(expr) == rules.Literal:
            self.bf_program += '[-]' #reset

            if expr.type == 'int':
                self.bf_program += '+' * expr.value
            elif expr.type == 'char':
                self.bf_program += '+' * ord(expr.value)
            elif expr.type == 'id':
                self.eval_id(expr)
        elif type(expr) == rules.FuncCall:
            self.eval_func(expr)
        elif type(expr) == rules.BinaryOp:
            self.eval_operation(expr)

        self.debug('</eval_expr>')

    def eval_operation(self, expr):
        self.debug('<eval_operation>: %s' % expr)

        def _eval_params():
            self.eval_expr(expr.left)
            self.bf_program += '>'
            self.tape_pos += 1
            self.eval_expr(expr.right)

            self.bf_program += '<'
            self.tape_pos -= 1

        if expr.op == '+' or expr.op == '-':
            _eval_params()
            # add or subract the values
            self.bf_program += '> [-<%s>] <' % expr.op
        elif expr.op == '!=': # '!='
            # subtract the values.
            # if the resulting value is 0, the operands are equal => false (0)
            # if the value != 0, they are not equal => true (1)
            self.eval_func(rules.FuncCall('normbool', [
                rules.BinaryOp('-', expr.left, expr.right)]))
        elif expr.op == '==': # '=='
            # equality is implemented through negated inequality
            self.eval_func(rules.FuncCall('not', [
                rules.BinaryOp('!=', expr.left, expr.right)]))

        self.debug('</eval_operation>')

        

    def eval_id(self, id):
        self.debug('<eval_id>: %s\n' % id)

        if not id.value in self.variables:
            raise Exception('Undeclared identifier %s' % id.value)
        else:
            self.bf_program += '[-]>[-]<' #reset the cells we will be using
            pos = self.tape_pos #the starting position
            var_pos = self.variables[id.value] #position of the variable

            # destructively copy the var's value into two cells
            self.goto_pos(var_pos)
            self.bf_program += '[-'
            self.goto_pos(pos)
            self.bf_program += '+>+<'
            self.goto_pos(var_pos)
            self.bf_program += ']'
            self.goto_pos(pos + 1)

            # move one of the values back to the original place
            self.bf_program += '[-'
            self.goto_pos(var_pos)
            self.bf_program += '+'
            self.goto_pos(pos + 1)
            self.bf_program += '] <' #end loop and move back to the orig. position

            # set the position correctly (we moved 1 cell left manually)
            self.tape_pos -= 1
        self.debug('</eval_id>')

    def eval_func(self, func):
        self.debug('<eval_func>: %s' % func)

        # TODO add a generic param length (and type?) check
        # user-defined functions not yet implemented
        if func.func == 'read':
            self.bf_program += ','
        elif func.func == 'print':
            if len(func.params) != 1:
                raise Exception('`print` accepts exactly one parameter')

            self.eval_expr(func.params[0])
            self.bf_program += '.'
        elif func.func == 'prints':
            if len(func.params) != 1:
                raise Exception('`prints` accepts exactly one parameter')

            for char in func.params[0].value:
                self.eval_func(rules.FuncCall('print',
                    [rules.Literal('char', char)]))
        elif func.func == 'normbool':
            if len(func.params) != 1:
                raise Exception('`normbool` accepts exactly one parameter')

            # normalize a boolean - if the value != 0, set it to exactly 1
            
            self.eval_expr(func.params[0])
            # preparation
            self.bf_program += '>[-]<' 
            # if the cell != 0, set it to 0 and set the temporary value to 1
            self.bf_program += '[[-]>+<]'
            # set the cell's value to the value of the temporary bit
            self.bf_program += '>[-<+>]<'
        elif func.func == 'not':
            # invert a boolean value (must be exactly 0 or 1)
            self.eval_expr(func.params[0])

            # preparation
            self.bf_program += '>[-]+<'
            # if the value is 0, skip the loop and move the value from the tmp cell (1)
            # to the current cell
            # if the value is 1, set both of the cells to 0 and move the value from the
            # tmp cell (0) to the curr cell
            self.bf_program += '[->-<] >[-<+>]<'
        else:
            raise Exception('Function %s does not exist' % func.func)
        self.debug('</eval_func>')

    def assign(self, assignment):
        self.debug('<assign> %s' % assignment)

        if assignment.op == '=':
            self.eval_expr(assignment.expr)
            pos = self.tape_pos

            # reset the variable's value
            self.goto_pos(self.variables[assignment.target])
            self.bf_program += '[-]'
            self.goto_pos(pos)

            self.bf_program += '[-'
            self.goto_pos(self.variables[assignment.target])
            self.bf_program += '+'
            self.goto_pos(pos)
            self.bf_program += ']'
        else:
            raise Exception('Assignment type `%s` is invalid' % assignment.op)
        self.debug('</assign>')
        

class Compiler:
    def __init__(self, wtf_program):
        self.machine = Machine()
        self.wtf_program = wtf_program

    def init_variables(self):
        """Allocates space for the variables"""
        count = 0
        for cmd in self.wtf_program:
            if type(cmd) == rules.Assignment and not cmd.target in self.machine.variables:
                self.machine.variables[cmd.target] = count 
                count += 1

        self.machine.stack_ptr = count #set the stack beginning to the end of the var space
        self.machine.goto_pos(count)

    def compile(self):
        for cmd in self.wtf_program:
            if type(cmd) == rules.FuncCall:
                self.machine.eval_func(cmd)
            elif type(cmd) == rules.Assignment:
                self.machine.assign(cmd)


if __name__ == '__main__':
    string = ''
    line = input() + '\n'
    while True: 
        string += line
        try:
            line = input() + '\n'
        except EOFError:
            break

    wtf_prog = WtfParser().parse(WtfLexer().tokenize(string))
    comp = Compiler(wtf_prog)

    comp.init_variables()
    if comp.machine.enableDebug:
        comp.machine.debug('variables: %s' % comp.machine.variables)

    comp.compile()


    print(comp.machine.bf_program)
