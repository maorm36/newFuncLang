
# imports
import ast
from pickletools import StackObject
from shutil import ExecError
import sys
from math import e, isnan

# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
EOF = "EOF"

# eg for lambda use is: lambd (b,a) (b * a)
KEYWORDS = {"Defun", "lambd"}

OPERATORS = {"/", "*", "-", "+", "%", "!"}

LOGICOPERATORS = {"||", "&&"}

COMPARATORS = {"==", "!=", ">=", "<=", ">", "<"}

PUNCTUATIONS = {"(", ")", ",", "{", "}", ";"}

ORFUNC = "ORFUNC"

(
    INTEGER,
    BOOLEAN,
    KEYWORD,
    IDENTIFIER,
    OPERATOR,
    PUNCTUATION,
    COMPARATOR,
    LOGICOPERATOR,
) = (
    "INTEGER",
    "BOOLEAN",
    "KEYWORD",
    "IDENTIFIER",
    "OPERATOR",
    "PUNCTUATION",
    "COMPARATOR",
    "LOGICOPERATOR",
)

# LLLLLLLLLLL             EEEEEEEEEEEEEEEEEEEEEEXXXXXXX       XXXXXXXEEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRR
# L:::::::::L             E::::::::::::::::::::EX:::::X       X:::::XE::::::::::::::::::::ER::::::::::::::::R
# L:::::::::L             E::::::::::::::::::::EX:::::X       X:::::XE::::::::::::::::::::ER::::::RRRRRR:::::R
# LL:::::::LL             EE::::::EEEEEEEEE::::EX::::::X     X::::::XEE::::::EEEEEEEEE::::ERR:::::R     R:::::R
#   L:::::L                 E:::::E       EEEEEEXXX:::::X   X:::::XXX  E:::::E       EEEEEE  R::::R     R:::::R
#   L:::::L                 E:::::E                X:::::X X:::::X     E:::::E               R::::R     R:::::R
#   L:::::L                 E::::::EEEEEEEEEE       X:::::X:::::X      E::::::EEEEEEEEEE     R::::RRRRRR:::::R
#   L:::::L                 E:::::::::::::::E        X:::::::::X       E:::::::::::::::E     R:::::::::::::RR
#   L:::::L                 E:::::::::::::::E        X:::::::::X       E:::::::::::::::E     R::::RRRRRR:::::R
#   L:::::L                 E::::::EEEEEEEEEE       X:::::X:::::X      E::::::EEEEEEEEEE     R::::R     R:::::R
#   L:::::L                 E:::::E                X:::::X X:::::X     E:::::E               R::::R     R:::::R
#   L:::::L         LLLLLL  E:::::E       EEEEEEXXX:::::X   X:::::XXX  E:::::E       EEEEEE  R::::R     R:::::R
# LL:::::::LLLLLLLLL:::::LEE::::::EEEEEEEE:::::EX::::::X     X::::::XEE::::::EEEEEEEE:::::ERR:::::R     R:::::R
# L::::::::::::::::::::::LE::::::::::::::::::::EX:::::X       X:::::XE::::::::::::::::::::ER::::::R     R:::::R
# L::::::::::::::::::::::LE::::::::::::::::::::EX:::::X       X:::::XE::::::::::::::::::::ER::::::R     R:::::R
# LLLLLLLLLLLLLLLLLLLLLLLLEEEEEEEEEEEEEEEEEEEEEEXXXXXXX       XXXXXXXEEEEEEEEEEEEEEEEEEEEEERRRRRRRR     RRRRRRR


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self._str_()


def recurse(node):
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mult) or isinstance(node.op, ast.Div):
            return (
                "(" + recurse(node.left) + recurse(node.op) + recurse(node.right) + ")"
            )
        else:
            return (
                "(" + recurse(node.left) + recurse(node.op) + recurse(node.right) + ")"
            )
    if isinstance(node, ast.Add):
        return "+"
    if isinstance(node, ast.Sub):
        return "-"
    if isinstance(node, ast.Mult):
        return "*"
    if isinstance(node, ast.Div):
        return "/"
    if isinstance(node, ast.Mod):
        return "%"
    if isinstance(node, ast.Eq):
        return "=="
    if isinstance(node, ast.NotEq):
        return "!="
    if isinstance(node, ast.Gt):
        return ">"
    if isinstance(node, ast.GtE):
        return ">="
    if isinstance(node, ast.Lt):
        return "<"
    if isinstance(node, ast.LtE):
        return "<="
    if isinstance(node, ast.And):
        return "&&"
    if isinstance(node, ast.Or):
        return "||"

    if isinstance(node, ast.BoolOp):
        return (
            "("
            + recurse(node.values[0])
            + recurse(node.op)
            + recurse(node.values[1])
            + ")"
        )

    if isinstance(node, ast.Compare):
        return (
            "("
            + recurse(node.left)
            + recurse(node.ops[0])
            + recurse(node.comparators[0])
            + ")"
        )

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return "(0 - " + recurse(node.operand) + ")"
        elif isinstance(node.op, ast.UAdd):
            return "(0 + " + recurse(node.operand) + ")"
        else:
            return "(!(" + recurse(node.operand) + "))"
    if isinstance(node, ast.Num):
        return str(node.n)
    if isinstance(node, ast.Name):
        return str(node.id)
    if isinstance(node, ast.NameConstant):
        return str(node.value)
    if isinstance(node, ast.Call):
        t = ""
        for x in node.args:
            t += recurse(x) + ","
        t = t[0 : len(t) - 1]
        return "(" + node.func.id + "(" + t + "))"

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.BoolOp):
            return (
                "("
                + recurse(child.values[0])
                + recurse(child.op)
                + recurse(child.values[1])
                + ")"
            )
        if isinstance(child, ast.BinOp):
            return (
                "("
                + recurse(child.left)
                + recurse(child.op)
                + recurse(child.right)
                + ")"
            )
        if isinstance(child, ast.Compare):
            return (
                "("
                + recurse(child.left)
                + recurse(child.ops[0])
                + recurse(child.comparators[0])
                + ")"
            )
        return recurse(child)


def search_expr(node):
    returns = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Expr):
            return child
        returns.append(search_expr(child))
    for ret in returns:
        if isinstance(ret, ast.Expr):
            return ret
    return None


def OrderParanthText(text):
    try:
        formula = text
        a = ast.parse(formula)
        expr = search_expr(a)
        if expr is not None:
            return recurse(expr)
    except:
        raise Exception("Syntax error")


class Lexer:
    def __init__(self, text):
        try:
            self.text = text

            boolFlagOrderParanthText = False

            if "Defun" not in str(self.text) and ";" not in str(self.text):
                for x in LOGICOPERATORS:
                    if x in str(self.text):
                        if x == "&&":
                            text = text.replace(x, " and ")
                        else:
                            text = text.replace(x, " or ")
                self.text = OrderParanthText(text)

            self.pos = 0
            if len(self.text) == 0:
                self.current_char = None
            self.current_char = self.text[self.pos]
        except:
            raise Exception("Syntax error")

    def error(self):
        raise Exception("Invalid character")

    def getNextChar(self):
        if self.pos + 1 < len(self.text):
            return str(self.text[self.pos + 1])
        else:
            return None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ""

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        return int(result)

    def identifier(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalnum()):
            result += self.current_char
            self.advance()

        if result in KEYWORDS:
            return Token(KEYWORD, result)

        elif result == "True":
            return Token(BOOLEAN, True)

        elif result == "False":
            return Token(BOOLEAN, False)

        elif result == "or":
            return Token(ORFUNC, "or")

        else:
            return Token(IDENTIFIER, result)

    def get_next_token(self):
        while self.current_char is not None:
            # skip whitespaces
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # if the char is a punctuation then return it as token and advance by one char
            elif self.current_char in PUNCTUATIONS:
                token = Token(PUNCTUATION, self.current_char)
                self.advance()
                return token

            # identify int nums as token
            if self.current_char.isdigit():
                return Token(INTEGER, self.number())

            # if the char is math operator then return it as token and advance by one char
            elif self.current_char in OPERATORS and self.current_char != "!":
                token = Token(OPERATOR, self.current_char)
                self.advance()
                return token

            # if the char is logic operator then return it as token and advance by two char
            elif self.current_char == "|":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "|":
                        token = Token(LOGICOPERATOR, "||")
                        self.advance()
                        self.advance()
                        return token
                else:
                    self.error()

            elif self.current_char == "&":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "&":
                        token = Token(LOGICOPERATOR, "&&")
                        self.advance()
                        self.advance()
                        return token
                else:
                    self.error()

            # if the char is a comparator then return it as token and advance by two char
            elif self.current_char == "=":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "=":
                        token = Token(COMPARATOR, "==")
                        self.advance()
                        self.advance()
                        return token
                else:
                    self.error()

            elif self.current_char == "!":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "=":
                        token = Token(COMPARATOR, "!=")
                        self.advance()
                        self.advance()
                        return token
                    else:
                        token = Token(OPERATOR, "!")
                        self.advance()
                        return token
                else:
                    token = Token(OPERATOR, "!")
                    self.advance()
                    return token

            elif self.current_char == ">":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "=":
                        token = Token(COMPARATOR, ">=")
                        self.advance()
                        self.advance()
                        return token
                    else:
                        token = Token(COMPARATOR, ">")
                        self.advance()
                        return token
                else:
                    token = Token(COMPARATOR, ">")
                    self.advance()
                    return token

            elif self.current_char == "<":
                if self.pos + 1 < len(self.text):
                    if self.text[self.pos + 1] == "=":
                        token = Token(COMPARATOR, "<=")
                        self.advance()
                        self.advance()
                        return token
                    else:
                        token = Token(COMPARATOR, "<")
                        self.advance()
                        return token
                else:
                    token = Token(COMPARATOR, "<")
                    self.advance()
                    return token

            # if the current char is alpha-type then identify the word by activation of identifier()
            elif self.current_char.isalpha():
                return self.identifier()

            else:
                self.error()

        return None


# PPPPPPPPPPPPPPPPP        AAA               RRRRRRRRRRRRRRRRR      SSSSSSSSSSSSSSS EEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRR
# P::::::::::::::::P      A:::A              R::::::::::::::::R   SS:::::::::::::::SE::::::::::::::::::::ER::::::::::::::::R
# P::::::PPPPPP:::::P    A:::::A             R::::::RRRRRR:::::R S:::::SSSSSS::::::SE::::::::::::::::::::ER::::::RRRRRR:::::R
# PP:::::P     P:::::P  A:::::::A            RR:::::R     R:::::RS:::::S     SSSSSSSEE::::::EEEEEEEEE::::ERR:::::R     R:::::R
#   P::::P     P:::::P A:::::::::A             R::::R     R:::::RS:::::S              E:::::E       EEEEEE  R::::R     R:::::R
#   P::::P     P:::::PA:::::A:::::A            R::::R     R:::::RS:::::S              E:::::E               R::::R     R:::::R
#   P::::PPPPPP:::::PA:::::A A:::::A           R::::RRRRRR:::::R  S::::SSSS           E::::::EEEEEEEEEE     R::::RRRRRR:::::R
#   P:::::::::::::PPA:::::A   A:::::A          R:::::::::::::RR    SS::::::SSSSS      E:::::::::::::::E     R:::::::::::::RR
#   P::::PPPPPPPPP A:::::A     A:::::A         R::::RRRRRR:::::R     SSS::::::::SS    E:::::::::::::::E     R::::RRRRRR:::::R
#   P::::P        A:::::AAAAAAAAA:::::A        R::::R     R:::::R       SSSSSS::::S   E::::::EEEEEEEEEE     R::::R     R:::::R
#   P::::P       A:::::::::::::::::::::A       R::::R     R:::::R            S:::::S  E:::::E               R::::R     R:::::R
#   P::::P      A:::::AAAAAAAAAAAAA:::::A      R::::R     R:::::R            S:::::S  E:::::E       EEEEEE  R::::R     R:::::R
# PP::::::PP   A:::::A             A:::::A   RR:::::R     R:::::RSSSSSSS     S:::::SEE::::::EEEEEEEE:::::ERR:::::R     R:::::R
# P::::::::P  A:::::A               A:::::A  R::::::R     R:::::RS::::::SSSSSS:::::SE::::::::::::::::::::ER::::::R     R:::::R
# P::::::::P A:::::A                 A:::::A R::::::R     R:::::RS:::::::::::::::SS E::::::::::::::::::::ER::::::R     R:::::R
# PPPPPPPPPPAAAAAAA                   AAAAAAARRRRRRRR     RRRRRRR SSSSSSSSSSSSSSS   EEEEEEEEEEEEEEEEEEEEEERRRRRRRR     RRRRRRR


# node types for the AST
class Num:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"


class Bool:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Bool({self.value})"


class CompOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"CompOp({self.left}, {self.op}, {self.right})"


class advancedFuncOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"advancedFuncOp({self.left}, {self.op}, {self.right})"


class FuncOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"FuncOp({self.left}, {self.op}, {self.right})"


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"

    def ifLeftIsNum(self):
        return not isnan(self.left)

    def ifRightIsNum(self):
        return not isnan(self.right)


class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.expr})"


class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Defun({self.name}, {self.params}, {self.body})"


class LambdaExpr:
    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Lambd({self.params}, {self.body})"


class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FuncCall({self.name}, {self.args})"


class Parser:
    def __init__(self, lexer, interpreter):
        self.lexer = lexer
        self.interpreterCopy = interpreter
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Syntax error")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self, func_name):
        token = self.current_token

        if token.type == KEYWORD and token.value == "lambd":
            return self.lambda_expr()

        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token.value)

        elif token.type == BOOLEAN:
            self.eat(BOOLEAN)
            return Bool(token.value)

        elif token.value in self.interpreterCopy.global_env.keys():
            func_name = token.value
            self.eat(IDENTIFIER)  # func name
            self.eat(PUNCTUATION)  # (
            args = []
            args.append(self.expr(""))
            while (
                self.current_token is not None
                and self.current_token.type == PUNCTUATION
                and self.current_token.value == ","
            ):
                self.eat(PUNCTUATION)  # ,
                args.append(self.expr(""))

            self.eat(PUNCTUATION)  # )
            return FuncCall(func_name, args)

        elif token.type == IDENTIFIER and token.value != func_name:
            self.eat(IDENTIFIER)
            return token.value

        elif token.type == IDENTIFIER:
            func_name = token.value
            self.eat(IDENTIFIER)  # func name
            self.eat(PUNCTUATION)  # (
            args = []
            args.append(self.expr(""))
            while (
                self.current_token is not None
                and self.current_token.type == PUNCTUATION
                and self.current_token.value == ","
            ):
                self.eat(PUNCTUATION)  # ,
                args.append(self.expr(""))
            self.eat(PUNCTUATION)  # )
            return FuncCall(func_name, args)

        elif (
            token.type == PUNCTUATION
            and token.value == "("
            and self.lexer.current_char == "-"
        ):
            self.eat(PUNCTUATION)
            self.eat(OPERATOR)
            num = self.current_token.value
            self.eat(INTEGER)
            self.eat(PUNCTUATION)
            return Num(-1 * num)

        elif token.type == PUNCTUATION and token.value == "(":
            self.eat(PUNCTUATION)
            expr = self.expr(func_name)
            self.eat(PUNCTUATION)
            return expr

        elif token.type == OPERATOR and token.value == "!":
            self.eat(OPERATOR)
            expr = self.factor(func_name)
            return UnaryOp("!", expr)

        else:
            self.error()

    def term(self, func_name):
        left = self.factor(func_name)

        while (
            self.current_token is not None
            and self.current_token.type == OPERATOR
            and (
                self.current_token.value == "*"
                or self.current_token.value == "/"
                or self.current_token.value == "%"
                or self.current_token.value == "-"
                or self.current_token.value == "+"
            )
        ):
            op = self.current_token.value
            self.eat(OPERATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == COMPARATOR
            and (
                self.current_token.value == "=="
                or self.current_token.value == "!="
                or self.current_token.value == ">"
                or self.current_token.value == "<"
                or self.current_token.value == ">="
                or self.current_token.value == "<="
            )
        ):
            op = self.current_token.value
            self.eat(COMPARATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == LOGICOPERATOR
            and (self.current_token.value == "&&" or self.current_token.value == "||")
        ):
            op = self.current_token.value
            self.eat(LOGICOPERATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == ORFUNC
            and self.current_token.value == "or"
        ):
            op = self.current_token.value
            self.eat(ORFUNC)
            right = self.factor(func_name)
            left = advancedFuncOp(left, op, right)

        return left

    def expr(self, func_name):
        left = self.term(func_name)

        while (
            self.current_token is not None
            and self.current_token.type == OPERATOR
            and (
                self.current_token.value == "*"
                or self.current_token.value == "/"
                or self.current_token.value == "%"
                or self.current_token.value == "-"
                or self.current_token.value == "+"
            )
        ):
            op = self.current_token.value
            self.eat(OPERATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == COMPARATOR
            and (
                self.current_token.value == "=="
                or self.current_token.value == "!="
                or self.current_token.value == ">"
                or self.current_token.value == "<"
                or self.current_token.value == ">="
                or self.current_token.value == "<="
            )
        ):
            op = self.current_token.value
            self.eat(COMPARATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == LOGICOPERATOR
            and (self.current_token.value == "&&" or self.current_token.value == "||")
        ):
            op = self.current_token.value
            self.eat(LOGICOPERATOR)
            right = self.factor(func_name)
            left = BinOp(left, op, right)

        while (
            self.current_token is not None
            and self.current_token.type == ORFUNC
            and self.current_token.value == "or"
        ):
            op = self.current_token.value
            self.eat(ORFUNC)
            right = self.factor(func_name)

            left = advancedFuncOp(left, op, right)

        while (
            isinstance(left, FuncCall)
            and self.current_token is not None
            and self.current_token.type == PUNCTUATION
            and self.current_token.value == ","
        ):
            op = self.current_token.value
            self.eat(PUNCTUATION)
            right = self.factor(func_name)
            left = FuncOp(left, op, right)

        return left

    def params(self):
        param_list = []

        while self.current_token is not None and self.current_token.type == IDENTIFIER:
            param_list.append(self.current_token.value)
            self.eat(IDENTIFIER)

            if (
                self.current_token is not None
                and self.current_token.type == PUNCTUATION
                and self.current_token.value == ","
            ):
                self.eat(PUNCTUATION)

        return param_list

    def function_definition(self):
        self.eat(KEYWORD)  # Defun
        self.eat(PUNCTUATION)  # {
        func_name = self.current_token.value
        self.eat(IDENTIFIER)  # name Of Func
        self.eat(PUNCTUATION)  # ,
        parameters = self.params()
        self.eat(PUNCTUATION)  # }
        body = self.expr(func_name)
        return FuncDef(func_name, parameters, body)

    def lambda_expr(self):
        self.eat(KEYWORD)  # lambd
        # parameters of the lambd
        self.eat(PUNCTUATION)  # (
        parameters = self.params()
        self.eat(PUNCTUATION)  # )
        # actual logic with operators - body of lambd
        self.eat(PUNCTUATION)  # (
        body = self.expr("")
        self.eat(PUNCTUATION)  # )
        return LambdaExpr(parameters, body)

    def function_call(self):
        func_name = self.current_token.value
        self.eat(IDENTIFIER)  # funcName
        self.eat(PUNCTUATION)  # (

        args = []
        if self.current_token.type != PUNCTUATION or self.current_token.value != ")":
            if (
                self.current_token.type == IDENTIFIER
            ):  # case if we have a func within left parameter
                args.append(self.function_call())
            else:
                args.append(self.expr(""))
            while (
                self.current_token is not None
                and self.current_token.type == PUNCTUATION
                and self.current_token.value == ","
            ):
                self.eat(PUNCTUATION)  # ,

                if (
                    self.current_token.type == IDENTIFIER
                ):  # case if we have a func within the right parameters
                    args.append(self.function_call())
                else:
                    args.append(self.expr(""))
        self.eat(PUNCTUATION)  # )
        return FuncCall(func_name, args)

    def statement(self):
        token = self.current_token
        if token.type == KEYWORD and token.value == "Defun":
            return self.function_definition()
        elif token.type == KEYWORD and token.value == "lambd":
            return self.lambda_expr()
        elif token.type == IDENTIFIER:
            return self.function_call()

        else:
            return self.expr("")

    def parse(self):
        try:
            statements = []
            while self.current_token is not None:
                statements.append(self.statement())
                if (
                    self.current_token is not None
                    and self.current_token.type == PUNCTUATION
                    and self.current_token.value == ";"
                ):
                    self.eat(PUNCTUATION)
            return statements
        except Exception as e:
            raise Exception("Syntax error")


# IIIIIIIIIINNNNNNNN        NNNNNNNNTTTTTTTTTTTTTTTTTTTTTTTEEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRR   PPPPPPPPPPPPPPPPP   RRRRRRRRRRRRRRRRR   EEEEEEEEEEEEEEEEEEEEEETTTTTTTTTTTTTTTTTTTTTTTEEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRR
# I::::::::IN:::::::N       N::::::NT:::::::::::::::::::::TE::::::::::::::::::::ER::::::::::::::::R  P::::::::::::::::P  R::::::::::::::::R  E::::::::::::::::::::ET:::::::::::::::::::::TE::::::::::::::::::::ER::::::::::::::::R
# I::::::::IN::::::::N      N::::::NT:::::::::::::::::::::TE::::::::::::::::::::ER::::::RRRRRR:::::R P::::::PPPPPP:::::P R::::::RRRRRR:::::R E::::::::::::::::::::ET:::::::::::::::::::::TE::::::::::::::::::::ER::::::RRRRRR:::::R
# II::::::IIN:::::::::N     N::::::NT:::::TT:::::::TT:::::TEE::::::EEEEEEEEE::::ERR:::::R     R:::::RPP:::::P     P:::::PRR:::::R     R:::::REE::::::EEEEEEEEE::::ET:::::TT:::::::TT:::::TEE::::::EEEEEEEEE::::ERR:::::R     R:::::R
#   I::::I  N::::::::::N    N::::::NTTTTTT  T:::::T  TTTTTT  E:::::E       EEEEEE  R::::R     R:::::R  P::::P     P:::::P  R::::R     R:::::R  E:::::E       EEEEEETTTTTT  T:::::T  TTTTTT  E:::::E       EEEEEE  R::::R     R:::::R
#   I::::I  N:::::::::::N   N::::::N        T:::::T          E:::::E               R::::R     R:::::R  P::::P     P:::::P  R::::R     R:::::R  E:::::E                     T:::::T          E:::::E               R::::R     R:::::R
#   I::::I  N:::::::N::::N  N::::::N        T:::::T          E::::::EEEEEEEEEE     R::::RRRRRR:::::R   P::::PPPPPP:::::P   R::::RRRRRR:::::R   E::::::EEEEEEEEEE           T:::::T          E::::::EEEEEEEEEE     R::::RRRRRR:::::R
#   I::::I  N::::::N N::::N N::::::N        T:::::T          E:::::::::::::::E     R:::::::::::::RR    P:::::::::::::PP    R:::::::::::::RR    E:::::::::::::::E           T:::::T          E:::::::::::::::E     R:::::::::::::RR
#   I::::I  N::::::N  N::::N:::::::N        T:::::T          E:::::::::::::::E     R::::RRRRRR:::::R   P::::PPPPPPPPP      R::::RRRRRR:::::R   E:::::::::::::::E           T:::::T          E:::::::::::::::E     R::::RRRRRR:::::R
#   I::::I  N::::::N   N:::::::::::N        T:::::T          E::::::EEEEEEEEEE     R::::R     R:::::R  P::::P              R::::R     R:::::R  E::::::EEEEEEEEEE           T:::::T          E::::::EEEEEEEEEE     R::::R     R:::::R
#   I::::I  N::::::N    N::::::::::N        T:::::T          E:::::E               R::::R     R:::::R  P::::P              R::::R     R:::::R  E:::::E                     T:::::T          E:::::E               R::::R     R:::::R
#   I::::I  N::::::N     N:::::::::N        T:::::T          E:::::E       EEEEEE  R::::R     R:::::R  P::::P              R::::R     R:::::R  E:::::E       EEEEEE        T:::::T          E:::::E       EEEEEE  R::::R     R:::::R
# II::::::IIN::::::N      N::::::::N      TT:::::::TT      EE::::::EEEEEEEE:::::ERR:::::R     R:::::RPP::::::PP          RR:::::R     R:::::REE::::::EEEEEEEE:::::E      TT:::::::TT      EE::::::EEEEEEEE:::::ERR:::::R     R:::::R
# I::::::::IN::::::N       N:::::::N      T:::::::::T      E::::::::::::::::::::ER::::::R     R:::::RP::::::::P          R::::::R     R:::::RE::::::::::::::::::::E      T:::::::::T      E::::::::::::::::::::ER::::::R     R:::::R
# I::::::::IN::::::N        N::::::N      T:::::::::T      E::::::::::::::::::::ER::::::R     R:::::RP::::::::P          R::::::R     R:::::RE::::::::::::::::::::E      T:::::::::T      E::::::::::::::::::::ER::::::R     R:::::R
# IIIIIIIIIINNNNNNNN         NNNNNNN      TTTTTTTTTTT      EEEEEEEEEEEEEEEEEEEEEERRRRRRRR     RRRRRRRPPPPPPPPPP          RRRRRRRR     RRRRRRREEEEEEEEEEEEEEEEEEEEEE      TTTTTTTTTTT      EEEEEEEEEEEEEEEEEEEEEERRRRRRRR     RRRRRRR


class Interpreter:
    def __init__(self):
        self.global_env = {}

    def visit_Num(self, node):
        return node.value

    def visit_Bool(self, node):
        return node.value

    def visit_BinOp(self, node, local_env):
        left_val = 0
        right_val = 0

        left_val = self.visit(node.left, local_env)
        right_val = self.visit(node.right, local_env)

        if (
            node.op == "+"
            and not isinstance(left_val, bool)
            and not isinstance(right_val, bool)
        ):
            return left_val + right_val
        elif (
            node.op == "-"
            and not isinstance(left_val, bool)
            and not isinstance(right_val, bool)
        ):
            return left_val - right_val
        elif (
            node.op == "*"
            and not isinstance(left_val, bool)
            and not isinstance(right_val, bool)
        ):
            return left_val * right_val
        elif (
            node.op == "/"
            and not isinstance(left_val, bool)
            and not isinstance(right_val, bool)
        ):
            if right_val == 0:
                raise RuntimeError("Division by zero")
            return left_val // right_val
        elif (
            node.op == "%"
            and not isinstance(left_val, bool)
            and not isinstance(right_val, bool)
        ):
            if right_val == 0:
                raise RuntimeError("Modulo by zero")
            return left_val % right_val
        elif node.op == "&&":
            if isinstance(left_val, bool) and isinstance(right_val, bool):
                return left_val and right_val
            else:
                raise TypeError("one of the Operands is not bool")
        elif node.op == "||":
            if isinstance(left_val, bool) and isinstance(right_val, bool):
                return left_val or right_val
            else:
                raise TypeError("one of the Operands is not bool")
        elif node.op == "==":
            return left_val == right_val
        elif node.op == "!=":
            return left_val != right_val
        elif node.op == ">":
            return left_val > right_val
        elif node.op == "<":
            return left_val < right_val
        elif node.op == ">=":
            return left_val >= right_val
        elif node.op == "<=":
            return left_val <= right_val
        else:
            raise TypeError("Type error")

    def visit_UnaryOp(self, node):
        expr_val = self.visit(node.expr, "")

        if node.op == "!" and isinstance(expr_val, bool):
            return not expr_val
        else:
            raise TypeError("Type error")

    def visit_FuncDef(self, node):
        self.global_env[node.name] = (node.params, node.body)
        return "defined successfully"

    def visit_LambdaExpr(self, node, local_env):
        return self.visit(node.body, local_env)

    def visit_FuncCall(self, node, local_env2):
        if node.name in self.global_env:
            params, body = self.global_env[node.name]

            if not isinstance(node.args, BinOp):
                if len(node.args) != len(params) and not isinstance(
                    node.args[0], FuncOp
                ):
                    raise RuntimeError(
                        f"Function {node.name} expects {len(params)} arguments, got {len(node.args)}"
                    )

                if isinstance(node.args[0], FuncOp):
                    local_env = {
                        params[0]: self.visit(node.args[0].left, local_env2),
                        params[1]: self.visit(node.args[0].right, local_env2),
                    }
                else:
                    local_env = {
                        params[i]: self.visit(node.args[i], local_env2)
                        for i in range(len(params))
                    }

            # continue from here in case of node.args is BinOp
            if isinstance(node.args, BinOp):
                local_env = {
                    params[i]: self.visit(node.args, local_env2)
                    for i in range(len(params))
                }

            return self._evaluate(body, local_env)
        else:
            raise RuntimeError(f"Function {node.name} is not defined")

    def visit_AdvancedFuncOp(self, node, local_env):
        if isinstance(node.left, BinOp):
            if isinstance(node.left.right, str):
                if node.left.right == list(local_env.values())[0]:
                    return list(local_env.values())[0]

            if isinstance(node.left.right, Num):
                if node.left.right.value == list(local_env.values())[0]:
                    return list(local_env.values())[0]

        if isinstance(node.right, FuncOp):
            print(self._evaluate(node.right.right, local_env))
            self._evaluate(node.right.left, local_env)

        return self._evaluate(node.right, local_env)

    def visit_str(self, node, local_env):
        return dict(local_env).get(node)

    def visit_FuncOp(self, node, local_env):
        return None
        
    def visit(self, node, local_env):
        method_name = "visit_" + type(node).__name__

        visitor = getattr(self, method_name, None)

        if visitor:
            if (
                method_name == "visit_BinOp"
                or method_name == "visit_FuncCall"
                or method_name == "visit_str"
                or method_name == "visit_LambdaExpr"
            ):
                return visitor(node, local_env)
            else:
                return visitor(node)
        else:
            raise RuntimeError(f"No visit_{type(node).__name__} method defined")

    def _evaluate(self, node, local_env):
        try:
            if isinstance(node, list):  # multiple statements
                result = []
                for statement in node:
                    result.append(self._evaluate(statement, local_env))
                return result
            elif isinstance(node, BinOp):
                return self.visit_BinOp(node, local_env)
            elif isinstance(node, UnaryOp):
                return self.visit_UnaryOp(node)
            elif isinstance(node, Num):
                return self.visit_Num(node)
            elif isinstance(node, Bool):
                return self.visit_Bool(node)
            elif isinstance(node, FuncDef):
                return self.visit_FuncDef(node)
            elif isinstance(node, LambdaExpr):
                return self.visit_LambdaExpr(node, local_env)
            elif isinstance(node, FuncCall):
                return self.visit_FuncCall(node, local_env)
            elif isinstance(node, advancedFuncOp):
                return self.visit_AdvancedFuncOp(node, local_env)
            elif isinstance(node, FuncOp):
                # return ""
                return self.visit_FuncOp(node, local_env)
        except TypeError as e:
            print(e)

    def interpret(self, statements):
        try:
            ans = self._evaluate(statements, {})
            if ans is None or ans == "":
                raise RuntimeError("Runtime Error")
            return ans
        except RuntimeError as e:
            print(e)


# MMMMMMMM               MMMMMMMM               AAA               IIIIIIIIIINNNNNNNN        NNNNNNNN
# M:::::::M             M:::::::M              A:::A              I::::::::IN:::::::N       N::::::N
# M::::::::M           M::::::::M             A:::::A             I::::::::IN::::::::N      N::::::N
# M:::::::::M         M:::::::::M            A:::::::A            II::::::IIN:::::::::N     N::::::N
# M::::::::::M       M::::::::::M           A:::::::::A             I::::I  N::::::::::N    N::::::N
# M:::::::::::M     M:::::::::::M          A:::::A:::::A            I::::I  N:::::::::::N   N::::::N
# M:::::::M::::M   M::::M:::::::M         A:::::A A:::::A           I::::I  N:::::::N::::N  N::::::N
# M::::::M M::::M M::::M M::::::M        A:::::A   A:::::A          I::::I  N::::::N N::::N N::::::N
# M::::::M  M::::M::::M  M::::::M       A:::::A     A:::::A         I::::I  N::::::N  N::::N:::::::N
# M::::::M   M:::::::M   M::::::M      A:::::AAAAAAAAA:::::A        I::::I  N::::::N   N:::::::::::N
# M::::::M    M:::::M    M::::::M     A:::::::::::::::::::::A       I::::I  N::::::N    N::::::::::N
# M::::::M     MMMMM     M::::::M    A:::::AAAAAAAAAAAAA:::::A      I::::I  N::::::N     N:::::::::N
# M::::::M               M::::::M   A:::::A             A:::::A   II::::::IIN::::::N      N::::::::N
# M::::::M               M::::::M  A:::::A               A:::::A  I::::::::IN::::::N       N:::::::N
# M::::::M               M::::::M A:::::A                 A:::::A I::::::::IN::::::N        N::::::N
# MMMMMMMM               MMMMMMMMAAAAAAA                   AAAAAAAIIIIIIIIIINNNNNNNN         NNNNNNN


def main():
    interpreter = Interpreter()
    print("would you like to initiate the interactive mode?")
    print("enter Y in order to activate it or enter N to access the options of:\n1) loading code from a lambda file\n2) activating the test suite")
    answer = input(">>> ")
    print()
    # Check if a .lambda file is provided as an argument
    if answer == "N":
        print("would you like to initiate the test suite?")
        print("enter Y in order to activate it or enter N to access the option of loading code from a lambda file")
        answer = input(">>> ")
        if answer == "Y":
            print("part 1: lambda statements: 4 statements to check")
            part1 = [
                "Defun (AddAplusAMulB,a,b)a + lambd (b,a) (b*a)",
                "AddAplusAMulB(4,2)",
                "Defun (AddAplusAMulBplusBMinusA,a,b)a + lambd (b,a) (b*a) + lambd (b,a) (b-a)",
                "AddAplusAMulBplusBMinusA(5,8)"
            ]

            print("part 2: functional programming statements: 30 statements to check")
            part2 = [
                "Defun (boolTrue,a)True",
                "boolTrue(0)&&True",
                "True&&boolTrue(0)",
                "Defun (Add,a,b)a+b",
                "Add(2,1)",
                "Add(2,1)-8",
                "8-Add(2,1)",
                "Add(Add(2,2),2)",
                "Add(2,Add(2,2))",
                "2-Add(Add(2,2),2)",
                "Add(Add(2,2),2) - 2",
                "2-Add(2,Add(2,2))",
                "Add(2,Add(2,2)) - 2",
                "Defun (Factorial, n)(n == 1) or (n * Factorial(n - 1))",
                "Factorial(4)",
                "-30/6*5-2",
                "Add(2,1)==3",
                "3==Add(2,1)",
                "Add(2,1)!=3",
                "3!=Add(2,1)",
                "(Add(2,1)==3)",
                "(3==Add(2,1))",
                "(Add(2,1)==3)||(Add(2,1)==3)",
                "(Add(2,1)==3)||(Add(2,1)==4)",
                "(Add(2,1)==4)||(Add(2,1)==4)",
                "(Add(2,1)==3)&&(Add(2,1)==3)",
                "(Add(2,1)==3)&&(Add(2,1)==4)",
                "(Add(2,1)==4)&&(Add(2,1)==4)",
                "not True",
                "not False"
            ]

            print("part 3: while loop statements: 2 statements to check")
            part3 = [
                "Defun (Add,a,b)a+b",
                "Defun (repeat,n)(n==0) or (repeat(n-1) , Add(1,1))",
                "repeat(5)"
            ]
            
            print("part 4: syntax errors statements: 10 statements to check")
            part4 = [
                "Add((2,2)",
                "jibrish",
                "repeat())",
                "repeat()",
                "repeat(5)0",
                "Deun (Add,a,b) a+b",
                "Defun (Add,a,b)",
                "Defun (Add,a,b+2)",
                "true",
                "false"
            ]
            
            print("part 5: type errors statements: 13 statements to check")
            part5 = [
                "not 1",
                "not -1",
                "Add(2,True)",
                "Add(True,2)",
                "1+True",
                "True+1",
                "1+False",
                "False+1",
                "Add(2,1)&&3",
                "3&&Add(2,1)",
                "Add(2,1)||3",
                "3||Add(2,1)"
            ]
            
            print("part 6: runtime errors statements: 7 statements to check")
            part6 = [
                "repeat(-1)",
                "Factorial(-1)",
                "2/0",
                "4%0"
            ]

            allParts = [part1 ,part2 ,part3 ,part4 ,part5, part6]

            allPartsOutPut = [
                "defined successfully",
                12,
                "defined successfully",
                48,
                
                "defined successfully",
                True,
                True,
                "defined successfully",
                3,
                -5,
                5,
                6,
                6,
                -4,
                4,
                -4,
                4,
                "defined successfully",
                24,
                -27,
                True,
                True,
                False,
                False,
                True,
                True,
                True,
                True,
                False,
                True,
                False,
                False,
                False,
                True,
                
                "defined successfully",
                "defined successfully"
            ]
            
            i = 1
            c = 0
            for part in allParts:
                print(f"\nthe results for the statements of part {i}:")
                i = i + 1
                for text in part:
                    try:
                        if text == "repeat(5)":
                            print("the following output should be five times 2")
                        lexer = Lexer(text)
                        parser = Parser(lexer, interpreter)
                        statements = parser.parse()
                        result = interpreter.interpret(statements)
                        if result[0] is not None:
                            for x in result:
                                if isinstance(x, bool):
                                    print(f"the statement is: {text}     test passed? -> {x is allPartsOutPut[c]}")
                                else:
                                    print(f"the statement is: {text}     test passed? -> {x == allPartsOutPut[c]}")
                                c = c + 1
                    except Exception as e:
                        if not isinstance(e, TypeError):
                            print(e)

        else:
            # Get the filename from the command line arguments
            print("enter path for the file with .lambda suffix")
            filename = input(">>> ")

            # Ensure the file has a .lambda suffix
            if not filename.endswith(".lambda"):
                print("Error: The file must have a .lambda suffix.")
                return

            # Read the file content
            try:
                with open(filename, "r") as file:
                    text = file.read()
            except FileNotFoundError:
                print(f"Error: The file '{filename}' was not found.")
                return
            try:
                # Process the content as a single input
                lexer = Lexer(text)
                parser = Parser(lexer, interpreter)
                statements = parser.parse()
                result = interpreter.interpret(statements)
                if result[0] is not None:
                    for x in result:
                        print(x)
            except Exception as e:
                if not isinstance(e, TypeError):
                    print(e)
    elif answer == "Y":
        while True:
            try:
                text = input(">>> ")
                lexer = Lexer(text)
                parser = Parser(lexer, interpreter)
                statements = parser.parse()
                result = interpreter.interpret(statements)
                if result[0] is not None:
                    for x in result:
                        print(x)
            except Exception as e:
                if isinstance(e, EOFError):
                    break
                if not isinstance(e, TypeError):
                    print(e)
    else:
        print("enter Y or N next time...")


# execute main
main()
