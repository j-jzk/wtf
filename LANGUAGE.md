# WTF - language documentation
Each command ends with a semicolon. Comments start with a hash `#`.

## Variables
Variables are declared automatically as they are defined.
(Note that this behavior might change with the future introduction of types).

You can set a variable like this:
```wtf
variable = value;
```

Variables don't currently have any datatypes and are simply pointers to different cells on the tape.

## Literals
- __Integers:__ written as regular numbers (for example `123`)
- __Characters:__ written in apostrophes (for example `'a'`). They are converted to numbers according to the ASCII table. They can contain escape sequences (like `\n`)
- __Strings:__ exist only for the sake of the function `prints` (see below). They are written in quotes (for example "hello") and no operations can be done on them. They can't contain escape sequences.

## Operators
### Arithmetic
WTF currently supports addition and subtraction.
```wtf
x = 2 + 2;      #x = 4
x = x - 3;      #x = 1
print(x + '0'); #prints the character '1'
```

### Comparisons
WTF currently supports the operators `==` and `!=`.
```wtf
x = 4 == 5;    #x = 0
x = 4 == 5-1;  #x = 1
x = 5 != 5;    #x = 0
x = 4 != 5;    #x = 1
```

### Parenthesis
Operator precedence can be overriden using parenthesis:
```wtf
x = 4 == 5 - 1;    #x = 4 == (5-1)   -> 4 == 4 -> 1
x = (4 == 5) - 1;  #x = (4 == 5) - 1 -> 1 - 1  -> 0
```

## Functions
Functions are called with parenthesis like this:
```wtf
read();
print('x');
func(variable, 'a', 123);
```

There is currently no support for user-defined functions.

### Built-in functions
- `print(what)`: prints a single value to the standard output. It depends on the brainfuck interperer you're using, but usually it is displayed as a character according to the ASCII table.
- `read()`: reads a single value from the standard input. Behaves similarly to the `print()` function in terms of encoding.
- `prints(string)`: a convenience function that prints out a string so you don't have to do `print('H'); print('e'); print('l'); ...`
- `normbool(value)`: normalizes a value into a boolean (exactly 1 or 0). If the value is 0, it returns 0 and if it is anything else, it returns 1.
- `not(bool)`: negates a boolean value (must be exactly 1 or 0).