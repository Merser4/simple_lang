from enum import IntEnum


class TokenType(IntEnum):
    NAME = 1
    LITERAL = 2

    COMMA = 3
    COLON = 4
    RARROW = 5

    ASSIGN = 6
    EQUAL = 7
    PLUS = 8
    MINUS = 9
    STAR = 10
    DOUBLE_STAR = 11
    SLASH = 12

    GT = 13
    GTE = 14
    LT = 15
    LTE = 16

    LPAREN = 17
    RPAREN = 18
    LBRACE = 19
    RBRACE = 20

    CONST = 21
    AND = 22
    OR = 23
    IN = 24
    NOT = 25
    IF = 26
    ELIF = 27
    ELSE = 28
    BREAK = 29
    CONTINUE = 30
    WHILE = 31
    FOR = 32
    RETURN = 33
    FN = 34

    INT = 35
    FLOAT = 36
    STR = 37
    BOOL = 38

    TRUE = 39
    FALSE = 40

    ERROR = 41


class Token:

    def __init__(self, tp: TokenType, value: int | str | float | bool | None = None):
        self.tp = tp
        self.value = value

    def __str__(self):
        if self.value is None:
            return self.tp.name

        return f'{self.tp.name}:{self.value}'


class Lexer:

    def __init__(self, source: str):
        self._source = source
        self._cursor = 0
        self._max_cursor = len(source) - 1
        self._row = 1
        self._col = 1

    def get_token(self) -> Token | None:
        while True:
            char = self._extract()
            if char is None:
                return None

            if not char.isspace():
                break

        if char.isalpha():
            return self._name_or_keyword(first_char=char)
        elif char.isdigit():
            return self._number_literal(first_digit=char, is_negative=False)
        elif char == '"':
            return self._str_literal()
        elif char == ',':
            return Token(tp=TokenType.COMMA)
        elif char == ':':
            return Token(tp=TokenType.COLON)
        elif char == '-':
            next_char = self._peak()
            if next_char == '>':
                return Token(tp=TokenType.RARROW)
            elif next_char and next_char.isdigit():
                return self._number_literal(first_digit=self._extract(), is_negative=True)

            return Token(tp=TokenType.MINUS)
        elif char == '+':
            return Token(tp=TokenType.PLUS)
        elif char == '*':
            if self._peak() == '*':
                return Token(tp=TokenType.DOUBLE_STAR)

            return Token(tp=TokenType.STAR)
        elif char == '/':
            return Token(tp=TokenType.SLASH)
        elif char == '=':
            if self._peak() == '=':
                return Token(tp=TokenType.EQUAL)

            return Token(tp=TokenType.ASSIGN)
        elif char == '>':
            if self._peak() == '=':
                return Token(tp=TokenType.GTE)

            return Token(tp=TokenType.GT)
        elif char == '<':
            if self._peak() == '=':
                return Token(tp=TokenType.LTE)

            return Token(tp=TokenType.LT)
        elif char == '(':
            return Token(tp=TokenType.LPAREN)
        elif char == ')':
            return Token(tp=TokenType.RPAREN)
        elif char == '{':
            return Token(tp=TokenType.LBRACE)
        elif char == '}':
            return Token(tp=TokenType.RBRACE)

        return Token(tp=TokenType.ERROR, value=f'invalid char at::{self._row}:{self._col}')

    def _extract(self) -> str | None:
        if self._cursor > self._max_cursor:
            return None

        char = self._source[self._cursor]
        if char == '\n':
            self._row += 1
            self._col = 1
        else:
            self._col += 1

        self._cursor += 1
        return char

    def _peak(self) -> str | None:
        if self._cursor > self._max_cursor:
            return None

        return self._source[self._cursor]

    def _name_or_keyword(self, first_char: str) -> Token:
        chars = [first_char]
        while True:
            next_char = self._peak()
            if next_char and (next_char.isalpha() or next_char == '_'):
                chars.append(self._extract())
            else:
                break

        identifier = ''.join(chars)
        match identifier:
            case 'const': return Token(tp=TokenType.CONST)
            case 'and': return Token(tp=TokenType.AND)
            case 'or': return Token(tp=TokenType.OR)
            case 'in': return Token(tp=TokenType.IN)
            case 'not': return Token(tp=TokenType.NOT)
            case 'if': return Token(tp=TokenType.IF)
            case 'elif': return Token(tp=TokenType.ELIF)
            case 'else': return Token(tp=TokenType.ELSE)
            case 'break': return Token(tp=TokenType.BREAK)
            case 'continue': return Token(tp=TokenType.CONTINUE)
            case 'while': return Token(tp=TokenType.WHILE)
            case 'for': return Token(tp=TokenType.FOR)
            case 'return': return Token(tp=TokenType.RETURN)
            case 'fn': return Token(tp=TokenType.FN)
            case 'int': return Token(tp=TokenType.INT)
            case 'float': return Token(tp=TokenType.FLOAT)
            case 'str': return Token(tp=TokenType.STR)
            case 'bool': return Token(tp=TokenType.BOOL)
            case 'true': return Token(tp=TokenType.TRUE)
            case 'false': return Token(tp=TokenType.FALSE)
            case _: return Token(tp=TokenType.NAME, value=identifier)

    def _number_literal(self, first_digit: str, is_negative: bool) -> Token:
        digits = ['-', first_digit] if is_negative else [first_digit]
        dots_count = 0
        while True:
            next_char = self._peak()
            if next_char:
                if next_char.isdigit():
                    digits.append(self._extract())
                elif next_char == '.':
                    dots_count += 1
                    if dots_count == 2:
                        return Token(tp=TokenType.ERROR, value=f'invalid char at::{self._row}:{self._col}')

                    digits.append(self._extract())
                else:
                    break
            else:
                break

        if dots_count == 1:
            return Token(tp=TokenType.LITERAL, value=float(''.join(digits)))

        return Token(tp=TokenType.LITERAL, value=int(''.join(digits)))

    def _str_literal(self) -> Token:
        chars = []
        is_closed = False
        while True:
            next_char = self._extract()
            if next_char is None:
                break

            if next_char == '"':
                is_closed = True
                break

            chars.append(next_char)

        if is_closed:
            return Token(tp=TokenType.LITERAL, value=''.join(chars))

        return Token(tp=TokenType.ERROR, value=f'invalid char at::{self._row}:{self._col}')
