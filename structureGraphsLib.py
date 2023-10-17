from tokenTypesDefinitionLib import *

# credit for ideas:
# https://medium.com/@phanindramoganti/regex-under-the-hood-implementing-a-simple-regex-compiler-in-go-ef2af5c6079
# https://www.python.org/doc/essays/graphs/
# fsm designer for documentation: https://madebyevan.com/fsm/

# constants to use in the third slot of an edge tuple, recording whether and how the edge should be captured
NO_CAPTURE = "not captured"
CAPTURE_ALONE = "captured on it's own"
CAPTURE_TOGETHER = "captured alongside any others adjacent also selected as capture together"

# structure graphs are a finite state machine graph that is traversed to detect if a token list is valid and, if it is, what its node type and capture groups are
# It is structured like so:
# Base List: AST node type, graph list
# Graph List: Starting Node, Ending Node, Main Graph Dictionary
# Main Graph Dictionary: Node name and edge list pairs
# Node Edge Lists: Lists containing Tuples of each valid edge
# Node Edge Tuples: Connecting node name, valid token type, capture parameter 


structure_graphs = [
    [ARRAY,
        [
            'A',
            'E',
            {
                'A':[('C', OPENING_SQUARE_BRACKET, NO_CAPTURE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', CLOSING_SQUARE_BRACKET, NO_CAPTURE), ('B', COMMA, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [TUPLE,
        [
            'A',
            'E',
            {
                'A':[('C', OPENING_TRIANGLE_BRACKET, NO_CAPTURE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', CLOSING_TRIANGLE_BRACKET, NO_CAPTURE), ('B', COMMA, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [DICTIONARY,
        [
            'A',
            'D',
            {
                'A':[('B', OPENING_CURLED_BRACKET, NO_CAPTURE)],
                'B':[('C', CLOSING_CURLED_BRACKET, NO_CAPTURE), ('B', COMMA, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', END, NO_CAPTURE)],
                'D':None
            }
        ]
    ],
    # Surrounding brackets
    [BRACKETS,
        [
            'A',
            'E',
            {
                'A':[('B', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    # Assigns a value to a pre-existing variable
    [ASSIGNMENT,
        [
            'A',
            'E',
            {
                'A':[('B', NAME_KEYWORD, CAPTURE_ALONE)],
                'B':[('C', EQUALS, NO_CAPTURE)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    # Assigns a value to new variable
    [DECLARATION_NORMAL_WITH_VALUE,
        [
            'A',
            'F',
            {
                'A':[('B', DECLARATIVE_KEYWORDS_VALUE, CAPTURE_ALONE)],
                'B':[('C', NAME_KEYWORD, CAPTURE_ALONE)],
                'C':[('D', EQUALS, NO_CAPTURE)],
                'D':[('E', ANY, CAPTURE_TOGETHER)],
                'E':[('F', END, NO_CAPTURE), ('E', ANY, CAPTURE_TOGETHER)],
                'F':None
            }
        ]
    ],
    [DECLARATION_NORMAL_WITHOUT_VALUE,
        [
            'A',
            'D',
            {
                'A':[('B', DECLARATIVE_KEYWORDS_NO_VALUE, CAPTURE_ALONE)],
                'B':[('C', NAME_KEYWORD, CAPTURE_ALONE)],
                'C':[('D', END, NO_CAPTURE)],
                'D':None
            }
        ]
    ],
    [IF_STATEMENT,
        [
            'A',
            'E',
            {
                'A':[('B', IF, NO_CAPTURE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', DO, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [WHILE_STATEMENT,
        [
            'A',
            'E',
            {
                'A':[('B', WHILE, NO_CAPTURE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', DO, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [FOR_STATEMENT,
        [
            'A',
            'G',
            {
                'A':[('B', FOR, NO_CAPTURE)],
                'B':[('C', NAME_KEYWORD, CAPTURE_ALONE)],
                'C':[('D', IN, NO_CAPTURE)],
                'D':[('E', ANY, CAPTURE_TOGETHER)],
                'E':[('F', DO, NO_CAPTURE), ('E', ANY, CAPTURE_TOGETHER)],
                'F':[('G', END, NO_CAPTURE)],
                'G':None

            }
        ]
    ],
    [OUTPUT_CALL,
        [
            'A',
            'F',
            {
                'A':[('B', OUTPUT, NO_CAPTURE)],
                'B':[('C', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('C', COMMA, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':[('F', END, NO_CAPTURE)],
                'F':None
            }
        ]
    ],
    [LENGTH_CHECK,
        [
            'A',
            'F',
            {
                'A':[('B', LENGTH, NO_CAPTURE)],
                'B':[('C', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':[('F', END, NO_CAPTURE)],
                'F':None
            }
        ]
    ],
    [STRING_LIST_READ_BY_INDEX,
        [
            'A',
            'H',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', STRING_LIST_READ_BY_INDEX, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [ARRAY_APPEND,
        [
            'A',
            'H',
            {
                'A':[('B', NAME_KEYWORD, CAPTURE_ALONE)],
                'B':[('C', DOT, NO_CAPTURE)],
                'C':[('D', APPEND, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [PRIORITY_QUEUE_ADD_ITEM,
        [
            'A',
            'J',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ADD_ITEM, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', COMMA, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', ANY, CAPTURE_TOGETHER)],
                'H':[('I', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('H', ANY, CAPTURE_TOGETHER)],
                'I':[('J', END, NO_CAPTURE)],
                'J':None
            }
        ]
    ],
    [STACK_QUEUE_ADD_ITEM,
        [
            'A',
            'H',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ADD_ITEM, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [STACK_QUEUE_ITEM_READ,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', READ_ITEM, NO_CAPTURE)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [STACK_QUEUE_ITEM_POP,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', POP_ITEM, NO_CAPTURE)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [DICTIONARY_INSERT,
        [
            'A',
            'H',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', INSERT_PAIR, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [DICTIONARY_LOOKUP,
        [
            'A',
            'H',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', LOOKUP_VALUE, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [DICTIONARY_REMOVE,
        [
            'A',
            'H',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', REMOVE_PAIR, NO_CAPTURE)],
                'D':[('E', OPENING_CURVED_BRACKET, NO_CAPTURE)],
                'E':[('F', ANY, CAPTURE_TOGETHER)],
                'F':[('G', CLOSING_CURVED_BRACKET, NO_CAPTURE), ('F', ANY, CAPTURE_TOGETHER)],
                'G':[('H', END, NO_CAPTURE)],
                'H':None
            }
        ]
    ],
    [DICTIONARY_KEY_LIST,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DOT, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', LIST_KEYS, NO_CAPTURE)],
                'D':[('E', END, NO_CAPTURE)],
                'E':None
            }
        ]
    ],
    [DICTIONARY_PAIR,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', COLON, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [BINARY_BOOLEAN_LOGICAL_STATEMENT,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', BINARY_BOOLEAN_LOGIC_KEYWORDS, CAPTURE_ALONE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [SINGLE_BOOLEAN_LOGICAL_STATEMENT,
        [
            'A',
            'D',
            {
                'A':[('B', SINGLE_BOOLEAN_LOGIC_KEYWORDS, CAPTURE_ALONE)],
                'B':[('C', ANY, CAPTURE_TOGETHER)],
                'C':[('D', END, NO_CAPTURE), ('C', ANY, CAPTURE_TOGETHER)],
                'D':None
            }
        ]
    ],
    [BOOLEAN_COMPARISON,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', ALL_BOOLEAN_COMPARATORS, CAPTURE_ALONE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [SUBTRACTION,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', MINUS, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [CONCATENATION_OR_ADDITION,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', PLUS, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [MULTIPLICATION,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', MULTIPLY, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [DIVISION,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', DIVIDE, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [INTEGER_DIVISION,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', INTEGER_DIVIDE, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
    [MODULO_DIVIDE,
        [
            'A',
            'E',
            {
                'A':[('B', ANY, CAPTURE_TOGETHER)],
                'B':[('C', MODULO, NO_CAPTURE), ('B', ANY, CAPTURE_TOGETHER)],
                'C':[('D', ANY, CAPTURE_TOGETHER)],
                'D':[('E', END, NO_CAPTURE), ('D', ANY, CAPTURE_TOGETHER)],
                'E':None
            }
        ]
    ],
]