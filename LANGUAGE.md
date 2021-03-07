# WTF - language documentation
Each command ends with a semicolon. Comments start with a hash `#`.

## Variables
Variables must be declared with `var` first.

Examples:
```wtf
var foo;      #just declaration
var bar = 1;  #declaration with assignment
foo = 12 + 8; #assignment
baz = 'a';    #ERROR - undeclared variable
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

## Conditions and loops
### If
An if statement is written like `if (condition) do_something` or like `if (condition) do_something else do_something`, where `do_something` is either a code block (`{ command; command; ... }`) or a single command.
Please note that, like in C, if the _if_'s body is a single command, it must end with a semicolon `;`.

Examples:
```wtf
# if statement with a single command
if (1)
	prints("Hello"); 

# if statement with multiple commands
if (2 + 2 == 5) {
	prints("yo what the hell");
	print(2 + 2);
}

# if statement with an else branch
if (read() == 'y')
	prints("yes");  #note the semicolon
else
	prints("no");
```

### While
Example:
```wtf
# while loop - counts from 0 to 9
var i = 0;
while (i != 10) {
	print(i + '0');
	print('\n');

	i = i + 1;
}
```

### For
For loops work like in any other C-like language. There is no support for _foreach_ loops.

```wtf
for (var i = 0; i != 10; i = i+1) {
	print(i + '0');
	print(' ');
}
```

If you just want to repeat a block of code several times, it is better to use the `repeat` loop because it is more efficient.

### Repeat
`repeat (n) command` repeats a _command_ _n_ times. It is more efficient than a regular for loop because it doesn't need to evaluate a lot of expressions that are needed in a for loop.

Example:
```wtf
# prints "hello" 10 times
repeat(10) {
	prints("hello");
	print('\n');
}

# prints a hyphen given nuber of times
prints("Enter a digit: ");
repeat(read() - '0')
	print('-');
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
