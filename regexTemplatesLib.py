from tokenTypesDefinitionLib import *


# TOKEN TYPE PATTERN RETRIEVAL AND COMPLETION
# used so the extra bits don't have to be included in the base templates
def get_template(pattern_key):
    # extracts the template from the template lists and adds a word ending 
    #   if the token type is a keyword
    if pattern_value := regex_templates_keywords.get(pattern_key):
        pattern_value += "\\b"
    else:
        pattern_value = regex_templates_non_keywords.get(pattern_key)
    if not pattern_value:
        raise Exception("No valid pattern")
    # these extra parts are applied to every pattern and do a couple of things:
    # a) '^' - ensures recognition is done from the begining of the string
    # b) '\s*' - burns off any whitespace before the pattern
    # c) '(.*)$ - takes the entire rest of the string and captures it for the 
    #   next round of processing
    pattern = f"^\s*{pattern_value}(.*)$"
    return pattern


# BASE REGEX TEMPLATES
# all templates for token types where a value needs to be extracted have a capture group 
# built into the template, the captured text will be detected by the lexer
regex_templates_non_keywords = {
    DECIMAL_NUMBER: "(-?[0-9]+\.[0-9]+)",
    INTEGER: "(-?[0-9]+)",
    # for char and string there are two cases: double quote mark and apostrophe quote 
    #   mark, they are represented in unicode for assurance of correct processing
    # this covers both, it is notable that each type of quote mark can be used in 
    #   the other's datatype without ramifications
    # ?: indicates that a bracketed group is not to be captured
    CHARACTER: "(?:\u0027([^\u0027])\u0027)",
    STRING: "(?:\u0022([^\u0022]*)\u0022)",
    COMMA: ",",
    COLON: ":",
    # \ is used as an escape character in regex for characters otherwise used in expressions
    DOT: "\.",
    OPENING_CURVED_BRACKET: "\(",
    CLOSING_CURVED_BRACKET: "\)",
    OPENING_SQUARE_BRACKET: "\[",
    CLOSING_SQUARE_BRACKET: "\]",
    OPENING_CURLED_BRACKET: "\{",
    CLOSING_CURLED_BRACKET: "\}",
    OPENING_TRIANGLE_BRACKET: "\<",
    CLOSING_TRIANGLE_BRACKET: "\>",
    INTEGER_DIVIDE: "\/\/",
    EQUALS: "=",
    PLUS: "\+",
    MINUS: "-",
    MULTIPLY: "\*",
    DIVIDE: "\/",
    MODULO: "%",
}

regex_templates_keywords = {
    # Booleans are included in this because their values are text-based in code
    BOOLEAN: "((?:TRUE)|(?:FALSE))",
    DECLARE_INTEGER: "INTEGER",
    DECLARE_FLOAT: "FLOAT",
    DECLARE_CHARACTER: "CHARACTER",
    DECLARE_STRING: "STRING",
    DECLARE_BOOLEAN: "BOOLEAN",
    DECLARE_ARRAY: "ARRAY",
    DECLARE_TUPLE: "TUPLE",
    DECLARE_DICT: "DICTIONARY",
    DECLARE_STACK: "STACK",
    DECLARE_QUEUE: "QUEUE",
    DECLARE_PRIORITY_QUEUE: "PRIORITYQUEUE",
    IF: "IF",
    ELSE: "ELSE",
    END_IF: "ENDIF",
    WHILE: "WHILE",
    END_WHILE: "ENDWHILE",
    FOR: "FOR",
    IN: "IN",
    DO: "DO",
    END_FOR: "ENDFOR",
    OUTPUT: "OUTPUT",
    AND: "AND",
    OR: "OR",
    NOT: "NOT",
    IS_EQUAL_TO: "ISEQUALTO",
    IS_NOT_EQUAL_TO: "ISNOTEQUALTO",
    IS_GREATER_THAN: "ISGREATERTHAN",
    IS_LESS_THAN: "ISLESSTHAN",
    IS_GREATER_THAN_OR_EQUAL_TO: "ISGREATERTHANOREQUALTO",
    IS_LESS_THAN_OR_EQUAL_TO: "ISLESSTHANOREQUALTO",
    LENGTH: "LENGTH",
    STRING_LIST_READ_BY_INDEX: "READBYINDEX",
    APPEND: "APPEND",
    ADD_ITEM: "ADDITEM",
    READ_ITEM: "READITEM",
    POP_ITEM: "POPITEM",
    INSERT_PAIR: "INSERTPAIR",
    LOOKUP_VALUE: "LOOKUPVALUE",
    REMOVE_PAIR: "REMOVEPAIR",
    LIST_KEYS: "LISTKEYS",
    # any of the valid characters for a name
    NAME_KEYWORD: "([a-zA-Z0-9_]+)"
}


# TESTING ORDER DEFINITION
to_test = [
    #numbers
    DECIMAL_NUMBER, 
    INTEGER,
    #string baseds
    CHARACTER,
    STRING,
    # syntax symbols
    COMMA,
    COLON,
    DOT,
    OPENING_CURVED_BRACKET,
    CLOSING_CURVED_BRACKET,
    OPENING_SQUARE_BRACKET,
    CLOSING_SQUARE_BRACKET,
    OPENING_CURLED_BRACKET,
    CLOSING_CURLED_BRACKET,
    OPENING_TRIANGLE_BRACKET,
    CLOSING_TRIANGLE_BRACKET,
    # reserved operators, starting with those using the most tokens characters
    INTEGER_DIVIDE,
    EQUALS,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    MODULO,
    # boolean value
    BOOLEAN,
    #declarative keywords
    DECLARE_INTEGER,
    DECLARE_FLOAT,
    DECLARE_CHARACTER,
    DECLARE_STRING,
    DECLARE_BOOLEAN,
    DECLARE_ARRAY,
    DECLARE_TUPLE,
    DECLARE_DICT,
    DECLARE_STACK,
    DECLARE_QUEUE,
    DECLARE_PRIORITY_QUEUE,
    # reserved keywords
    LENGTH,
    STRING_LIST_READ_BY_INDEX,
    APPEND,
    ADD_ITEM,
    READ_ITEM,
    POP_ITEM,
    INSERT_PAIR,
    LOOKUP_VALUE,
    REMOVE_PAIR,
    LIST_KEYS,
    # statement keywords
    DO,
    IF,
    ELSE,
    END_IF,
    WHILE,
    END_WHILE,
    FOR,
    IN,
    END_FOR,
    OUTPUT,
    # boolean logic keywords
    AND,
    OR,
    NOT,
    # boolean comparison keywords
    IS_EQUAL_TO,
    IS_NOT_EQUAL_TO,
    IS_GREATER_THAN,
    IS_LESS_THAN,
    IS_GREATER_THAN_OR_EQUAL_TO,
    IS_LESS_THAN_OR_EQUAL_TO,
    # name keywords
    NAME_KEYWORD
]