from tokenTypesDefinitionLib import *
import re

# --- Variable Conversion --- #

# takes a token and converts it to a standalone virtual variable. The token can be a basic type or a virtual variable type
def convert_to_virtual_variable(token_to_convert):
    if not type(token_to_convert) == Token:
        raise Exception(f"{token_to_convert} is not a token")
    elif isinstance(token_to_convert.value, Virtual_variable):
        converted_variable = token_to_convert.value
    else:
        token_type = token_to_convert.type
        token_value = token_to_convert.value
        converted_variable = None
        if token_type == INTEGER:
            converted_variable = Integer_virtual(token_value)
        elif token_type == FLOAT or token_type == DECIMAL_NUMBER:
            converted_variable = Float_virtual(token_value)
        elif token_type == STRING:
            converted_variable = String_virtual(token_value)
        elif token_type == CHARACTER:
            converted_variable = Character_virtual(token_value)
        elif token_type == BOOLEAN:
            converted_variable = Boolean_virtual(token_value)
        elif token_type == TUPLE:
            converted_variable = Tuple_virtual(token_value)
        elif token_type == ARRAY:
            converted_variable = Array_virtual(token_value)
        elif token_type == STACK:
            converted_variable = Stack_virtual(None)
        elif token_type == QUEUE:
            converted_variable = Queue_virtual(None)
        elif token_type == PRIORITY_QUEUE:
            converted_variable = Priority_queue_virtual(None)
        elif token_type == DICTIONARY:
            converted_variable = Dictionary_virtual(None, None, token_value)
        if not converted_variable:
            raise Exception(f"{token_type} type tokens cannot be converted to virtual variables")
    return converted_variable

# --- Variable Implementation --- #

import copy
# __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
# by: https://stackoverflow.com/users/541136/russia-must-remove-putin

class Virtual_variable:
    # every virtual variable that is created will immediately run the set value procedure, which is specific to the class used
    def __init__(self, value):
        self.set_value(value)

    def check_valid(self, value):
        return True

    # all virtual variables' set value procedures will run the check valid procedure, which is also specific to the class used
    def set_value(self, value):
        if self.check_valid(value):
            self.value = value
    
    def get_value(self):
        return self.value

    def get_length(self):
        return len(self.value)

    # convert to token is used when a variable is taken out of the virtual environment by the interpreter
    # it provides a token that can be placed into an AST as a leaf node, these will take the for of
    # the relevant token type and the Virtual variable.
    def convert_to_token(self):
        raise Exception("This is an abstract virtual variable class and cannot be converted to token")

    def output_representation(self):
        return str(self.value)

    # __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.value, memo))
            memo[id_self] = _copy 
        return _copy

    # all virtual variables will have a __str__ function which specifies their variable type and value, their __repr__ function will
    # always parrot the __str__ function
    def __str__(self):
        return f"Unknown_virtual({self})"
    def __repr__(self):
        return self.__str__()

class Integer_virtual(Virtual_variable):
    # value is the python string from the token used to create this
    # check that the string is a valid integer
    def check_valid(self, value):
        if not (type(value) == int or (type(value) == str and (value.isdigit() or (value[0] == "-" and value[1:].isdigit())))):
            raise Exception(f"{value} is not a valid integer value")
        else:
            return True

    # set value to the integer value
    def set_value(self, value):
        if self.check_valid(value):
            self.value = int(value)

    # arithmetic operations which only take intergers and output integers
    def integer_add(self, other_virt_integer):
        total = self.get_value() + other_virt_integer.get_value()
        self.set_value(total)
    
    def integer_subtract(self, other_virt_integer):
        total = self.get_value() - other_virt_integer.get_value()
        self.set_value(total)
    
    def integer_multiply(self, other_virt_integer):
        total = self.get_value() * other_virt_integer.get_value()
        self.set_value(total)
    
    def integer_division(self, other_virt_integer):
        total = self.get_value() // other_virt_integer.get_value()
        self.set_value(total)
    
    def integer_modulo_division(self, other_virt_integer):
        total = self.get_value() % other_virt_integer.get_value()
        self.set_value(total)

    def convert_to_virtual_float(self):
        value = self.get_value()
        return Float_virtual(value)
    
    def get_length(self):
        raise Exception("This is an integer virtual variable class and its length cannot be requested")

    def convert_to_token(self):
        return Token(VIRTUAL_INTEGER, copy.deepcopy(self))

    def __str__(self):
        return f"Integer_virtual({self.value})"

ANYFLOATREGEX = "^-?[0-9]+(?:\.[0-9]+)?$"
class Float_virtual(Virtual_variable):
    # value is a python string from the token used to create this
    # check that the string is a valid representation of a float
    def check_valid(self, value):
        if not (type(value) == float or type(value) == int or (type(value) == str and re.match(ANYFLOATREGEX, value))):
            raise Exception(f"{value} is not a valid float value")
        else:
            return True
    
    # set value to the float value
    def set_value(self, value):
        if self.check_valid(value):
            self.value = float(value)

    # various arithmetic operations
    def add(self, other_virt_number):
        total = self.value + other_virt_number.value
        self.set_value(total)
    
    def subtract(self, other_virt_number):
        total = self.value - other_virt_number.value
        self.set_value(total)

    def multiply(self, other_virt_number):
        total = self.value * other_virt_number.value
        self.set_value(total)
    
    def divide(self, other_virt_number):
        total = self.value / other_virt_number.value
        self.set_value(total)
    
    def get_length(self):
        raise Exception("This is a float virtual variable class and its length cannot be requested")

    def convert_to_token(self):
        return Token(VIRTUAL_FLOAT, copy.deepcopy(self))
    
    def __str__(self):
        return f"Float_virtual({self.value})"

class String_virtual(Virtual_variable):
    def check_valid(self, value):
        if not type(value) == str:
            raise Exception(f"{value} is not a valid string value")
        else:
            return True
    
    # sets the value of this variable to itself followed by the value of another virtual string
    def concatenate(self, other_virt_string):
        new_value = self.get_value() + other_virt_string.get_value()
        self.set_value(new_value)

    # Allows reading of an individual letter or a series of letters within the string virtual
    def read_item(self, index):
        if type(index) == int:
            output = self.value[index]
        elif type(index) == list and len(index) == 2:
            output = ""
            for position in range(index[0].get_value(), index[1].get_value()):
                output += (self.value[position])
        else:
            raise Exception(f"{index} is an invalid index")
        return output

    def convert_to_token(self):
        return Token(VIRTUAL_STRING, copy.deepcopy(self))

    def __str__(self):
        return f"String_virtual({self.value})"

class Character_virtual(Virtual_variable):
    # Check text is of a valid format for chars (any single char)
    def check_valid(self, value):
        if not (len(value) == 1 and type(value) == str):
            raise Exception(f"{value} is not a valid character value, it must contain only one ascii character")
        else:
            return True

    def convert_to_token(self):
        return Token(VIRTUAL_CHARACTER, copy.deepcopy(self))

    def __str__(self):
        return f"Character_virtual({self.value})"

ANYBOOLEANREGEX = "^((?:TRUE)|(?:FALSE))$"
class Boolean_virtual(Virtual_variable):
    # Check text is of a valid format for booleans
    def check_valid(self, value):
        if not (type(value) == int or (re.match(ANYBOOLEANREGEX, value) and type(value) == str)):
            raise Exception(f"{value} is not a valid boolean value")
        else:
            return True

    # Set value 1 or 0 (true or false), related to the inputted value
    def set_value(self, value):
        if self.check_valid(value):
            if value == "TRUE" or value == 1:
                self.value = 1
            elif value == "FALSE" or value == 0:
                self.value = 0
            else:
                raise Exception("check_valid has failed")
    
    def output_representation(self):
        if self.value == 1:
            output = "TRUE"
        else:
            output = "FALSE"
        return output
    
    def get_length(self):
        raise Exception("This is a boolean virtual variable class and its length cannot be requested")

    def convert_to_token(self):
        return Token(VIRTUAL_BOOLEAN, copy.deepcopy(self))

    def __str__(self):
        return f"Boolean_virtual({self.value})"

class List_based_virtual(Virtual_variable):
    # It should be noted that this only checks the validity of the structure entered and not the items within,
    # this is done when the items within are instantiated during the set_value procedure
    def check_valid(self, value):
        if not type(value) == list:
            raise Exception(f"{value} is not a valid expression for a list")
        else:
            return True
    
    def set_value(self, value):
        if self.check_valid(value):
            new_value = []
            # ensures that every item within the data structure is also a virtual variable by checking and converting
            for item in value:
                if isinstance(item, Virtual_variable):
                    new_value.append(item)
                elif isinstance(item, Token):
                    new_item = convert_to_virtual_variable(item)
                    new_value.append(new_item)
                else:
                    raise Exception(f"{item} is not a virtual variable or a token")
            self.value = new_value

    # Allows reading of an individual item or a series of items within the list based virtual
    def read_item(self, index):
        if type(index) == int:
            output = self.value[index]
        elif type(index) == list and len(index) == 2:
            output = []
            for position in range(index[0].get_value(), index[1].get_value()+1):
                output.append(self.value[position])
        else:
            raise Exception(f"{index} is an invalid index")
        return output

    def output_representation(self):
        output = "["
        index = 0
        while index <= len(self.value)-2:
            item = self.value[index]
            output_item = item.output_representation()
            output += output_item + ", "
            index += 1
        if len(self.value) != 0:
            output += self.value[len(self.value)-1].output_representation()
        output += "]"
        return output

    def convert_to_token(self):
        raise Exception("This is an abstract list-based virtual variable class and cannot be converted to token")
    
    def __str__(self):
        return f"Unknown_List-based_virtual({self.value})"

# Virtual Tuple, mostly uses the base functionality of the list-based virtual abstract class
class Tuple_virtual(List_based_virtual):
    def convert_to_token(self):
        return Token(VIRTUAL_TUPLE, copy.deepcopy(self))

    def __str__(self):
        return f"Tuple_virtual({self.value})"

# Arrays have insert and remove as well as standard tuple properties
class Array_virtual(List_based_virtual):
    # Places the item in the index value position
    def append_item(self, append_value):
        to_insert = convert_to_virtual_variable(append_value)
        new_list = self.value + [to_insert]
        self.value = new_list
    
    # Removes the item at the index specified
    def remove_item(self, index):
        # input validation
        if not type(index) == int:
            raise Exception(f"{index} is an invalid index")
        else:
            end_list = self.value[0:index] + self.value[(index+1):len(self.value)]
            self.value = end_list
    
    # appends another array's values to the end of this one's
    def join(self, other_virt_array):
        new_value = self.get_value() + other_virt_array.get_value()
        self.set_value(new_value)
            
    def convert_to_token(self):
        return Token(VIRTUAL_ARRAY, copy.deepcopy(self))
    
    def __str__(self):
        return f"Array_virtual({self.value})"

# General stack and queue base class, stacks and queues are designed to have the last-most item
# be the one that can be viewed/removed
class Stack_queue_based_virtual(Virtual_variable):
    # Stacks and Queues are instantiated with no values and then added to
    def __init__(self, value):
        if value:
            self.value = value
        else:
            self.value = []

    def set_value(self, value):
        raise Exception("This object's value cannot be set")
    
    def get_value(self):
        raise Exception("Stack/queue values cannot be retrieved")
    
    # Remove the lastmost variable
    def pop_item(self):
        length = len(self.value)
        if length == 0:
            raise Exception("Stack or queue is empty, cannot pop another item")
        else:
            new_list = self.value[0:length-1]
            self.value = new_list
    
    # Read the lastmost variable
    def read_item(self):
        return self.value[-1].convert_to_token()
    
    def output_representation(self):
        raise Exception("This is a stack/queue virtual variable class \
            and cannot be outputted")
    
    def convert_to_token(self):
        raise Exception("This is an abstract stack/queue virtual variable class and \
            cannot be converted to token")

    def __str__(self):
        return f"Unknown_Stack_or_Queue_type({self.value})"

class Stack_virtual(Stack_queue_based_virtual):
    # Places the item at the end of the list (The position that is removed first)
    def add_item(self, item):
        to_add = convert_to_virtual_variable(item)
        self.value += [to_add]
    
    def convert_to_token(self):
        return Token(VIRTUAL_STACK, copy.deepcopy(self))
    
    def __str__(self):
        return f"Stack_virtual({self.value})"

class Queue_virtual(Stack_queue_based_virtual):
    # Places the item at the beginning of the list (The position that is removed last)
    def add_item(self, item):
        to_add = convert_to_virtual_variable(item)
        self.value = [to_add] + self.value
    
    def convert_to_token(self):
        return Token(VIRTUAL_QUEUE, copy.deepcopy(self))
    
    def __str__(self):
        return f"Queue_virtual({self.value})"

# Priority queue items in the value list will first contain a virtual variable and 
#   then a priority rating (integer)
class Priority_queue_virtual(Stack_queue_based_virtual):
    def read_item(self):
        return self.value[-1][0].convert_to_token()
    
    # Places the item in the queue such that it is order by priority (highest out first)
    def add_item(self, item, priority):
        converted_item = convert_to_virtual_variable(item)
        queue_length = len(self.value)
        location_found = False
        queue_index = 0
        # finds the first item with a priority value greater than or equal to the 
        #   new item and then adds it just before it
        if queue_length != 0:
            while (not location_found) and (queue_index < queue_length):
                if self.value[queue_index][1] >= priority:
                    location_found = True
                else:
                    queue_index += 1
            if not location_found and priority > self.value[len(self.value)-1][1]:
                queue_index = len(self.value)
                location_found = True
            new_value = self.value[0:queue_index] + [[converted_item, priority]] \
                + self.value[queue_index:queue_length]
            if not location_found:
                raise Exception(f"no valid insertion location found, priority = {priority}")
        else:
            new_value = [[converted_item, priority]]
        self.value = new_value
        
    def convert_to_token(self):
        return Token(VIRTUAL_PRIORITY_QUEUE, copy.deepcopy(self))

    def __str__(self):
        return f"Priority_queue_virtual({self.value})"

# Used as a half-way step in the construction of dictionaries
class Dictionary_pair(Virtual_variable):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def get_key(self):
        return self.key

    def get_value(self):
        return self.value

    def get_length(self):
        raise Exception("This is a dictionary pair virtual variable class and its length cannot be requested")
    
    def output_representation(self):
        raise Exception("This is a dictionary pair virtual variable class and cannot be outputted")
    
    def convert_to_token(self):
        return Token(VIRTUAL_DICTIONARY_PAIR, copy.deepcopy(self))

    # __deepcopy__ adapted from StackOverflow answer: https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.key, memo),
                copy.deepcopy(self.value, memo))
            memo[id_self] = _copy 
        return _copy

    def __str__(self):
        return f"Virtual_Dictionary_Pair(key({self.key})_value({self.value})"

from math import log

class Dictionary_virtual(Virtual_variable):
    def __init__(self, dictionary_length, max_length, dictionary_list):
        if dictionary_length != None:
            self.dictionary_length = dictionary_length
            self.max_length = max_length
            self.dictionary_list = dictionary_list
        else:
            self.set_value(dictionary_list)

    def check_valid(self, value):
        if not type(value) == list:
            raise Exception(f"{input} is not a valid dictionary value")
        else:
            return True

    # Uses the hash function to produce a number related to the inputted key 
    #   which is less than the current max length of the dictionary
    # The use of a hash function means that the outputs of this function are 
    #   evenly distributed but can be consistently derived from the key
    def hash_key(self, key):
        full_hash = hash(key)
        dictionary_hash = abs(full_hash) % self.max_length
        return dictionary_hash
    
    def set_value(self, input):
        if self.check_valid(input):
            base_pairs_list = []
            for pair in input:
                pair = convert_to_virtual_variable(pair)
                if not type(pair) == Dictionary_pair:
                    raise Exception(f"Invalid Token pair input: {pair}")
                else:
                    new_pair = [pair.get_key(), pair.get_value()]
                base_pairs_list.append(new_pair)
            # finds the smallest 2^(n+1) for 2^n > len(base_pairs_list)
            # aka finds a length that the list can be which is a multiple of 
            #   two and at least double the number of pairs
            if len(base_pairs_list) == 0:
                # Edge case where length == 0 creates a ValueError as log of 0 is undefined
                resized_max_length = 2
            else:
                resized_max_length = 2^(round(log(len(base_pairs_list), 2))+1)
            # 8 is the minimum length to avoid frequeunt resizing 
            #   for small dictionaries
            if resized_max_length < 8:
                resized_max_length = 8
            self.dictionary_length = 0
            self.resize(base_pairs_list, resized_max_length)
    
    def get_value(self):
        raise Exception("Dictionary values cannot be retrieved")
    
    # input_pairs_list can be either a non-dictionary list from 
    #   set_value or a previous dictionary list
    # it doesn't matter that these have different formats as the 
    #   algorithm only uses the first two attributes
    # of the pairs in a previous dictionary list
    # a dictionary item has three attributes, stored in the list 
    #   in the order that follows:
    #      -key, the value that is hashed when a pair is queried
    #      -value, the value that is produced when a pair is queried
    #      -used, a value that is used to show whether the list position 
    #          has been used in a collision, if used is True then a 
    #          search will continue past the position even if the key 
    #          hashes are different
    def resize(self, input_pairs_list, new_max_length):
        # Filling the list with empty sections
        self.max_length = new_max_length
        self.dictionary_list = [[None, None, False]] * new_max_length
        # inserts every pair in the 
        for pair in input_pairs_list:
            if pair[0] != None:
                self.pair_insertion(Dictionary_pair(pair[0], pair[1]))
    
    def pair_insertion(self, dict_pair):
        pair_key_virt_var = dict_pair.get_key()
        pair_value_virt_var = dict_pair.get_value()
        pair_key = pair_key_virt_var.get_value()
        if pair_key in self.get_key_values():
            raise Exception("pair with this key value already exists!")
        else:
            pair_value = pair_value_virt_var.get_value()
            if (self.dictionary_length + 1)*2 > self.max_length:
                self.resize(self.dictionary_list, self.max_length*2)
            pair_key_hash = self.hash_key(pair_key)
            position = pair_key_hash
            # variable to use to end loop
            position_found = False
            # using position as an used markers
            used = False
            while not position_found:
                # checking if position is occupied
                if self.dictionary_list[position][0] == None:
                    position_found = True
                    if self.dictionary_list[position][2] == True:
                        used = True
                else:
                    position += 1
                    if position == self.max_length:
                        position = 0
            dictionary_entry = [pair_key_virt_var, pair_value_virt_var, used]
            self.dictionary_list[position] = dictionary_entry
            self.dictionary_length += 1
    
    def pair_removal(self, pair_key_virt_var):
        pair_key = pair_key_virt_var.get_value()
        pair_key_hash = self.hash_key(pair_key)
        position = pair_key_hash
        # variable to use to end loop
        search_complete = False
        position_found = False
        while not search_complete:
            # checking if the pair is at the current position
            current_position_key = self.dictionary_list[position][0].get_value()
            current_position_hash = self.hash_key(current_position_key)
            if current_position_key == pair_key:
                search_complete = True
                position_found = True
            # Checks if there has been a collision
            elif current_position_hash == pair_key_hash or \
                self.dictionary_list[position][2] == True:
                position += 1
                if position == self.max_length:
                    postion = 0
                # if we are back at the original position then the pair 
                #   also has not been found
                if position == pair_key_hash:
                    search_complete = True
        dictionary_entry = [None, None, True]
        self.dictionary_list[position] = dictionary_entry
        self.dictionary_length -= 1

    def find_value(self, pair_key_virt_var):
        pair_key = pair_key_virt_var.get_value()
        pair_key_hash = self.hash_key(pair_key)
        search_complete = False
        position_found = False
        position = pair_key_hash
        while not search_complete:
            # checking if the pair is at the current position
            if self.dictionary_list[position][0]:
                current_position_key = self.dictionary_list[position][0].get_value()
                current_position_hash = self.hash_key(current_position_key)
                if current_position_key == pair_key:
                    search_complete = True
                    position_found = True
                else:
                    position += 1
                    if position >= self.max_length:
                        position = 0
            else:
                search_complete = True
            # if we are back at the original position then 
            #   the pair also has not been found
            if position == pair_key_hash:
                search_complete = True
        # Output control
        if not position_found:
            raise Exception(f"{pair_key} is not available as a key \
                in the dictionary")
        else:
            pair_value = self.dictionary_list[position][1]
            return pair_value
    
    # for internal use!
    def get_keys(self):
        keys = []
        for pair in self.dictionary_list:
            if pair[0]:
                keys.append(pair[0])
        return keys
    
    def get_key_values(self):
        keys = self.get_keys()
        key_values = []
        for key in keys:
            key_values.append(key.get_value())
        return key_values

    def key_list(self):
        keys = self.get_keys()
        return convert_to_virtual_variable(Token(ARRAY,keys))
    
    def get_length(self):
        return self.dictionary_length
    
    def output_representation(self):
        raise Exception("This is a dictionary virtual variable class \
            and cannot be outputted")
    
    def convert_to_token(self):
        return Token(VIRTUAL_DICTIONARY, copy.deepcopy(self))
    
    # __deepcopy__ adapted from StackOverflow answer: 
    #   https://stackoverflow.com/a/46939443 
    # by: https://stackoverflow.com/users/541136/russia-must-remove-putin
    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                copy.deepcopy(self.dictionary_length, memo),
                copy.deepcopy(self.max_length, memo),
                copy.deepcopy(self.dictionary_list, memo))
            memo[id_self] = _copy 
        return _copy

    def __str__(self):
        return f"Dictionary({self.dictionary_list})"