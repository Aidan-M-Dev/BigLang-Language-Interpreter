# used in dictionaries
from math import log as logarithm

# to print things nicely for debugging!
from textwrap import indent

# defining values for all token types, enables easier coding and clearer debug messages
# also importing the token class, which is used as the primary data format across this program
from tokenTypesDefinitionLib import *

# regex library
import re

# used to get around python's passing by reference shenanigans
import copy


# ------------------------------ LEXER ------------------------------ #

# get_template produces the correct regex template for the inputted token
# to_test is a list of all tokens to test for in an optimum order/non-broken order for testing
from regexTemplatesLib import get_template, to_test

def process_text(my_line):
    # setting up variables
    # .strip() removes leading and trailing whitespace
    working_text = my_line.strip()
    token_list = []
    while len(working_text) != 0:
        # variables to be used to iterate through all the valid tokens
        token_type_index = 0
        found = False
        while token_type_index < len(to_test) and not found:
            # gets the next token type to check out of to test
            token_type = to_test[token_type_index]
            # calling a regex template from regexTemplatesLib
            pattern = get_template(token_type)
            # regex checking
            match_output = re.match(pattern, working_text)
            if match_output:
                # things to do if the regex matches
                match_capture_groups = match_output.groups()
                num_groups = len(match_capture_groups)
                # if the token is one without a specific value, the pattern will 
                # return one capture group: the rest of the line
                # if it has a value, the first group will be the value and the 
                # second the rest of the line
                if num_groups == 1:
                    new_token = Token(token_type, None)
                    working_text = match_capture_groups[0]
                elif num_groups == 2:
                    new_token = Token(token_type, match_capture_groups[0])
                    working_text = match_capture_groups[1]
                else:
                    # shouldn't be possible to have more than 2 capture groups
                    raise Exception(f"Too many captures: {match_capture_groups}")
                token_list.append(new_token)
                found = True
            token_type_index += 1
        # at this point all valid token formats have been checked for
        if not found:
            raise Exception(f"token not found for beginning of '{working_text}'")
    token_list.append(Token(END, None))
    return token_list


# ------------------------------ AST NODES ------------------------------ #
class Leaf_node:
    def __init__(self, token):
        # token will be of type token, which will define what type of value 
        # is held in the leaf node
        self.type = token.type
        self.value = token.value

    # prints out token when asked for str conversion or when printed
    # used for debugging and error messages
    def __str__(self):
        return f"({self.type}, '{self.value}')"
    def __repr__(self):
        return self.__str__()

class Operator_node:
    def __init__(self, operation, child_nodes):
        self.type = operation
        self.child_nodes = child_nodes
    
    # prints out the node type followed by every child node in brackets
    # used for debugging and error messages
    def __str__(self):
        output_string = f"{self.type}(\n"
        for node in self.child_nodes:
            stringed_node = indent(str(node), "   ")
            output_string += f"{stringed_node},\n"
        output_string+=")\n"
        return output_string
    def __repr__(self):
        return self.__str__()


# ------------------------------ PARSER ------------------------------ #
# base_token_list is a list of tokens which has been lexed which will 
#   be used to create the current node and any descendant nodes
# form_AST is applied recursively, with each pass using split_token_list
#   to break the token list into lists that will form a descendant tree
#   base case is any value token on its own, this will create a leaf node
def form_AST(base_token_list):
    # checking if this is an empty list
    if len(base_token_list) == 1:
        my_node = Leaf_node(Token("empty line", None))
    # checking if this is a leaf node, the last token in a token list will always
    #   be an END type so a single item list has length 2
    elif len(base_token_list) == 2:
        # creates a leaf node with token type and value of the remaining token
        final_token = base_token_list[0]
        my_node = Leaf_node(final_token)
    else:
        # operation_token is the token of this operator node
        # child_token_lists is a list of all the lists of tokens that are children 
        #   of this node
        operation, child_token_lists = split_token_list(base_token_list)
        child_nodes = []
        for token_list in child_token_lists:
            # takes each child list, recursively creates a descendant tree for it and 
            #   adds it to child_nodes
            new_node = form_AST(token_list)
            child_nodes.append(new_node)
        my_node = Operator_node(operation, child_nodes)
    return my_node

# Structure graphs are used to detect patterns for each valid operation and capture the 
#   correct information to create an AST node for it
from structureGraphsLib import *

def split_token_list(base_token_list):
    # setting up variables to iterate through the available structure graphs
    # when success is found to be true the iteration will immediately cease as the 
    #   correct formatting has been found
    structure_graphs_index = 0
    success = False
    while structure_graphs_index < len(structure_graphs) and not success:
        # setting up variables for traversing one structure graph
        # structure graph formatting notes can be found in structureGraphsLib.py
        structure = structure_graphs[structure_graphs_index]
        # structure[1][0] is the starting node
        current_node_name = structure[1][0]
        end_node_name = structure[1][1]
        main_graph = structure[1][2]
        current_node = main_graph.get(current_node_name)
        token_list_index = 0
        current_token = base_token_list[token_list_index]
        # captures are as so:
        # when a token is found under a CAPTURE_TOGETHER node, it is added to 
        #   the capture_buffer list
        # when a token is found under a CAPTURE_ALONE or NO_CAPTURE node, the 
        #   CAPTURE_TOGETHER list is placed (as one item) into the capture list, 
        #   followed by the new capture if it is a CAPTURE_ALONE node
        capture = []
        capture_buffer = []
        # Bracket counts are used for each capture buffer buildup. A left curved bracket 
        #   increases curved bracket count by one and a right curved bracket decreases it by one.
        # A capture buffer CANNOT be emptied and non-CAPTURE_TOGETHER nodes 
        #   cannot be processed until all bracket counts = 0
        # This ensures that groups enclosed by brackets cannot be separated during processing
        # The individual counts within the bracket count array are, in order, curved, square, 
        #   curled and triangle brackets
        bracket_counts = [0,0,0,0]
        # if a structure graph is designated not matching, failure is set to True and the code 
        #   quickly exits this loop to analyse against the next structure graph
        failure = False
        while not failure and not success:
            if current_node:
                # testing all valid edges for exiting the current node against the current token
                match = False
                index = 0
                while not match and index < len(current_node):
                    # checks if there is an inbalance of brackets or if this is a continuation of a 
                    # CAPTURE_TOGETHER group, then checks if type is correct
                    brackets_are_zero = all(counter == 0 for counter in bracket_counts)
                    if (brackets_are_zero or current_node[index][2] == CAPTURE_TOGETHER) and \
                        token_matches(current_token.type, current_node[index][1]):
                        match = True
                    else:
                        index += 1
                # carries out capture management and variable management if a valid exiting node exists
                if match:
                    capture_preference = current_node[index][2]
                    if capture_preference == CAPTURE_TOGETHER:
                        # managing bracket counts
                        current_token_type = current_token.type
                        if current_token_type == OPENING_CURVED_BRACKET:
                            bracket_counts[0] += 1
                        elif current_token_type == CLOSING_CURVED_BRACKET:
                            bracket_counts[0] -= 1
                        elif current_token_type == OPENING_SQUARE_BRACKET:
                            bracket_counts[1] += 1
                        elif current_token_type == CLOSING_SQUARE_BRACKET:
                            bracket_counts[1] -= 1
                        elif current_token_type == OPENING_CURLED_BRACKET:
                            bracket_counts[2] += 1
                        elif current_token_type == CLOSING_CURLED_BRACKET:
                            bracket_counts[2] -= 1
                        elif current_token_type == OPENING_TRIANGLE_BRACKET:
                            bracket_counts[3] += 1
                        elif current_token_type == CLOSING_TRIANGLE_BRACKET:
                            bracket_counts[3] -= 1
                        capture_buffer.append(current_token)
                    else:
                        # managing captures:
                        # empties the capture buffer as a new capture and inserts the latest value 
                        #   if it is classified as capture alone
                        if capture_buffer:
                            capture.append(capture_buffer + [Token(END, None)])
                            capture_buffer = []
                        if capture_preference == CAPTURE_ALONE:
                            capture.append([current_token] + [Token(END, None)])
                        elif capture_preference == NO_CAPTURE:
                            pass
                        else:
                            raise Exception(f"Invalid capture preference: {capture_preference}")
                    current_node_name = current_node[index][0]
                    current_node = main_graph.get(current_node_name)
                    # detecting if the graph has been completed
                    if current_node_name == end_node_name:
                        success = True
                    # detecting if out of tokens but graph is not yet completed
                    elif token_list_index == len(base_token_list)-1:
                        failure = True
                    else:
                        # making variables correct for next iteration since no completion state 
                        #   has been discovered
                        token_list_index += 1
                        current_token = base_token_list[token_list_index]
                else:
                    failure = True
            else:
                raise Exception(f"no node in {structure[0]} with code {current_node}")
        # move on to next structure graph
        if not success:
            structure_graphs_index += 1
    if not success:
        raise Exception(f"no valid pattern found for {base_token_list}")
    return structure_graphs[structure_graphs_index][0], capture

# Matches a string to another string or checks if it matches an item in a list 
# of strings, depending on what variable type is inputted as to_match
# In this project it is used to compare token types and lists of types from 
# tokenTypesDefinitionLib.py against each other
def token_matches(token_type, to_match):
    if to_match == ANY:
        answer = True
    elif type(to_match) == str:
        answer = (token_type == to_match)
    elif type(to_match) == list:
        answer = False
        for item in to_match:
            if item == token_type:
                answer = True
    return answer


# ------------------------------ VIRTUAL ENVIRONMENT ------------------------------ #

# --- Variable Implementation --- #

# Importing Virtual Environment Classes and the convert_to_virtual_variable method
from virtualEnvironmentClassesLib import *

# --- Stack Frames --- #

# these are types of stack frame, used to determine how they are handled by the virtual environment
# and to give information to the interpreter
BASE_FRAME = "Base frame type"
IF_FRAME = "If statement frame type"
WHILE_FRAME = "While statement frame type"
FOR_FRAME = "For statement frame type"

# a stack frame is an object used within a virtual environment's frame stack,
#   each frame added represents the entering of a clause or statement
#   and the removal of one represents the closing of it.
# Frames contain all variables that are declared within them and any information
#   about their looping or conditions regarding it.
# Depending on the type of frame, variable values may be preserved on frame
#   destruction by placing them in the frame below but this is not the case for 
#   define or call frames and for the iterated variable in a for frame.
class Stack_frame(object):
    # odd-looking __init__ is necessary so that deepcopy functions correctly
    def __init__(self, values, subroutines, frame_type, condition):
        if values == None:
            self.values = {}
            self.subroutines = {}
            self.type = frame_type
            self.condition = condition
        else:
            self.values = values
            self.subroutines = subroutines
            self.type = frame_type
            self.condition = condition

    # checks if the variable name is a variable in the stack frame
    def variable_in(self, name):
        if name in self.values.keys():
            return True

    # returns the value of the variable whose name is requested
    def read_item_value(self, name):
        if not self.variable_in(name):
            raise Exception(f"Variable {name} does not exist")
        else:
            return self.values[name]

    # set item can only change variables that already exist in the frame
    def set_item_value(self, item, name):
        if self.variable_in(name):
            self.values[name] = item
        else:
            raise Exception(f"Variable {name} does not exist")
    
    # make item creates a new variable in the frame, this cannot overwrite a 
    #   pre-existing one
    def make_item(self, item, name):
        if not self.variable_in(name):
            self.values[name] = item
        else:
            raise Exception(f"Variable {name} already exists")

    # removes a variable from the frame
    def remove_item(self, name):
        self.values.pop(name)

    def get_variable_names(self):
        return self.values.keys()

    # __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.values, memo),
                copy.deepcopy(self.subroutines, memo),
                copy.deepcopy(self.type, memo),
                copy.deepcopy(self.condition, memo))
            memo[id_self] = _copy 
        return _copy

    # nice printing of the stack frame for debugging
    def __str__(self):
        output_string = f"{self.type}"
        if self.condition:
            output_string += f", conditional on {self.condition}"
        output_string += ":\n"
        for key, item in self.values.items():
            output_string += indent(f"{str(key)}: {str(item)}\n", "   ")
        return output_string
    def __repr__(self):
        return self.__str__()

# --- Main Stack Frame Manipulation --- #

class Virtual_environment(object):
    # odd-looking __init__ is necessary so that deepcopy functions correctly
    def __init__(self, frame_stack):
        if frame_stack:
            self.frame_stack = frame_stack
        else:
            self.frame_stack = [Stack_frame(None, None, BASE_FRAME, None)]

    # opens a new stack frame
    def new_stack_frame(self, frame_type, condition):
        self.frame_stack.append(Stack_frame(None, None, frame_type, condition))
    
    # closes the top stack frame, returning its contents
    # this is used internally only
    def stack_frame_pop(self):
        if len(self.frame_stack) <= 1:
            raise Exception("No more stack frames can be be removed")
        else:
            return self.frame_stack.pop()

    # closes the top stack frame, deleting the variables within it
    def destructive_pop_stack_frame(self):
        frame = self.stack_frame_pop()
        return frame.type, frame.condition

    # closes the top stack frame, transferring all variables within it to the 
    #   new top stack frame
    def constructive_pop_stack_frame(self):
        temp_frame_copy = copy.deepcopy(self.stack_frame_pop())
        names = temp_frame_copy.get_variable_names()
        for name in names:
            value = temp_frame_copy.read_item_value(name).convert_to_token()
            self.make_variable(value, name)
        return temp_frame_copy.type, temp_frame_copy.condition

    # iterates through all of the frames in the frame stack from top to bottom looking 
    #   for the requested variable until a frame that shouldn't be iterated past is reached
    # used as an internal method for fetch_virtual_variable and set_virtual_variable
    def find_variable(self, input_name_keyword):
        frame_index = len(self.frame_stack) - 1
        end_iteration = False
        value_found = False
        while not end_iteration:
            current_stack_frame = self.frame_stack[frame_index]
            # if the variable is in the frame then take it
            if current_stack_frame.variable_in(input_name_keyword):
                end_iteration = True
                value_found = True
            else:
                #If the base frame is reached then there is nothing left to iterate through
                if token_matches(current_stack_frame.type, BASE_FRAME):
                    end_iteration = True
                    value_found = False
                else:
                    frame_index -= 1
        if not value_found:
            raise Exception(f"there is no variable with the name keyword \
                {input_name_keyword} available in the current scope")
        else:
            # all that is needed is the frame in which the variable is contained
            return frame_index

    # fetches the current token-formatted value of the variable name specified
    def fetch_virtual_variable(self, input_name_keyword):
        # outputting the variable value as a token if found
        frame_index = self.find_variable(input_name_keyword)
        containing_stack_frame = self.frame_stack[frame_index]
        output_value = containing_stack_frame.read_item_value(input_name_keyword).convert_to_token()
        return output_value

    # sets the value of the specified variable
    def set_variable(self, input_name_keyword, my_input):
        # ensures converted_virtual_var is a virtual var, whether the input is an 
        #   unconverted token or a virtual var
        if not type(my_input) == Token:
            raise Exception(f"{my_input} is an invalid set_variable input")
        # converting to virtual variable, the standard for storing data in 
        #   the virtual environment
        converted_virtual_var = convert_to_virtual_variable(my_input)
        
        # locating the variable's position in the frame stack
        frame_index = self.find_variable(input_name_keyword)

        # ensuring the variable is of the type of the variable
        original_value = self.frame_stack[frame_index].read_item_value(input_name_keyword)
        if type(original_value) == type(converted_virtual_var):
            self.frame_stack[frame_index].set_item_value(converted_virtual_var, input_name_keyword)
        else:
            raise Exception(f"Wrong type: {original_value} and {converted_virtual_var} \
                are not of the same type")
    
    # creates a new variable in the current stack frame
    def make_variable(self, my_input, input_name_keyword):
        # ensures converted_virtual_var is a virtual var, whether the input is 
        #   an unconverted token or a virtual var
        if type(my_input) != Token:
            raise Exception(f"{my_input} is an invalid make_variable input, it must \
                be a token")
        # converting to virtual variable, the standard for storing data in 
        #   the virtual environment
        converted_virtual_var = convert_to_virtual_variable(my_input)
        # inserting into the stack frame
        self.frame_stack[-1].make_item(converted_virtual_var, input_name_keyword)
    
    # deletes a variable with the stated name
    def delete_variable(self, input_name_keyword):
        frame_index = self.find_variable(input_name_keyword)
        self.frame_stack[frame_index].remove_item(input_name_keyword)

    # returns the number of stack frames
    def get_frame_stack_len(self):
        return len(self.frame_stack)

    # __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.frame_stack, memo))
            memo[id_self] = _copy 
        return _copy

    # nice printing of the virtual env for debugging
    def __str__(self):
        output_string = "Virtual environment:\n"
        for frame in self.frame_stack:
            output_string += indent(f"{str(frame)}\n","   ")
        return output_string
    def __repr__(self):
        return self.__str__()


# ------------------------------ INTERPRETER ------------------------------ #

# The purpose of process_AST is to recursively consolidate an AST into one instruction
#   using the values and operations contained within and calls for values from the 
#   virtual environment
# Summary_token is what this branch of the AST is condensed into
# It is a Token to be operated on by its parent node
def process_AST(my_AST, virtual_environment):
    if type(my_AST) == Leaf_node:
        # if the AST is a leaf node then it can be treated as a lone Token
        summary_token = Token(my_AST.type, my_AST.value)
    else:
        my_child_nodes = my_AST.child_nodes
        # my_child_values will hold the resultant values after each child node is processed
        my_processed_tokens = []
        # process each child node and record the vales they produce
        for child_node in my_child_nodes:
            if child_node.type in ROOT_NODE_TYPES:
                raise Exception(f"The root node {child_node} has been passed to a {my_AST.type}")
            new_value, virtual_environment = process_AST(child_node, virtual_environment)
            my_processed_tokens.append(new_value)
        # do_operation carries out whatever operation is inputted as first parameter
        summary_token, virtual_environment = do_operation(my_AST.type, my_processed_tokens, \
            virtual_environment)
    return summary_token, virtual_environment

# used to convert variable references to their values as needed
def make_not_variable_name(input_token, virtual_environment):
    if input_token.type == NAME_KEYWORD:
        output = virtual_environment.fetch_virtual_variable(input_token.value)
    else:
        output = input_token
    output = copy.deepcopy(output)
    return output

# Takes type tokens either standard value ones or virtual variable ones. 
# Outputs the standard value or standard value equivalent
def make_basic_type(token_type):
    if token_type in VALUE_TYPES:
        return token_type
    elif token_type in VIRTUAL_VARIABLE_TYPES:
        return VIRTUAL_VARIABLE_TYPES_TO_BASIC_TYPES[token_type]
    else:
        raise Exception(f"cannot convert {token_type} to basic type")

# this subroutine takes an operation and its inputs and carries it out, returning any 
#   necessary outputs for any operation it is an operand of
def do_operation(operation, input_token_list_original, virtual_environment):
    output = None
    input_token_list = copy.deepcopy(input_token_list_original)
    # if statement to funnell the data to the correct subroutine
    if operation == ASSIGNMENT:
        virtual_environment = assignment_operation(input_token_list, virtual_environment)
    elif operation == DECLARATION_NORMAL_WITH_VALUE:
        virtual_environment = declaration_operation(input_token_list, virtual_environment)
    elif operation == DECLARATION_NORMAL_WITHOUT_VALUE:
        virtual_environment = declaration_without_value_operation(input_token_list, virtual_environment)
    elif operation == FOR_STATEMENT:
        virtual_environment, output = for_statement_operation(input_token_list, virtual_environment)
    elif operation == ARRAY_APPEND:
        virtual_environment = array_append_operation(input_token_list, virtual_environment)
    elif operation == PRIORITY_QUEUE_ADD_ITEM:
        virtual_environment = priority_queue_add_item_operation(input_token_list, virtual_environment)
    elif operation == STACK_QUEUE_ADD_ITEM:
        virtual_environment = stack_queue_add_item_operation(input_token_list, virtual_environment)
    elif operation == STACK_QUEUE_ITEM_POP:
        virtual_environment = stack_queue_pop_item_operation(input_token_list, virtual_environment)
    elif operation == DICTIONARY_INSERT:
        output = dictionary_insert_operation(input_token_list, virtual_environment)
    elif operation == DICTIONARY_REMOVE:
        output = dictionary_remove_operation(input_token_list, virtual_environment)
    else:
        # all operations after this do not involve setting a variable value and as such all
        # their variable references need to be converted into their actual values. For those 
        # before this they need the name so they can define the variable
        for index in range(len(input_token_list)):
            input_token_list[index] = make_not_variable_name(input_token_list[index], virtual_environment)

        # if statement to continue funnelling data to the correct operation subroutines
        if operation == BRACKETS:
            output = brackets_operation(input_token_list)
        elif operation == IF_STATEMENT:
            output = if_statement_operation(input_token_list)
        elif operation == WHILE_STATEMENT:
            output = while_statement_operation(input_token_list)
        elif operation in [ARRAY, TUPLE, DICTIONARY]:
            output = array_tuple_dict_operation(operation, input_token_list)
        elif operation == CONCATENATION_OR_ADDITION:
            output = concatenation_or_addition_operation(input_token_list)
        elif operation == SUBTRACTION:
            output = subtraction_operation(input_token_list)
        elif operation == MULTIPLICATION:
            output = multiplication_operation(input_token_list)
        elif operation == DIVISION:
            output = division_operation(input_token_list)
        elif operation == INTEGER_DIVISION:
            output = integer_division_operation(input_token_list)
        elif operation == MODULO_DIVIDE:
            output = modulo_division_operation(input_token_list)
        elif operation == BOOLEAN_COMPARISON:
            output = boolean_comparison_operation(input_token_list)
        elif operation == BINARY_BOOLEAN_LOGICAL_STATEMENT:
            output = binary_boolean_logical_statement_operation(input_token_list)
        elif operation == SINGLE_BOOLEAN_LOGICAL_STATEMENT:
            output = single_boolean_logical_statement_operation(input_token_list)
        elif operation == STRING_LIST_READ_BY_INDEX:
            output = string_list_read_by_index(input_token_list)
        elif operation == LENGTH_CHECK:
            output = length_check_operation(input_token_list)
        elif operation == OUTPUT_CALL:
            output = output_operation(input_token_list)
        elif operation == STACK_QUEUE_ITEM_READ:
            output = stack_queue_read_item_operation(input_token_list)
        elif operation == DICTIONARY_LOOKUP:
            output = dictionary_lookup_operation(input_token_list)
        elif operation == DICTIONARY_KEY_LIST:
            output = dictionary_key_list_operation(input_token_list, virtual_environment)
        elif operation == DICTIONARY_PAIR:
            output = dictionary_pair_operation(input_token_list)
        else:
            raise Exception(f"Invalid operation: {operation}")
    if output == None:
        output = Token(NON_ACTIONABLE_ROOT_NODE, None)
    return output, virtual_environment

# changes an already existing virtual environment variable's value
def assignment_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"only two inputs can be used in the assignment \
            operation: {input_token_list}")
    else:
        value_to_assign = make_not_variable_name(input_token_list[1], virtual_environment)
        name_to_assign_to = input_token_list[0].value
        virtual_environment.set_variable(name_to_assign_to, value_to_assign)
    return virtual_environment        

# creates a new variable, of a specified type
def declaration_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 3:
        raise Exception(f"only three inputs can be used in the normal declaration \
            operation: {input_token_list}")
    else:
        # data manipulation to get into correct formats
        declaration_type = input_token_list[0].type
        name_to_assign_to = input_token_list[1].value
        type_to_assign = DECLARATION_TYPES_TO_BASIC_TYPES_DICT[declaration_type]
        value_token = make_not_variable_name(input_token_list[2], virtual_environment)
        value_type = value_token.type
        value_type_basic = make_basic_type(value_type)
        value = value_token.value
        # checking that the value is valid for the datatype
        if type_to_assign == value_type_basic:
            token_to_convert = Token(type_to_assign, value)
            token_to_assign = convert_to_virtual_variable(token_to_convert).convert_to_token()
        # special case for assigning values to floating points as numbers which don't 
        #   contain decimal points can still be floats
        elif(value_type_basic == DECIMAL_NUMBER or value_type_basic == INTEGER) and type_to_assign == FLOAT:
            if value_type == VIRTUAL_INTEGER:
                token_to_assign = value.convert_to_virtual_float().convert_to_token()
            else:
                token_to_convert = Token(type_to_assign, value)
                token_to_assign = convert_to_virtual_variable(token_to_convert).convert_to_token()
        else:
            raise Exception(f"{value_token} cannot be assigned to a(n) {type_to_assign} variable")
        # creation of variable
        virtual_environment.make_variable(token_to_assign, name_to_assign_to)
    return virtual_environment

def declaration_without_value_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"only two inputs can be used in the normal declaration \
            without value operation: {input_token_list}")
    else:
        # data manipulation to get into correct formats
        declaration_type = input_token_list[0].type
        type_to_assign = DECLARATION_TYPES_TO_BASIC_TYPES_DICT[declaration_type]
        token_to_convert = Token(type_to_assign, None)
        token_to_assign = convert_to_virtual_variable(token_to_convert).convert_to_token()
        name_to_assign_to = input_token_list[1].value
        # Creation of variable
        virtual_environment.make_variable(token_to_assign, name_to_assign_to)
    return virtual_environment

def for_statement_operation(input_token_list, virtual_environment):
    try:
        if len(input_token_list) != 2:
            raise Exception(f"only two inputs can be used in the normal \
                declaration without value operation: {input_token_list}")
        else:
            # data manipulation and confirmation of correct input types
            name = input_token_list[0].value
            values_list = convert_to_virtual_variable(make_not_variable_name(input_token_list[1], virtual_environment))
            if type(values_list) != Array_virtual:
                raise Exception(f"Input {values_list} is not an array")
            # sending information to high level flow management using root node outputs
            if values_list.get_length() == 0:
                token_to_send = Token(SKIP_FOR, None)
            else:
                token_to_send = Token(OPEN_FOR, [name, values_list])
    except Exception as e:
        if DEBUG_OUTPUTS : print(f"Error: {e}")
    return virtual_environment, token_to_send

# bracketing removal
def brackets_operation(input_token_list):
    if len(input_token_list) != 1:
        raise Exception(f"brackets are surrounding multiple children, this should \
            not be possible after processing: {input_token_list}")
    else:
        output = input_token_list[0]
    return output

# formations of arrays, tuples and dictionaries from their constituent parts
def array_tuple_dict_operation(var_type, input_token_list):
    token_to_convert = Token(var_type, input_token_list)
    output = convert_to_virtual_variable(token_to_convert).convert_to_token()
    return output

def if_statement_operation(input_token_list):
    try:
        if len(input_token_list) != 1:
            raise Exception(f"Only one item can be inputted to an if statement \
                operation: {input_token_list}")
        else:
            # data formatting then checking the boolean evaluation and forwarding 
            #   instructions to the high level flow management using root node outputs
            input_virt_var = convert_to_virtual_variable(input_token_list[0])
            value = input_virt_var.get_value()
            if value == 1:
                output = Token(OPEN_IF, None)
            elif value == 0:
                output = Token(SKIP_IF, None)
            else:
                raise Exception("Invalid boolean value")
    except Exception as e:
        if DEBUG_OUTPUTS : print(f"Error: {e}")
    return output

def while_statement_operation(input_token_list):
    try:
        if len(input_token_list) != 1:
            raise Exception(f"Only one item can be inputted to a while \
                statement operation: {input_token_list}")
        else:
            # data formatting then checking the boolean evaluation and forwarding
            #   instructions to the high level flow management using root node outputs
            input_virt_var = convert_to_virtual_variable(input_token_list[0])
            value = input_virt_var.get_value()
            if value == 1:
                output = Token(OPEN_WHILE, None)
            elif value == 0:
                output = Token(SKIP_WHILE, None)
            else:
                raise Exception("Invalid boolean value")
    except Exception as e:
        if DEBUG_OUTPUTS : print(f"Error: {e}")
    return output

def output_operation(input_token_list):
    output = Token(OUTPUT_REQUEST, input_token_list)
    return output

# addition/concatentation of various types. This operation can be carried out on 
#   pairs of strings, arrays and various combinations of integer and floating point numbers
def concatenation_or_addition_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to an addition/concatenation \
            operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        # strings
        if type(value_1) == String_virtual and type(value_2) == String_virtual:
            value_1.concatenate(value_2)
            output = value_1.convert_to_token()
        # arrays
        elif type(value_1) == Array_virtual and type(value_2) == Array_virtual:
            value_1.join(value_2)
            output = value_1.convert_to_token()
        # detecting the different numerical combinations and carrying out the appropriate operations
        elif type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1.integer_add(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Float_virtual and (type(value_2) == Integer_virtual or type(value_2) == Float_virtual):
            value_1.add(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Integer_virtual and type(value_2) == Float_virtual:
            value_1 = value_1.convert_to_virtual_float()
            value_1.add(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for concatenation/addition: {value_1, value_2}")
    
    return output

# subtracting the second number from the first
def subtraction_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to an subtraction operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        # detecting the different numerical combinations and carrying out the appropriate operations
        if type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1.integer_subtract(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Float_virtual and (type(value_2) == Integer_virtual or type(value_2) == Float_virtual):
            value_1.subtract(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Integer_virtual and type(value_2) == Float_virtual:
            value_1 = value_1.convert_to_virtual_float()
            value_1.subtract(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for subtraction: {value_1, value_2}")

        return output

# multiplying together two numbers
def multiplication_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to a multiplication operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        # detecting the different numerical combinations and carrying out the appropriate operations
        if type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1.integer_multiply(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Float_virtual and (type(value_2) == Integer_virtual or type(value_2) == Float_virtual):
            value_1.multiply(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Integer_virtual and type(value_2) == Float_virtual:
            value_1 = value_1.convert_to_virtual_float()
            value_1.multiply(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for multiplication: {value_1, value_2}")

        return output

# dividing a number by another number
def division_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to a division operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        # detecting the different numerical combinations and carrying out the appropriate operations
        if type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1 = value_1.convert_to_virtual_float()
            value_1.divide(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Float_virtual and (type(value_2) == Integer_virtual or type(value_2) == Float_virtual):
            value_1.divide(value_2)
            output = value_1.convert_to_token()
        elif type(value_1) == Integer_virtual and type(value_2) == Float_virtual:
            value_1 = value_1.convert_to_virtual_float()
            value_1.divide(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for division: {value_1, value_2}")

        return output

# carry out integer division on two integers
def integer_division_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to a integer division \
            operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        if type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1.integer_division(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for integer division: {value_1, value_2}")

        return output

# carry out modulo division on two integers
def modulo_division_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to a modulo division \
            operation: {input_token_list}")
    else:
        value_1 = convert_to_virtual_variable(input_token_list[0])
        value_2 = convert_to_virtual_variable(input_token_list[1])
        # detecting the different numerical combinations and carrying out the 
        #   appropriate operations
        if type(value_1) == Integer_virtual and type(value_2) == Integer_virtual:
            value_1.integer_modulo_division(value_2)
            output = value_1.convert_to_token()
        else:
            raise Exception(f"Invalid operands for modulo division: {value_1, value_2}")

        return output

# evaluation of a boolean comparison
def boolean_comparison_operation(input_token_list):
    if len(input_token_list) != 3:
        raise Exception(f"Three operands must be passed to a boolean \
            comparison operaiton: {input_token_list}")
    else:
        # input values extraction
        item_1 = convert_to_virtual_variable(input_token_list[0])
        item_2 = convert_to_virtual_variable(input_token_list[2])

        # comparator extraction
        if not isinstance(input_token_list[1], Token):
            raise Exception(f"comparator {input_token_list[1]} must \
                be a token")
        comparator = input_token_list[1].type

        if type(item_1) != type(item_2):
            raise Exception(f"Inputs to a boolean comparison operation \
                must be of the same type ({item_1} and {item_2} were input)")
        else:
            value_1 = item_1.get_value()
            value_2 = item_2.get_value()

            # carrying out the comparisons depending on the comparator parameter
            result = 0
            if comparator == IS_EQUAL_TO:
                if value_1 == value_2:
                    result = 1
            elif comparator == IS_NOT_EQUAL_TO:
                if value_1 != value_2:
                    result = 1
            else:
                if not(type(item_1) == Integer_virtual or type(item_1) == Float_virtual):
                    raise Exception("Only integers and floats can have \
                        non-equals-based comparators")
                else:
                    if comparator == IS_LESS_THAN:
                        if value_1 < value_2:
                            result = 1
                    elif comparator == IS_LESS_THAN_OR_EQUAL_TO:
                        if value_1 <= value_2:
                            result = 1
                    elif comparator == IS_GREATER_THAN:
                        if value_1 > value_2:
                            result = 1
                    elif comparator == IS_GREATER_THAN_OR_EQUAL_TO:
                        if value_1 >= value_2:
                            result = 1
        boolean_output = Boolean_virtual(result)
        return boolean_output.convert_to_token()    

# evaluation of a binary boolean logical statement (and, or)
def binary_boolean_logical_statement_operation(input_token_list):
    if len(input_token_list) != 3:
        raise Exception(f"Three operands must be passed to a boolean logical \
            statement operaiton: {input_token_list}")
    else:
        # input values extraction
        item_1 = convert_to_virtual_variable(input_token_list[0])
        item_2 = convert_to_virtual_variable(input_token_list[2])
        if type(item_1) != Boolean_virtual or type(item_2) != Boolean_virtual:
            raise Exception(f"Inputs to a boolean logical statement operation \
                must be boolean, ({item_1} and {item_2} were input)")

        # comparator extraction
        if not isinstance(input_token_list[1], Token):
            raise Exception(f"logical keyword {input_token_list[1]} must be a token")
        logical_keyword = input_token_list[1].type

        value_1 = item_1.get_value()
        value_2 = item_2.get_value()
        result = 0
        # carries out the operation
        if logical_keyword == AND:
            if value_1 == 1 and value_2 == 1:
                result = 1
        elif logical_keyword == OR:
            if value_1 == 1 or value_2 == 1:
                result = 1
        boolean_output = Boolean_virtual(result)
        return boolean_output.convert_to_token() 
            
# evaluation of a single-input boolean logical statement (not)
def single_boolean_logical_statement_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Two operands must be passed to a boolean \
            logical statement operation: {input_token_list}")
    else:
        # input value extraction
        item = convert_to_virtual_variable(input_token_list[1])
        if type(item) != Boolean_virtual:
            raise Exception(f"Inputs to a boolean logical statement \
                operation must be boolean, ({item_1} was input)")

        if not isinstance(input_token_list[0], Token):
            raise Exception(f"logical keyword {input_token_list[0]} \
                must be a token")
        logical_keyword = input_token_list[0].type

        value = item.get_value()
        result = 0
        # carries out the operation
        if logical_keyword == NOT:
            if value == 0:
                result = 1
        
        boolean_output = Boolean_virtual(result)
        return boolean_output.convert_to_token() 

# reads a string or list by index (either single index integer or index range list)
def string_list_read_by_index(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to string/list \
            read by index: {input_token_list}")
    else:
        # data extraction and manipulation
        to_be_read = convert_to_virtual_variable(input_token_list[0])
        position_parameter = convert_to_virtual_variable(input_token_list[1]).get_value()
        if not(isinstance(to_be_read, List_based_virtual) or isinstance(to_be_read, String_virtual)):
            raise Exception("Only lists and strings can be read by index")
        else:
            # funnels instructions to the virtual variable
            output = to_be_read.read_item(position_parameter)
            if isinstance(output, Virtual_variable):
                output_virt_var = output
            else:
                output_virt_var = type(to_be_read)(output)
    return output_virt_var.convert_to_token()

# outputs the length of the inputted data structure
def length_check_operation(input_token_list):
    if len(input_token_list) != 1:
        raise Exception(f"Only one item can have its \
            length checked: {input_token_list}")
    else:
        # formatting values and calling get_length
        item = input_token_list[0].value
        length = item.get_length()
        virt_var = Integer_virtual(length)
    return virt_var.convert_to_token()

# appends a value to the end of an array
def array_append_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted \
            to array append: {input_token_list}")
    else:
        # formatting and the calling of the array's append method
        array = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        value_to_add = make_not_variable_name(input_token_list[1], virtual_environment)
        array_name = input_token_list[0]
        array.append_item(value_to_add)
        new_array_token = array.convert_to_token()
        # reassigning the edited version of the array
        assignment_operation([array_name, new_array_token], virtual_environment)
    return virtual_environment

# inserts an item into a priority queue
def priority_queue_add_item_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 3:
        raise Exception(f"Only three items can be inputted \
            to priority queue add item: {input_token_list}")
    else:
        # formatting values
        prioqueue = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        prioqueue_name = input_token_list[0]
        value_to_add = make_not_variable_name(input_token_list[1], virtual_environment)
        priority_token = convert_to_virtual_variable(make_not_variable_name(input_token_list[2], virtual_environment))
        if not type(priority_token) == Integer_virtual:
            raise Exception(f"{priority_token} is not valid")
        else:
            # carrying out the actual operation
            priority = priority_token.get_value()
            prioqueue.add_item(value_to_add, priority)
            # reassigning the datastructure
            new_prioqueue_token = prioqueue.convert_to_token()
            assignment_operation([prioqueue_name, new_prioqueue_token], virtual_environment)
    return virtual_environment

# inserts an item into a normal stack or queue
def stack_queue_add_item_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to \
            stack/queue add item: {input_token_list}")
    else:
        # formatting values
        datastruct = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        value_to_add = make_not_variable_name(input_token_list[1], virtual_environment)
        datastruct_name = input_token_list[0]
        # adding the item
        datastruct.add_item(value_to_add)
        # reassigning the datastructure
        new_datastruct_token = datastruct.convert_to_token()
        assignment_operation([datastruct_name, new_datastruct_token], virtual_environment)
    return virtual_environment

# outputs the value of the first item in a stack/queue/priorityqueue
def stack_queue_read_item_operation(input_token_list):
    if len(input_token_list) != 1:
        raise Exception(f"Only one item can be inputted to \
            stack/queue read item: {input_token_list}")
    else:
        datastruct = convert_to_virtual_variable(input_token_list[0])
        output = datastruct.read_item()
    return output

# removes the first item from stack/queue/priorityqueue
def stack_queue_pop_item_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 1:
        raise Exception(f"Only one item can be inputted to \
            stack/queue pop item: {input_token_list}")
    else:
        # setting up/extracting values
        datastruct = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        datastruct_name = input_token_list[0]
        # removing the item
        datastruct.pop_item()
        # reassigning the datastructure
        new_datastruct_token = datastruct.convert_to_token()
        assignment_operation([datastruct_name, new_datastruct_token], virtual_environment)
    return virtual_environment

# inserts an item into a dictionary
def dictionary_insert_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to \
            dictionary insert pair: {input_token_list}")
    else:
        # setting up/extracting values
        dictionary = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        pair_to_add = convert_to_virtual_variable(make_not_variable_name(input_token_list[1], virtual_environment))
        dictionary_name = input_token_list[0]
        # inserting the item
        dictionary.pair_insertion(pair_to_add)
        # reassigning the datastructure
        new_dictionary_token = dictionary.convert_to_token()
        assignment_operation([dictionary_name, new_dictionary_token], virtual_environment)
    return virtual_environment

# looks up the value associated with a key in a dictionary
def dictionary_lookup_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to \
            dictionary lookup item: {input_token_list}")
    else:
        # setting up/extracting values
        dictionary = convert_to_virtual_variable(input_token_list[0])
        key = convert_to_virtual_variable(input_token_list[1])
        # getting the value
        value = dictionary.find_value(key).convert_to_token()
    return value

# removing a key-value pair from a dictionary using the key
def dictionary_remove_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to \
            dictionary remove pair: {input_token_list}")
    else:
        # setting up/extracting values
        dictionary = convert_to_virtual_variable(make_not_variable_name(input_token_list[0], virtual_environment))
        key = convert_to_virtual_variable(make_not_variable_name(input_token_list[1], virtual_environment))
        dictionary_name = input_token_list[0]
        # removing the pair
        dictionary.pair_removal(key)
        # reassigning the dictionary
        new_dictionary_token = dictionary.convert_to_token()
        assignment_operation([dictionary_name, new_dictionary_token], virtual_environment)
    return virtual_environment

# returns an array of the valid keys for a dictionary
def dictionary_key_list_operation(input_token_list, virtual_environment):
    if len(input_token_list) != 1:
        raise Exception(f"Only one item can be inputted to \
            dictionary key list: {input_token_list}")
    else:
        dictionary = convert_to_virtual_variable(input_token_list[0])
        keys = dictionary.key_list().convert_to_token()
    return keys

# takes a key and a value and returns a Dictionary_pair of them
def dictionary_pair_operation(input_token_list):
    if len(input_token_list) != 2:
        raise Exception(f"Only two items can be inputted to \
            dictionary pair: {input_token_list}")
    else:
        key = convert_to_virtual_variable(input_token_list[0])
        value = convert_to_virtual_variable(input_token_list[1])
        key_pair = Dictionary_pair(key, value).convert_to_token()
    return key_pair


# ------------------------------ TOP-LEVEL FLOW MANAGEMENT ------------------------------ #

# instantiated with an array of abstract syntax trees and can run them.
class Program_runner(object):
    def __init__(self, ast_lines):
        self.ast_lines = ast_lines
    
    def run(self):
        # setting up values
        self.my_virtual_environment = Virtual_environment(None)
        self.line_index = -1
        
        # runs each line in sequence
        while self.line_index < len(self.ast_lines)-1:
            self.increment()
            result, self.my_virtual_environment = process_AST(self.ast, self.my_virtual_environment)
            # if an actionable root node is passed up to run() this signals an action that needs
            #   to be taken, these are handled by handle_root_nodes()
            if result and type(result) == Token and (result.type in ACTIONABLE_ROOT_NODE_TYPES):
                self.handle_root_nodes(result)
        
        # debug info
        if DEBUG_OUTPUTS : print(self.my_virtual_environment)

        # senses if there has been an error and not all frames have been accounted for at
        #   the end of program execution
        if self.my_virtual_environment.get_frame_stack_len() != 1:
            raise Exception(f"Program ended without working back to base \
                frame, length: {self.my_virtual_environment.get_frame_stack_len()}")

    def handle_root_nodes(self, result):
        if DEBUG_OUTPUTS : print(self.my_virtual_environment)

        # for outputting values
        if result.type == OUTPUT_REQUEST:
            handle_outputs(result.value)
        
        elif result.type == OPEN_IF:
            # begins a new if statement, which will work through the lines in the if section 
            #   but will skip those in the else section if there is one
            # the boolean condition indicates whether else lines should be run
            self.my_virtual_environment.new_stack_frame(IF_FRAME, False)
        elif result.type == SKIP_IF:
            # begins a new if statement, which will skip the lines in the if statement but 
            #   run those in the else section if there is one
            self.my_virtual_environment.new_stack_frame(IF_FRAME, True)
            self.skip_until([END_IF, ELSE])
        elif result.type == ELSE:
            # checks the boolean condition (run_else_bool) on an if frame and runs the code after 
            #   the else statement if it = True
            frame_type, run_else_bool = self.my_virtual_environment.constructive_pop_stack_frame()
            if frame_type != IF_FRAME:
                raise Exception("ELSE can only be placed to end an if statement")
            else:
                if run_else_bool:
                    self.my_virtual_environment.new_stack_frame(IF_FRAME, None)
                else:
                    self.my_virtual_environment.new_stack_frame(IF_FRAME, None)
                    self.skip_until([END_IF])
        elif result.type == END_IF:
            # closes an if statement
            frame_type, run_else_bool = self.my_virtual_environment.constructive_pop_stack_frame()
            if frame_type != IF_FRAME:
                raise Exception("ENDIF can only be placed to end an if statement")
            else:
                pass
        
        elif result.type == OPEN_WHILE:
            # begins a new while statement, the 'condition' in a while statement is the line 
            #   where it began so it can be returned to when the code block has been run
            self.my_virtual_environment.new_stack_frame(WHILE_FRAME, self.line_index)
        elif result.type == SKIP_WHILE:
            # skips until the end of a while statement, used when the boolean condition 
            #   returns false
            self.my_virtual_environment.new_stack_frame(WHILE_FRAME, None)
            self.skip_until([END_WHILE])
        elif result.type == END_WHILE:
            # closes a while statement, returns to the beginning for another boolean condition 
            #   check ifthe condition part of the stack frame contains an index (the absence 
            #   of an index is an indication that the statement is complete/skip while has been used)
            frame_type, return_index = self.my_virtual_environment.constructive_pop_stack_frame()
            if frame_type != WHILE_FRAME:
                raise Exception("ENDWHILE can only be placed to end an while statement")
            else:
                if return_index:
                    self.set_index(return_index-1)
                else:
                    pass
        
        elif result.type == OPEN_FOR:
            # begins a new for statement, the 'condition' in a while stack frame is made up of 
            #   the name of the value that is being assigned, the list of values remaining to 
            #   be iterated over and the index of the beginning of the statement
        
            # extracting values
            input_info = result.value
            name = input_info[0]
            values_list = input_info[1]
            if values_list.get_length() == 0:
                raise Exception(f"values_list is empty")
            else:
                # sets up the stack frame and variable
                self.my_virtual_environment.new_stack_frame(FOR_FRAME, \
                    [name, values_list.read_item([Integer_virtual(1), \
                        Integer_virtual(values_list.get_length()-1)]), self.line_index])
                self.my_virtual_environment.make_variable(\
                    values_list.read_item(0).convert_to_token(), name)
        elif result.type == SKIP_FOR:
            # used if the initial call of for contains an empty list for iterating over, 
            #   just skips until the end of the statement
            if result.value:
                raise Exception(f"A value should not be passed to skip for, \
                    the value is {result.value}")
            else:
                self.my_virtual_environment.new_stack_frame(FOR_FRAME, None)
                self.skip_until(END_FOR)
        elif result.type == END_FOR:
            # closes a for statement and removes its temporary variable, if the list 
            #   to be iterated over is not empty it returns to the beginning of the
            #   statement and creates a new temporary variable
            frame_type, conditions = self.my_virtual_environment.constructive_pop_stack_frame()
            if frame_type != FOR_FRAME:
                raise Exception("ENDFOR can only be placed to end a for statement")
            else:
                if conditions:
                    # extracting information and removing most recent iteration of the variable
                    name = conditions[0]
                    values_list = conditions[1]
                    return_index = conditions[2]
                    self.my_virtual_environment.delete_variable(name)
                    if len(values_list) != 0:
                        # setting up next iteration
                        self.my_virtual_environment.new_stack_frame(FOR_FRAME, \
                            [name, values_list[1:], return_index])
                        self.my_virtual_environment.make_variable(\
                            values_list[0].convert_to_token(), name)
                        self.set_index(return_index)
                    else:
                        pass
                else:
                    pass

    # moves to the specified line
    def set_index(self, index_value):
        self.line_index = index_value
        self.ast = self.ast_lines[self.line_index]

    # moves to the next line
    def increment(self):
        self.line_index += 1
        if self.line_index == len(self.ast_lines):
            raise Exception("End has been reached")
        self.ast = self.ast_lines[self.line_index]
    
    # moves to the line before
    def decrement(self):
        if self.line_index == 0:
            raise Exception("Beginning has been reached")
        self.line_index -= 1
        self.ast = self.ast_lines[self.line_index]

    # moves through the 
    def skip_until(self, ending_token_list):
        found = False

        # used so that process_AST will run
        temp_virtual_environment = copy.deepcopy(self.my_virtual_environment)

        # the resolver counts are used to ensure that if, while and for statements 
        #   contained within other statements are complete. This is ensured by
        #   this is done by keeping a running count for each which increases on an
        #   open line and decreases on an end line
        # IF, WHILE, FOR
        resolver_count = [0,0,0]

        while not found:
            self.increment()
            try:
                # extracts the root node
                ast_root_type = self.ast.type
                if ast_root_type in OPERATION_TYPE_TO_ROOT_NODE.keys():
                    root_type = OPERATION_TYPE_TO_ROOT_NODE.get(ast_root_type)
                else:
                    root_type = ast_root_type
                
                # checks if the end has been reached
                if all(counter == 0 for counter in resolver_count):
                    if root_type in ending_token_list:
                        found = True
                
                # manages resolver counts
                if root_type == OPEN_IF or root_type == SKIP_IF:
                    resolver_count[0] += 1
                elif root_type == END_IF:
                    resolver_count[0] -= 1
                elif root_type == OPEN_WHILE or root_type == SKIP_WHILE:
                    resolver_count[1] += 1
                elif root_type == END_WHILE:
                    resolver_count[1] -= 1
                elif root_type == OPEN_FOR or root_type == SKIP_FOR:
                    resolver_count[2] += 1
                elif root_type == END_FOR:
                    resolver_count[2] -= 1
            except Exception as e:
                if DEBUG_OUTPUTS : print(f"Error: {e}")
        # moves back to the correct position to run the line that has been skipped to
        self.decrement()

# outputs each of the values entered on a single line
def handle_outputs(values):
    full_output = "> "
    for value in values:
        value = convert_to_virtual_variable(value)
        # calls the output_representation method which all virtual variables have
        full_output += value.output_representation()
    print(full_output)


# ------------------------------ MAIN CONTROLLER ------------------------------ #

# The component that runs each of the main parts of the program in sequence
def main_controller():
    code_lines = get_code()
    print("\nRunning program...\n")
    if DEBUG_OUTPUTS or LOW_DEBUG_OUTPUTS : print(code_lines)
    processed_code_lines = process_code(code_lines)
    if DEBUG_OUTPUTS or LOW_DEBUG_OUTPUTS : print(processed_code_lines)
    program_run = Program_runner(processed_code_lines)
    program_run.run()
    print("\nProgram complete! Exiting...\n")
    exit()

# used to grab arguments when the program is called in the command line
import sys

# handles input from the Command Line either as a parameter or as an input 
#   when the program is run
# also validates the file name is valid using regex
valid_file_name_pattern = "^.+\.bp$"
def get_code():
    # extract file name or request from user
    arguments = sys.argv
    if len(arguments) == 2:
        file_name = arguments[1]
    elif len(arguments) == 1:
        if RUN_PROGRAM_WITHOUT_INPUT: 
            file_name = "program_code.bp"
        else:
            file_name = input("\nName the file that is to be run\n>>> ")
    else:
        raise Exception("Invalid number of arguments in the CLI")
    # file name validation
    if not re.match(valid_file_name_pattern, file_name):
        raise Exception("Invalid file name, must have the extension .bp")
    else:
        file = open(file_name, "r")
        code_lines = file.readlines()
        file.close()
    return code_lines

# takes an array of code lines and returns an array of the equivalent 
#   Abstract Syntax Trees
def process_code(code_lines):
    processed_lines = []
    for code_line in code_lines:
        AST = form_AST(process_text(code_line))
        processed_lines.append(AST)
    return processed_lines

# Flags used for developing and debugging
DEBUG_OUTPUTS = False
LOW_DEBUG_OUTPUTS = False
RUN_PROGRAM_WITHOUT_INPUT = False

if __name__ == "__main__":
    main_controller()
