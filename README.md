# BigLang-Language-Interpreter
A modified version of my programming language interpreter written in Python. I created this for my Computer Science A-level Coursework.

The language is based loosely on the pseudocode style of writing algorithms, nicknamed BIGLANG (.bl). It supports most basic procedural programming language features.
This includes:
- Variables (including local variables and allowing for multiple variables in different domains with the same identifier)
- Multiple basic pre-defined types and typeclasses (i.e. numbers includes integers and floats
- Many advanced data structures including lists, tuples, dictionaries, stacks and queues
- if-then-else statements
- while statements

To do this I implemented a couple sub-sections of the program to pass values around and manipulate them:
- Lexer - processes a string of text into a list of tokens that represents the line
- Parser - takes a list of a lexed string and produces an abstract syntax tree (AST) which represents the structure of the code line. This uses finite state automata to recognise patterns that form operation syntax
- Processor - consolidates an AST by carrying out each operation
- Virtual environment - used by the processor to store and modify variables as virtual variable datatypes. Variables and other information are stored here in a call stack
- Top level flow management - deals with conditionals and loops passed out to it by the processor to decide which line should be run next. Stores its information by creating, reading and destroying stack frames on the call stack

Extensive documentation which was made for the coursework is available on request. 
