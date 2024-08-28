### Documentation of the BNF, Detailed Language Syntax, and Features
#defining the syntax for the program

### A program can be a single statement or a series of statements.
<program> ::= <statement> | <statement> ";" <program>

### Defining a statement which can be a function definition, expression, or boolean expression
<statement> ::= <function_def> | <expression> | <boolean_expr>

### Function definition syntax
<function_def> ::= "Defun" "(" <identifier> "," <parameters> ")" "(" <identifier> <rel_op> <bool_vals> ")" "or" "(" <expression> ")" | "Defun" "(" <identifier> "," <parameters> ")" "(" <identifier> <rel_op> <number> ")" "or" "(" <expression> ")" | "Defun" "(" <identifier> "," <parameters> ")" <expression>
"Defun" is used to define a function, followed by function name, parameters, and body.

### Parameters of a function
<parameters> ::= <identifier> | <parameters> "," <parameters>
Parameters can be a single identifier or a comma-separated list of identifiers.

### An expression in the language
<expression> ::= <term> | "(" <expression> ")" | <expression> <rel_op> <term> | <expression> <add_op> <term> | <expression> <bool_op> <term> | <expression> <mul_op> <term> | <lambda_expr> | <function_call>  
An expression can be a term, a term with addition or subtraction, a lambda expression, or a function call.

### Terms and factors for arithmetic expressions
<term> ::= <factor> | "(" <term> ")" | <term> <rel_op> <factor> |<term> <mul_op> <factor> | <term> <add_op> <factor> | <term> <bool_op> <factor>
<factor> ::= <bool_vals> | <number> | <function_call> | <lambda_expr>
Terms are composed of factors, which can be numbers, identifiers, expressions in parentheses, function calls, or lambda expressions.

### Lambda expression syntax
<lambda_expr> ::= "lambd" "(" <parameters> ")" "(" <expression> ")"
"lambd" introduces a lambda expression with parameters and a body.

### Function call syntax
<function_call> ::= <identifier> "(" <arguments> ")"
Function call includes the function name and arguments.

### Arguments for function calls
<arguments> ::= <number> | <bool_vals> | <function_call> | <arguments> "," <arguments>
Arguments can be a single expression or a list of expressions separated by commas.

### Boolean expressions and relations
<boolean_expr> ::= <relation> | <boolean_expr> <bool_op> <relation>
<relation> ::= <expression> <rel_op> <expression> | <unary_op> <expression>
Boolean expressions include relations and logical operations.

### Arithmetic and boolean operators
<add_op> ::= "+" | "-"
<mul_op> ::= "*" | "/"
<rel_op> ::= "==" | "!=" | ">" | "<" | ">=" | "<="
<bool_op> ::= "&&" | "||"
<unary_op> ::= "not"
<bool_vals> ::= "True" | "False"
Operators for addition, multiplication, comparison, and boolean logic.

### Identifiers and numbers
<identifier> ::= [a-zA-Z_][a-zA-Z0-9_]*
<number> ::= [0-9]+


### User Guide for Running the Interpreter
At the start of the program, the following screen will appear:
+------------------------------------------------------------------------------------------------------+
|            would you like to initiate the interactive mode?                                          |
|            enter Y in order to activate it or enter N to access the options of:                      |
|            1) loading code from a lambda file                                                        |
|            2) activating the test suite                                                              |
|            >>>                                                                                       |
+------------------------------------------------------------------------------------------------------+

The user can enter either capital y ('Y') or capital n ('N'):
if the user entered Y Then interactive mode will start and the user can begin to write code at the following screen.  
+------------------------------------------------------------------------------------------------------+
|	>>>							                                                                                     |
+------------------------------------------------------------------------------------------------------+

And if the user entered N then the following screen will appear:
+------------------------------------------------------------------------------------------------------+
|	would you like to initiate the test suite?                                                           |
|	enter Y in order to activate it or enter N to access the option of loading code from a lambda file   |
|	>>>			                                                                                				     |
+------------------------------------------------------------------------------------------------------+

Then the user can choose to initiate the prewritten test suite by entering Y or to run code that is written on lambda file that is stored on the user's machine.
If the user entered N from that point, then the following screen will appear:
+------------------------------------------------------------------------------------------------------+
|	enter path for the file with .lambda suffix			                                                     |
|	>>>								                                                                                   |
+------------------------------------------------------------------------------------------------------+
Then the user will enter the path for the location of which the lambda file is stored, 
and then the program will execute it.

### Design Report
Key Design Decision ####
Functional Programming Approach: The project uses functional programming, which focuses on using functions that don't change data and have no side effects. This makes the code more predictable and easier to debug.
Use of Recursion: The project relies on recursion to handle tasks like parsing and evaluating expressions. This helps to easily manage nested structures, such as mathematical expressions with parentheses.
Enforcing Immutability: By keeping data unchanged (immutability), the code avoids accidental changes to the state, making it easier to understand and reducing the chance of bugs.

Challenges Faced ####
Managing Recursion: A key challenge was handling the call stack during recursion, especially with deeply nested expressions. If not managed well, this could cause stack overflow errors if the recursion goes too deep.
Parsing Complex Syntax: Another challenge was developing a parser to handle complex expressions with various operators and functions. The parser needed to be robust enough to correctly understand and process the structure of these expressions, even when there were errors or unexpected inputs.

### Solutions to Challenges
Optimizing Recursion: We used tail call optimization (TCO) to reduce the risk of stack overflow. TCO reuses stack space for certain recursive calls, allowing the interpreter to handle deeper recursion without using too much memory.
Custom Error Handling: We added custom error handling to give clear error messages and prevent crashes. This included creating special exception classes and making sure the interpreter can manage and pass on errors properly.
Parser Optimization: We improved the parser with techniques like lookahead tokens and a clear grammar that focuses on operator precedence and correct expression grouping. This helps the parser efficiently handle complex inputs.

### Answers to Theoretical Questions
#### 1. *What is Functional Programming and How is it Applied Here?*
Functional programming is a way of writing programs where you use functions that don't change data or depend on external factors. In this project, it’s used by keeping data unchanged, using simple functions, and recursion. This ensures the interpreter behaves consistently and predictably.
#### 2. *Explain Lambda Calculus and Its Relevance to the Project*  
Lambda calculus is a system that forms the base of functional programming languages, allowing you to express computations using functions. This project uses lambda functions (anonymous functions) in expressions, which is key to how the interpreter processes and evaluates code.
#### 3. *Why Choose Recursion Over Iteration?*
Recursion was chosen because it's better suited for handling nested structures like abstract syntax trees (ASTs) used in this project. It simplifies managing complex structures and fits well with the functional programming approach used here.
#### 4. *What are the Benefits and Drawbacks of Immutability?*
Immutability, or keeping data unchanged, helps make the code easier to understand and less prone to errors. It also works well with concurrent processes. However, it can slow down performance since new copies of data have to be created instead of modifying existing ones. In this project, the benefits of immutability, like consistency, outweigh the downsides.
