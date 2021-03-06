class Assignment:
    def __init__(self, op, target, expr):
        self.op = op
        self.target = target
        self.expr = expr

    def __str__(self):
        return 'Assign: %s %s { %s }' % (self.target, self.op, self.expr)

class FuncCall:
    def __init__(self, func, params):
        self.func = func
        self.params = params

    def __str__(self):
        return 'Function call: %s, params: %s' % (self.func, self.params)

class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return 'Binary operation: { %s } %s { %s }' % (self.left, self.op, self.right)

class Literal:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return '%s: \'%s\'' % (self.type, self.value)

class CodeBlock:
    def __init__(self, commands):
        self.commands = commands

    def __str__(self):
        return 'Code block'

class Declaration:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        val_str = ''
        if self.value:
            val_str = ' = %s' % self.value

        return 'Variable declaration: %s%s' % (self.name, val_str)

class ControlStmt:
    def __init__(self, type, params, command):
        self.type = type
        self.params = params
        self.command = command

    def __str__(self):
        return 'Control statement: %s %s: %s' % (self.type, self.params, self.command)
