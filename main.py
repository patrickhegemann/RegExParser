import sys
from typing import List

"""
Grammar:

<regex>     ::= <term> '|' <term>
            |   <term>

<term>      ::= { <factor> }

<factor>    ::= <base> { '*' }
         
<base>      ::= <char>
            |   '.'
            |   '(' <regex> ')'
"""

# =============================================================================


class Node:
    pass


class Normal(Node):
    def __init__(self, char: str):
        self.char = char

    def __str__(self):
        return self.char


class Any(Node):
    def __init__(self):
        pass

    def __str__(self):
        return "."


class ZeroOrMore(Node):
    def __init__(self, exp: Node):
        self.exp = exp

    def __str__(self):
        return f"{str(self.exp)}*"


class Or(Node):
    def __init__(self, exp1: Node, exp2: Node):
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        return f"{str(self.exp1)}|{str(self.exp2)}"


class Str(Node):
    def __init__(self, exps: List[Node]):
        self.exps = exps

    def __str__(self):
        return f"({''.join([str(e) for e in self.exps])})"

    def add(self, exp: Node):
        self.exps.append(exp)

# =============================================================================


class Parser:
    def __init__(self, inp: str):
        self.inp = inp
        self.tokens = list(inp)
        self.failure = False

    def next_token(self) -> None:
        self.tokens = self.tokens[1:]

    def peek(self) -> str:
        return self.tokens[0]

    def accept(self, symbol: str) -> bool:
        if self.tokens and self.tokens[0] == symbol:
            self.next_token()
            return True
        return False

    def expect(self, symbol: str) -> bool:
        if self.accept(symbol):
            return True

        if self.tokens:
            self.error(f"Unexpected symbol: {self.peek()}")
        else:
            self.error("Unexpected end of file")

    def error(self, message: str) -> None:
        print(f"Parsing error on input '{self.inp}' : {message}", file=sys.stderr)
        self.failure = True

    def regex(self) -> Node:
        term: Node = self.term()

        if self.tokens and self.accept("|"):
            term2: Node = self.term()
            return Or(term, term2)
        else:
            return term

    def term(self) -> Node:
        factor = Str([])

        while self.tokens and not self.peek() == ')' and not self.peek() == '|':
            next_factor: Node = self.factor()
            factor.add(next_factor)

        if not factor.exps:
            self.error("Empty factor")

        if len(factor.exps) == 1:
            factor = factor.exps[0]

        return factor

    def factor(self) -> Node:
        base = self.base()

        if self.accept("*"):
            base = ZeroOrMore(base)

        return base

    def base(self) -> Node:
        if self.accept('('):
            regex: Node = self.regex()
            self.expect(')')
            return regex

        elif self.accept('.'):
            return Any()

        else:
            if self.accept('*'):
                self.error("Unexpected symbol: *")
                return Node()

            normal = Normal(self.peek())
            self.next_token()
            return normal

    def parse(self):
        r = self.regex()
        if self.tokens:
            self.error(f"Unexpected symbol: {self.peek()}")
        return r if not self.failure else None

# =============================================================================


def ast_str(node: Node) -> str:
    if isinstance(node, Normal):
        return f"Normal ('{node.char}')"
    elif isinstance(node, Any):
        return "Any ()"
    elif isinstance(node, ZeroOrMore):
        return f"ZeroOrMore ({ast_str(node.exp)})"
    elif isinstance(node, Or):
        return f"Or ({ast_str(node.exp1)}, {ast_str(node.exp2)})"
    elif isinstance(node, Str):
        return f"Str ([{', '.join([ast_str(e) for e in node.exps])}])"

# =============================================================================


def parse_reg_exp(inp: str) -> Node:
    parser = Parser(inp)
    ast = parser.parse()
    print("Input:", inp)
    print("AST:", ast_str(ast))
    print("RegEx:", ast)
    print("===")
    return ast if ast else ""

# =============================================================================


if __name__ == '__main__':
    parse_reg_exp("ab*")
    parse_reg_exp("(ab)*")
    parse_reg_exp("ab|a")
    parse_reg_exp("a(b|a)")
    parse_reg_exp("a|b*")
    parse_reg_exp("(a|b)*")
    parse_reg_exp("a|b")

    parse_reg_exp("a")
    parse_reg_exp("ab")
    parse_reg_exp("a.*")
    parse_reg_exp("(a.*)|(bb)")

    # Error cases
    parse_reg_exp("")
    parse_reg_exp(")(")
    parse_reg_exp("*")
    parse_reg_exp("a(")
    parse_reg_exp("()")
    parse_reg_exp("a**")
