from mainScript import *

print(form_AST(process_text("variable_name = 3+(5*3+1)")))
print(form_AST(process_text("array_variable = [\"Alice\", \"Bob\", \"Eve\"]")))
print(form_AST(process_text("IF number ISEQUALTO 5 DO ")))