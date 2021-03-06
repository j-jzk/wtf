# Technical notes
## Parser
The parser converts the tokens created by the lexer to an abstract syntax tree.
The parser class should be reorganized and cleaned up in the future.

## Compiler
The compiler contains a class called Machine which acts as an abstraction layer.
You instruct it to do a certain action (assign a variable for example) and it generates the brainfuck code that would do the action.

The machine keeps an internal tape position variable. It must be set correctly in order to access the variables and do certain commands.
There is also a variable called `stack_ptr` which doesn't do anything.

### Code blocks and variables
At the start of the program or a code block, the machine reserves space for the variables in that block.
The allocation function then returns a dict of positions of all the variables.
Functions that generate code then pass around a list of those dicts, each corresponding to a different nesting level.
The variable list is passed as a function parameter instead of an instance variable to make the future implementation of functions easier.

