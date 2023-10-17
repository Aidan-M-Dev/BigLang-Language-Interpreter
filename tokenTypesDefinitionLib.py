# ------------------------------ TOKEN CLASS ------------------------------ #

import copy
# __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
# by: https://stackoverflow.com/users/541136/russia-must-remove-putin

# The token class has two variables. The type, which signals what to be done with it and a value, 
# which is called if it is a type that can have a value (like an integer)
class Token:
    def __init__(self, type, value):
        # Token types are constants defined in the tokenTypesDefinitionLib.py library
        self.type = type
        # The value used for a token may be the value of a data type in string format 
        # or the text equivalent
        # Those whose values are not actually strings will be converted to 
        # their proper representation when they are processed by the virtual environment
        self.value = value
    
    # __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.type, memo),
                copy.deepcopy(self.value, memo))
            memo[id_self] = _copy 
        return _copy
    
    # Code to allow Token to be printed for error messages and debugging purposes
    def __str__(self):
        return f"Token({self.type}, {self.value})"
    def __repr__(self):
        return self.__str__()


# ------------------------------ TOKEN TYPES ------------------------------ #

# defining token types so they can be written as 'INTEGER' instead of '"integer"'
# the values of these are only used in error messages
# token types are used for comparison e.g. token.type == INTEGER
# also defining useful groups of token types for easy checking

# END
# end of a token list
END = "end of list"

# ANY
# represents any token, used in parser
ANY = "any token"

# NUMBERS
INTEGER = "integer value"
# float has a decmial type which will then be converted into a float, 
# in the virtual environment
DECIMAL_NUMBER = "decimal number value"
FLOAT = "float value"

# CHARACTER-BASED
CHARACTER = "character value"
# string exists as its value until the virtual environment, where it is turned 
# into an array of characters
STRING = "string value"

# BOOLEAN VALUES
BOOLEAN = "boolean value"

# DECLARATIVE KEYWORDS
DECLARE_INTEGER = "integer declarator"
DECLARE_FLOAT = "floating point declarator"
DECLARE_CHARACTER = "character declarator"
DECLARE_STRING = "string declarator"
DECLARE_BOOLEAN = "boolean declarator"
DECLARE_ARRAY = "array declarator"
DECLARE_TUPLE = "tuple declarator"
DECLARE_DICT = "dictionary declarator"
DECLARE_STACK = "stack declarator"
DECLARE_QUEUE = "queue declarator"
DECLARE_PRIORITY_QUEUE = "priority queue declarator"

# just includes all of these
# STATEMENT KEYWORDS
DO = "do keyword"
IF = "if keyword"
ELSE = "else keyword/root node opening the else part of an if statement"
END_IF = "end if keyword/root node ending an if statement"
WHILE = "while keyword"
END_WHILE = "end while keyword/root node ending a while statement"
FOR = "for keyword"
IN = "in keyword"
END_FOR = "end for keyword/root node ending a for statement"
# for methods
DEFINE = "define keyword"
END_DEFINE = "end define keyword/root node ending a subroutine definition/call"

OUTPUT = "data output keyword"

# BOOLEAN LOGIC KEYWORDS
AND = "and keyword"
OR = "or keyword"
NOT = "not keyword"

# RESERVED KEYWORDS
APPEND = "array append"
LENGTH = "length"
ADD_ITEM = "stack/queue add item"
READ_ITEM = "stack/queue/PRIORITY_QUEUE read item"
POP_ITEM = "stack/queue/PRIORITY_QUEUE pop item"
INSERT_PAIR = "dictionary insert pair"
LOOKUP_VALUE = "dictionary lookup value"
REMOVE_PAIR = "dictionary remove pair"
LIST_KEYS = "dictionary list keys"

# NAME KEYWORDS
NAME_KEYWORD = "name keyword (variable or method name)"

# SYNTAX SYMBOLS
COMMA = "comma"
COLON = "colon"
DOT = "dot/full stop"
OPENING_CURVED_BRACKET = "opening curved bracket"
CLOSING_CURVED_BRACKET = "closing curved bracket"
OPENING_SQUARE_BRACKET = "opening square bracket"
CLOSING_SQUARE_BRACKET = "closing square bracket"
OPENING_CURLED_BRACKET = "opening curled bracket"
CLOSING_CURLED_BRACKET = "closing curled bracket"
OPENING_TRIANGLE_BRACKET = "opening triangle bracket"
CLOSING_TRIANGLE_BRACKET = "closing triangle bracket"

# RESERVED OPERATORS
EQUALS = "equals"
PLUS = "plus"
MINUS = "minus"
MULTIPLY = "multiply"
DIVIDE = "divide"
MODULO = "modulo"
INTEGER_DIVIDE = "integer divide"
IS_LESS_THAN = "less than"
IS_GREATER_THAN = "greater than"
IS_LESS_THAN_OR_EQUAL_TO = "less than or equal to"
IS_GREATER_THAN_OR_EQUAL_TO = "greater than or equal to"
IS_EQUAL_TO = "is equal to"
IS_NOT_EQUAL_TO = "is not equal to"

# ANYTHING BELOW THIS POINT IS USED IN THE AST BUT NOT IN THE LEXER

# COMPLEX DATA STRUCTURES
ARRAY = "Array value"
TUPLE = "Tuple value"
STACK = "Stack value"
QUEUE = "Queue value"
PRIORITY_QUEUE = "Priority queue value"
DICTIONARY = "Dictionary value"

# ROOT NODE TOKEN TYPES
OPEN_IF = "root node opening an if statement"
SKIP_IF = "root node skipping the contents of an if statement"
OPEN_WHILE = "root node opening a while statement"
SKIP_WHILE = "root node skipping the contents of a while statement"
OPEN_FOR = "root node opening a for statement"
SKIP_FOR = "root node skipping the contents of a while statement"
OPEN_DEFINE = "root node opening a subroutine definition"
RETURN = "root node closing a subroutine call"
OUTPUT_REQUEST = "root node requesting the output of a value"

INVALID = "token used to indicate if a root node output is invalid but that there is a root node there"

# VIRTUAL VARIABLES
# tokens which contain virtual variables as values
VIRTUAL_INTEGER = "integer virtual variable"
VIRTUAL_FLOAT = "float virtual variable"
VIRTUAL_STRING = "string virtual variable"
VIRTUAL_CHARACTER = "character virtual variable"
VIRTUAL_BOOLEAN = "boolean virtual variable"
VIRTUAL_TUPLE = "tuple virtual variable"
VIRTUAL_ARRAY = "array virtual variable"
VIRTUAL_STACK = "stack virtual variable"
VIRTUAL_QUEUE = "queue virtual variable"
VIRTUAL_PRIORITY_QUEUE = "priority queue virtual variable"
VIRTUAL_DICTIONARY = "dictionary virtual variable"
VIRTUAL_DICTIONARY_PAIR = "dictionary pair virtual variable"

BRACKETS = "Surrounding brackets"
ASSIGNMENT = "Assignment"
DECLARATION_NORMAL_WITH_VALUE = "Normal declaration with a value"
DECLARATION_NORMAL_WITHOUT_VALUE = "Normal declaration without a value"

IF_STATEMENT = "If statement"
WHILE_STATEMENT = "While statment"
FOR_STATEMENT = "For statement"
DEFINE_STATEMENT = "method definition"
RETURN_STATEMENT = "return statement"

METHOD_CALL = "Method call"

OUTPUT_CALL = "Output call"

# uses isequalto, isleassthan, etc
BOOLEAN_COMPARISON = "Boolean comparison"
# uses and, or, not
BINARY_BOOLEAN_LOGICAL_STATEMENT = "Binary boolean logical statement"
SINGLE_BOOLEAN_LOGICAL_STATEMENT = "Single boolean logical statement"

MULTIPLICATION = "Multiplication, supports integers and floats"
SUBTRACTION = "Subtraction, supports integers and floats"
MODULO_DIVIDE = "Integer-only division-related operation, %"
INTEGER_DIVISION = "Integer-only division operation, //"
DIVISION = "standard division operation, /"
CONCATENATION_OR_ADDITION = "Concatentation or addition"

STRING_LIST_READ_BY_INDEX = "String or list, read by index"
ARRAY_APPEND = "Array append"
DICTIONARY_PAIR = "Dictionary pair"
DICTIONARY_INSERT = "Dictionary insert"
DICTIONARY_LOOKUP = "Dictionary lookup"
DICTIONARY_REMOVE = "Dictionary remove"
DICTIONARY_KEY_LIST = "Dictionary keylist"
STACK_QUEUE_ADD_ITEM = "Stack or queue item add"
PRIORITY_QUEUE_ADD_ITEM = "Priority queue item add"
STACK_QUEUE_ITEM_READ = "Stack, queue or priority queue item read"
STACK_QUEUE_ITEM_POP = "Stack, queue or priority queue item pop"
LENGTH_CHECK = "Length check"

# SUMMARY LISTS
NUMBERS = [INTEGER, DECIMAL_NUMBER, FLOAT]

CHARACTER_BASED_VALUE = [CHARACTER, STRING]

ACTIONABLE_ROOT_NODE_TYPES = [OPEN_IF, SKIP_IF, ELSE, END_IF, OPEN_WHILE, SKIP_WHILE, END_WHILE, OPEN_FOR, SKIP_FOR, END_FOR, METHOD_CALL, OPEN_DEFINE, END, OUTPUT_REQUEST]
NON_ACTIONABLE_ROOT_NODE = "Root node which doesn't state an instruction for the main controller"
ROOT_NODE_TYPES = ACTIONABLE_ROOT_NODE_TYPES + [NON_ACTIONABLE_ROOT_NODE]

OPERATION_TYPE_TO_ROOT_NODE = {
    IF_STATEMENT : OPEN_IF,
    WHILE_STATEMENT : OPEN_WHILE,
    FOR_STATEMENT : OPEN_FOR,
    DEFINE_STATEMENT : OPEN_DEFINE
}

VIRTUAL_VARIABLE_TYPES = [VIRTUAL_INTEGER, VIRTUAL_FLOAT, VIRTUAL_STRING, VIRTUAL_CHARACTER, VIRTUAL_BOOLEAN, VIRTUAL_TUPLE, VIRTUAL_ARRAY, VIRTUAL_STACK, VIRTUAL_QUEUE, VIRTUAL_PRIORITY_QUEUE, VIRTUAL_DICTIONARY]

VIRTUAL_VARIABLE_TYPES_TO_BASIC_TYPES = {
    VIRTUAL_INTEGER : INTEGER,
    VIRTUAL_FLOAT : FLOAT,
    VIRTUAL_STRING : STRING,
    VIRTUAL_CHARACTER : CHARACTER,
    VIRTUAL_BOOLEAN : BOOLEAN,
    VIRTUAL_TUPLE : TUPLE,
    VIRTUAL_ARRAY : ARRAY,
    VIRTUAL_STACK : STACK,
    VIRTUAL_QUEUE : QUEUE,
    VIRTUAL_PRIORITY_QUEUE: PRIORITY_QUEUE,
    VIRTUAL_DICTIONARY: DICTIONARY
}

BASIC_TYPES_TO_VIRTUAL_VARIABLE_TYPES = {
    INTEGER : VIRTUAL_INTEGER,
    FLOAT : VIRTUAL_FLOAT,
    STRING : VIRTUAL_STRING,
    CHARACTER : VIRTUAL_CHARACTER,
    BOOLEAN : VIRTUAL_BOOLEAN,
    TUPLE : VIRTUAL_TUPLE,
    ARRAY : VIRTUAL_ARRAY,
    STACK : VIRTUAL_STACK,
    QUEUE : VIRTUAL_QUEUE,
    PRIORITY_QUEUE : VIRTUAL_PRIORITY_QUEUE,
    DICTIONARY : VIRTUAL_DICTIONARY
}

DECLARATIVE_KEYWORDS_NORMAL = [DECLARE_INTEGER, DECLARE_FLOAT, DECLARE_CHARACTER, DECLARE_STRING, DECLARE_BOOLEAN]
DECLARATIVE_KEYWORDS_LIST_BASED = [DECLARE_ARRAY, DECLARE_TUPLE, DECLARE_DICT]
DECLARATIVE_KEYWORDS_VALUE = DECLARATIVE_KEYWORDS_NORMAL + DECLARATIVE_KEYWORDS_LIST_BASED
DECLARATIVE_KEYWORDS_NO_VALUE = [DECLARE_STACK, DECLARE_QUEUE, DECLARE_PRIORITY_QUEUE]
DECLARATIVE_KEYWORDS = DECLARATIVE_KEYWORDS_VALUE + DECLARATIVE_KEYWORDS_NO_VALUE

STATEMENT_BEGINNING_KEYWORDS = [IF, WHILE, FOR, DEFINE]
STATEMENT_ENDING_KEYWORDS = [END_IF, END_WHILE, END_FOR, END_DEFINE]
STATEMENT_KEYWORDS = [DO, IN] + STATEMENT_BEGINNING_KEYWORDS + STATEMENT_ENDING_KEYWORDS

BINARY_BOOLEAN_LOGIC_KEYWORDS = [AND, OR]
SINGLE_BOOLEAN_LOGIC_KEYWORDS = [NOT]
BOOLEAN_LOGIC_KEYWORDS = BINARY_BOOLEAN_LOGIC_KEYWORDS + SINGLE_BOOLEAN_LOGIC_KEYWORDS
RESERVED_KEYWORDS = []

SYNTAX_SYMBOLS = [COMMA,COLON, OPENING_CURVED_BRACKET, CLOSING_CURVED_BRACKET, OPENING_SQUARE_BRACKET, CLOSING_SQUARE_BRACKET, 
OPENING_CURLED_BRACKET, CLOSING_CURLED_BRACKET, OPENING_TRIANGLE_BRACKET, CLOSING_TRIANGLE_BRACKET]

INTEGER_ONLY_OPERATORS = [MODULO, INTEGER_DIVIDE]
FLOAT_OPERATORS = [PLUS, MINUS, MULTIPLY, DIVIDE]
NUMBER_OPERATORS = INTEGER_ONLY_OPERATORS + FLOAT_OPERATORS

BOOLEAN_NUMERICAL_ONLY_COMPARATORS = [IS_LESS_THAN, IS_GREATER_THAN, IS_LESS_THAN_OR_EQUAL_TO, IS_GREATER_THAN_OR_EQUAL_TO]
BOOLEAN_UNIVERSAL_COMPARATORS = [IS_EQUAL_TO, IS_NOT_EQUAL_TO]
ALL_BOOLEAN_COMPARATORS = BOOLEAN_NUMERICAL_ONLY_COMPARATORS + BOOLEAN_UNIVERSAL_COMPARATORS

COMPLEX_DATA_STRUCTURES = [ARRAY, TUPLE, STACK, QUEUE, PRIORITY_QUEUE, DICTIONARY]

# all possible types for value tokens
VALUE_TYPES = NUMBERS + CHARACTER_BASED_VALUE + [BOOLEAN] + COMPLEX_DATA_STRUCTURES + [NAME_KEYWORD]

DECLARATION_TYPES_TO_BASIC_TYPES_DICT = {
    DECLARE_INTEGER : INTEGER,
    DECLARE_FLOAT : FLOAT,
    DECLARE_CHARACTER : CHARACTER,
    DECLARE_STRING : STRING,
    DECLARE_BOOLEAN : BOOLEAN,
    DECLARE_ARRAY : ARRAY,
    DECLARE_TUPLE : TUPLE,
    DECLARE_DICT : DICTIONARY,
    DECLARE_STACK : STACK,
    DECLARE_QUEUE : QUEUE,
    DECLARE_PRIORITY_QUEUE : PRIORITY_QUEUE
}