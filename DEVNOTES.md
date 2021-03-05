# Technical notes
## Parser
The parser converts the tokens created by the lexer to an abstract syntax tree.
The parser class should be reorganized and cleaned up in the future.

## Compiler
The compiler contains a class called Machine which acts as an abstraction layer.
You instruct it to do a certain action (assign a variable for example) and it generates the brainfuck code that would do the action.

The machine keeps an internal tape position variable. It must be set correctly in order to access the variables and do certain commands.
There is also a variable called `stack_ptr` which doesn't do anything useful.

At the start of the program, space is reserved at the beginning of the tape for the variables. The space after it is then used as a stack or a store for temporary values.
This will have to be modified in order to make local variables (in code blocks and functions) possible.


