# WTF
WTF is a language that compiles into Brainfuck.
It is very much a work in progress, so anything might change.

This document contains general information about the project and the compiler. If you want to read about the language itself, see _LANGUAGE.md_.
If you want to get information abou the inner workings of the implementation, see _DEVNOTES.md_.

## Tooling
Since the project is in a very basic stage, the compiler (`src/compiler.py`) only works on standard IO and does not accept any arguments.
There is a convenience script `compile.sh`, which compiles a file called `test.wtf` into `test.bf` and runs it using `beef`.

The compiler can add debug information into the output.
This behavior can be controlled with the variable `enableDebug` in the Machine class located in the file `src/compiler.py`.

## Error detection and handling
Errors in the program are not handled properly and they might go undetected.
If the compiled program doesn't work as it should, you have to inspect the source code or the generated brainfuck code with debug messages enabled.

## Thank you
I would like to thank David Beazley for the amazing tool [SLY](https://github.com/dabeaz/sly) which powers the lexical analyser and parser of WTF.
The license of SLY can be seen [here](https://github.com/dabeaz/sly/blob/master/LICENSE).
