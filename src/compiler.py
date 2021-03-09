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

    def init_variables(self, block):
        """
        Allocates space for the variables defined in a code block and returns
        a dict with their positions
        """

        ptr = self.tape_pos
        variables = {}

        for cmd in block.commands:
            if type(cmd) == rules.Declaration:
                if not cmd.name in variables:
                    variables[cmd.name] = ptr 
                    ptr += 1
                else:
                    raise Exception('Duplicit variable declaration (%s)' % cmd.name)
            

        self.goto_pos(ptr)
        return variables

    def _get_var_pos(vars, name):
        """Returns a variable's position on the tape"""
        for closure in vars:
            if name in closure:
                return closure[name]
        
        # variable not found
        raise Exception("Undeclared variable '%s'" % name)

    def eval_block(self, vars_, block):
        self.debug('<eval_block>')

        vars = [self.init_variables(block)] + vars_
        self.debug('variables: %s' % vars)

        for cmd in block.commands:
            if type(cmd) == rules.FuncCall:
                self.eval_func(vars, cmd)
            elif type(cmd) == rules.Assignment:
                self.assign(vars, cmd)
            elif type(cmd) == rules.Declaration and cmd.value:
                # declaration with assignment
                self.assign(vars, rules.Assignment('=', cmd.name, cmd.value))
            elif type(cmd) == rules.Declaration:
                pass
            elif type(cmd) == rules.CodeBlock:
                self.eval_block(vars, cmd)
            elif type(cmd) == rules.ControlStmt:
                self.eval_control(vars, cmd)
            else:
                raise Exception('Invalid command type: %s' % type(cmd))
        self.debug('</eval_block>')

    def eval_expr(self, vars, expr):
        self.debug('<eval_expr>: %s' % expr)

        if type(expr) == rules.Literal:
            self.bf_program += '[-]' #reset

            if expr.type == 'int':
                self.bf_program += '+' * expr.value
            elif expr.type == 'char':
                self.bf_program += '+' * ord(expr.value)
            elif expr.type == 'id':
                self.eval_id(vars, expr)
        elif type(expr) == rules.FuncCall:
            self.eval_func(vars, expr)
        elif type(expr) == rules.BinaryOp:
            self.eval_operation(vars, expr)

        self.debug('</eval_expr>')

    def eval_operation(self, vars, expr):
        self.debug('<eval_operation>: %s' % expr)

        def _eval_params():
            self.eval_expr(vars, expr.left)
            self.bf_program += '>'
            self.tape_pos += 1
            self.eval_expr(vars, expr.right)

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
            self.eval_func(vars, rules.FuncCall('normbool', [
                rules.BinaryOp('-', expr.left, expr.right)]))
        elif expr.op == '==': # '=='
            # equality is implemented through negated inequality
            self.eval_func(vars, rules.FuncCall('not', [
                rules.BinaryOp('!=', expr.left, expr.right)]))
        elif expr.op == '<=':
            # cell values: (result) (a) (b) 0 1
            #     numbers:    0      1   2  3 4

            # prepare the cell values
            self.bf_program += '[-]>'
            self.tape_pos += 1
            _eval_params()
            self.bf_program += '>>[-]>[-]+<<'
            self.tape_pos += 1
            # we are now on cell 2
            
            # this is for handling the case when a = 0. we set the result cell
            # to 1 (since (0 <= x) = true) and then surround the entirety of
            # the algorithm in [] so that it is run only when a != 0
            # at the start of the brackets, we set the result cell back to 0.
            self.bf_program += '<<+>[<->>'
            # we are now on cell 2

            # we start subtracting b from a. the [<] is run everytime except in
            # the case cell 1 (a) has reached 0. the whole [<]>> means that:
            #  - if cell 1 != 0, it shifts to cell 2
            #  - if cell 1 = 0, the [<] is not executed so we end up in cell 3,
            #    which is set to 0 and that ends the loop.
            # when we do [<, we will be shifted to the result cell (set to 0),
            # so we don't cause and infinite loop with the ].
            # the whole loop does this:
            #  - if we first reach 0 in cell 1 (a <= b), we end up in cell 3
            #  - if we first reach 0 in cell 2 (b < a), we end up in cell 2
            self.bf_program += '[-<- [<]>> ]'

            # we then shift one cell right, so that
            #  - if a <= b, we are in cell 4 (set to 1)
            #  - if a > b, we are in cell 3 (set to 0)
            # the code in brackets then only executes when we are in cell 4
            # = when a <= b. in the brackets, we set the result to 1 and shift
            # back to the 3rd cell so that we are in the same cell regardless on
            # where we were previously.
            self.bf_program += '>[ <<<<+ >>>]'

            # we shift to cell 0, set it to [-] so we don't cause an infinite
            # loop, end the brackets responsible for handling a = 0 and shift
            # to the result cell.
            self.bf_program += '<<[-]]<'
        elif expr.op == '>=':
            # (a >= b) === (b <= a)
            self.eval_operation(vars,
                rules.BinaryOp('<=', expr.right, expr.left))
        elif expr.op == '>':
            # (a > b) === !(a <= b)
            self.eval_func(vars, rules.FuncCall('not', [
                rules.BinaryOp('<=', expr.left, expr.right)
            ]))
        elif expr.op == '<':
            # (a < b) === !(a >= b) === !(b <= a)
            self.eval_func(vars, rules.FuncCall('not', [
                rules.BinaryOp('<=', expr.right, expr.left)
            ]))
        self.debug('</eval_operation>')

    def eval_id(self, vars, id):
        self.debug('<eval_id>: %s\n' % id)

        self.bf_program += '[-]>[-]<' #reset the cells we will be using
        pos = self.tape_pos #the starting position
        var_pos = Machine._get_var_pos(vars, id.value) #position of the variable

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

    def eval_func(self, vars, func):
        self.debug('<eval_func>: %s' % func)

        # TODO add a generic param length (and type?) check
        # user-defined functions not yet implemented
        if func.func == 'read':
            self.bf_program += ','
        elif func.func == 'print':
            if len(func.params) != 1:
                raise Exception('`print` accepts exactly one parameter')

            self.eval_expr(vars, func.params[0])
            self.bf_program += '.'
        elif func.func == 'prints':
            if len(func.params) != 1:
                raise Exception('`prints` accepts exactly one parameter')

            for char in func.params[0].value:
                self.eval_func(vars, rules.FuncCall('print',
                    [rules.Literal('char', char)]))
        elif func.func == 'normbool':
            if len(func.params) != 1:
                raise Exception('`normbool` accepts exactly one parameter')

            # normalize a boolean - if the value != 0, set it to exactly 1
            
            self.eval_expr(vars, func.params[0])
            # preparation
            self.bf_program += '>[-]<' 
            # if the cell != 0, set it to 0 and set the temporary value to 1
            self.bf_program += '[[-]>+<]'
            # set the cell's value to the value of the temporary bit
            self.bf_program += '>[-<+>]<'
        elif func.func == 'not':
            # invert a boolean value (must be exactly 0 or 1)
            self.eval_expr(vars, func.params[0])

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

    def eval_control(self, vars, stmt):
        self.debug('<eval_control> %s' % stmt)

        def _exec_as_block(cmd):
            if type(cmd) == rules.CodeBlock:
                self.eval_block(vars, cmd)
            else:
                self.eval_block(vars, rules.CodeBlock([cmd]))

        if stmt.type == 'if':
            self.eval_expr(vars, stmt.params)

            # set a cell next to the current one to 1. if the positive branch is
            # executed, we set this cell to 0 (at the end of the []). we then use
            # this cell to determine whether to execute the exit branch.
            self.bf_program += '>[-]+<['

            # command[0] = positive branch, command[1] = else branch
            
            _exec_as_block(stmt.command[0])
            
            # set the else flag to 0 and end the loop ([])
            self.bf_program += '>[-]< [-]]'

            # if the statement has an else branch, process it accordingly
            if stmt.command[1]:
                self.bf_program += '>[<'
                _exec_as_block(stmt.command[1])
                self.bf_program += '>[-]]<'
        elif stmt.type == 'while':
            self.eval_expr(vars, stmt.params)

            # self-explanatory
            self.bf_program += '[>'
            self.tape_pos += 1
            
            # if it isn't, enclose the while's body in a block
            if type(stmt.command) == rules.CodeBlock:
                self.eval_block(vars, stmt.command)
            else:
                self.eval_block(vars, rules.CodeBlock([stmt.command]))

            # evaluate the expression again and end the [] 
            self.bf_program += '<'
            self.tape_pos -= 1

            self.eval_expr(vars, stmt.params)
            self.bf_program += ']'
        elif stmt.type == 'for':
            cmd_block = None
            if type(stmt.command) == rules.CodeBlock:
                cmd_block = stmt.command
            else:
                cmd_block = rules.CodeBlock([stmt.command])

            # add the command that executes on each iteration
            cmd_block.commands += [stmt.params[2]]

            self.eval_block(vars, rules.CodeBlock([
                stmt.params[0], #initialization command
                rules.ControlStmt('while', stmt.params[1], cmd_block)
            ]))
        elif stmt.type == 'repeat':
            self.eval_expr(vars, stmt.params)

            # start the loop and shift right
            self.bf_program += '[>'
            self.tape_pos += 1

            _exec_as_block(stmt.command)

            # decrease the iteration cell
            self.bf_program += '<-]'
            self.tape_pos -= 1
        else:
            raise Exception('Invalid statement type `%s`' % stmt.type)

        self.debug('</eval_control>')

    def assign(self, vars, assignment):
        self.debug('<assign> %s' % assignment)

        var_pos = Machine._get_var_pos(vars, assignment.target)
        
        if assignment.op == '=':
            self.eval_expr(vars, assignment.expr)
            pos = self.tape_pos

            # reset the variable's value
            self.goto_pos(var_pos)
            self.bf_program += '[-]'
            self.goto_pos(pos)

            self.bf_program += '[-'
            self.goto_pos(var_pos)
            self.bf_program += '+'
            self.goto_pos(pos)
            self.bf_program += ']'
        else:
            raise Exception('Assignment type `%s` is invalid' % assignment.op)
        self.debug('</assign>')
        

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
    machine = Machine()
    #try:
    machine.eval_block([], rules.CodeBlock(wtf_prog))
    #except:
    #    pass  #only for debugging

    print(machine.bf_program)
