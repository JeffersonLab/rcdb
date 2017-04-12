__doc__ = """

Lexer for Python AST.

"""
from collections import namedtuple

import ply.lex
from ply.lex import TOKEN


rcdb_query_restricted = [
    'AS',
    'ASSERT',
    'BREAK',
    'CLASS',
    'CONTINUE',
    'DEF',
    'DEL',
    'ELIF',
    'ELSE',
    'EXCEPT',
    'EXEC',
    'FINALLY',
    'FOR',
    'FROM',
    'GLOBAL',
    'IF',
    'IMPORT',
    'IS',
    'LAMBDA',
    'PASS',
    'PRINT',
    'RAISE',
    'RETURN',
    'TRY',
    'WHILE',
    'WITH',
    'YIELD',

    'SEMICOLON']

reserved = {
    'and': 'AND',
    'as': 'AS',
    'assert': 'ASSERT',
    'break': 'BREAK',
    'class': 'CLASS',
    'continue': 'CONTINUE',
    'def': 'DEF',
    'del': 'DEL',
    'elif': 'ELIF',
    'else': 'ELSE',
    'except': 'EXCEPT',
    'exec': 'EXEC',
    'finally': 'FINALLY',
    'for': 'FOR',
    'from': 'FROM',
    'global': 'GLOBAL',
    'if': 'IF',
    'import': 'IMPORT',
    'in': 'IN',
    'is': 'IS',
    'lambda': 'LAMBDA',
    'not': 'NOT',
    'or': 'OR',
    'pass': 'PASS',
    'print': 'PRINT',
    'raise': 'RAISE',
    'return': 'RETURN',
    'try': 'TRY',
    'while': 'WHILE',
    'with': 'WITH',
    'yield': 'YIELD',
}


tokens = [
    'NEWLINE',
    'INDENT',
    'DEDENT',
    'ENDMARKER',
    'NAME',
    'STRINGLITERAL',
    'FLOATNUMBER',
    'BININTEGER',
    'HEXINTEGER',
    'OCTINTEGER',
    'DECIMALINTEGER',
    'AT',
    'DOT',
    'LPAREN',
    'RPAREN',
    'LSQ',
    'RSQ',
    'LCURL',
    'RCURL',
    'LANG',
    'RANG',
    'DEQ',
    'GEQ',
    'LEQ',
    'NEQ',
    'NEQ2',
    'COMMA',
    'SEMICOLON',
    'PIPE',
    'CARET',
    'AMPERSAND',
    'DBL_LANG',
    'DBL_RANG',
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH',
    'DBL_STAR',
    'DBL_SLASH',
    'MOD',
    'TILDE',
    'COLON',
    'BACKTICK',
    'EQ',
    'PLUS_EQ',
    'MINUS_EQ',
    'STAR_EQ',
    'SLASH_EQ',
    'MOD_EQ',
    'AMPERSAND_EQ',
    'PIPE_EQ',
    'CARET_EQ',
    'DBL_LANG_EQ',
    'DBL_RANG_EQ',
    'DBL_STAR_EQ',
    'DBL_SLASH_EQ',
]
tokens.extend(reserved.values())

t_AT = r'@'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQ = r'\['
t_RSQ = r'\]'
t_LCURL = r'{'
t_RCURL = r'}'
t_LANG = r'<'
t_RANG = r'>'
t_DEQ = r'=='
t_GEQ = r'>='
t_LEQ = r'<='
t_NEQ = r'!='
t_NEQ2 = r'<>'
t_COMMA = r','
t_SEMICOLON = r';'
t_PIPE = r'\|'
t_CARET = r'\^'
t_AMPERSAND = r'&'
t_DBL_LANG = r'<<'
t_DBL_RANG = r'>>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_SLASH = r'/'
t_DBL_STAR = r'\*\*'
t_DBL_SLASH = r'//'
t_MOD = r'%'
t_TILDE = r'~'
t_COLON = r':'
t_BACKTICK = r'`'
t_EQ = r'='
t_PLUS_EQ = r'\+='
t_MINUS_EQ = r'-='
t_STAR_EQ = r'\*='
t_SLASH_EQ = r'/='
t_MOD_EQ = r'%='
t_AMPERSAND_EQ = r'&='
t_PIPE_EQ = r'\|='
t_CARET_EQ = r'^='
t_DBL_LANG_EQ = r'<<='
t_DBL_RANG_EQ = r'>>='
t_DBL_STAR_EQ = r'\*\*='
t_DBL_SLASH_EQ = r'//='


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


#######################################
## Integer and long integer literals ##
#######################################

digit = r'[0-9]'
hexdigit = r'[0-9a-fA-F]'
bindigit = r'[0-1]'
octdigit = r'[0-7]'
nonzerodigit = r'[1-9]'
longoptional = r'[lL]?'

octinteger = (r'0[oO]' + octdigit + r'+' + longoptional + r'|' +
              r'0' + octdigit + r'+' + longoptional)
hexinteger = r'0[xX]' + hexdigit + r'+' + longoptional
bininteger = r'0[bB]' + bindigit + r'+' + longoptional
decimalinteger = (nonzerodigit + digit + r'*' + longoptional + r'|' +
                  r'0' + longoptional)


#############################
## Floating point literals ##
#############################

exponent = r'[eE][+-]?' + digit + r'+'
fraction = r'\.' + digit + r'+'
intpart = digit + r'+'
pointfloat = (r'(' + r'(' + intpart + r')?' + fraction + r')' + r'|' +
              r'(' + intpart + r'\.)')
exponentfloat = r'((' + intpart + r'|' + pointfloat + ')' + exponent + r')'
floatnumber = exponentfloat + '|' + pointfloat


#####################
## String literals ##
#####################
longstring = (r'(' +
              r'"""([^\\]|(\\[\x00-\x7f]))*"""' +
              r'|' +
              r"'''([^\\]|(\\[\x00-\x7f]))*'''" +
              r')')
shortstring = (r'(' +
               r'"([^\\\n\"]|(\\[\x00-\x7f]))*"' +
               r'|' +
               r"'([^\\\n\']|(\\[\x00-\x7f]))*'" +
               r')')
stringprefix = r'([rR]|([uUbB][rR]?))'
stringliteral = (r'(' + stringprefix + ')?' +
                 r'(' + longstring + '|' + shortstring + ')')


@TOKEN(stringliteral)
def t_STRINGLITERAL(t):
    return t


####################################
## Identifiers and reserved words ##
####################################


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t


# NOTE: These functions are defined to force an order in which
# we apply the greediest rules first

@TOKEN(floatnumber)
def t_FLOATNUMBER(t):
    return t


@TOKEN(bininteger)
def t_BININTEGER(t):
    return t


@TOKEN(hexinteger)
def t_HEXINTEGER(t):
    return t


@TOKEN(octinteger)
def t_OCTINTEGER(t):
    return t


@TOKEN(decimalinteger)
def t_DECIMALINTEGER(t):
    return t


################
## WHITESPACE ##
################


def t_NEWLINE(t):
    r'\n[ \t]*'

    t.lexer.lineno += 1

    # Count whitespace according to unix rules
    count = 0
    for char in t.value[1:]:
        if char == '\t':
            count += 8 - (count % 8)
        else:
            count += 1

    t.value = count
    return t


# NOTE: needs to be checked after newline and leading whitespace
def t_IGNORED_WHITESPACE(t):
    r'\s'
    return None


class _IndentParser(object):
    """A wrapper for the lexer to inject indentation tokens.

    These cannot be generated with the regular parser because we may need
    to generate multiple DEDENT tokens when parsing a newline.

    See also https://docs.python.org/2/reference/lexical_analysis.html#indentation
    and http://stackoverflow.com/questions/28259366/ply-return-multiple-tokens

    """
    IndentToken = namedtuple('Token', 'type value lineno lexpos')

    def __init__(self, lexer):
        self.lexer = lexer
        self._generator = None

    def input(self, text):
        return self.lexer.input(text)

    def token(self):
        if self._generator is None:
            self._generator = self._token_generator()
        try:
            return next(self._generator)
        except StopIteration:
            return None

    def _make_token(self, type):
        return self.IndentToken(
            type, None, self.lexer.lineno, self.lexer.lexpos)

    def _token_generator(self):
        """A generator that yields tokens until end of input"""
        stack = [0]

        while True:
            token = self.lexer.token()

            if token is None:
                # EOF
                while stack[-1]:
                    stack.pop()
                    yield self._make_token('DEDENT')
                yield self._make_token('ENDMARKER')
                return

            if token.type == "NEWLINE":
                yield token

                top = stack[-1]

                if token.value > top:
                    stack.append(token.value)
                    yield self._make_token('INDENT')

                elif token.value < top:
                    assert token.value in stack, "Inconsistent dedent"
                    while token.value != stack[-1]:
                        stack.pop()
                        yield self._make_token('DEDENT')
            else:
                yield token


def get_lexer():
    return _IndentParser(ply.lex.lex())


def tokenize(text):
    lexer = get_lexer()
    lexer.input(text)

    while True:
        token = lexer.token()
        if token is None:
            return
        yield token


if __name__ == '__main__':
    def print_all(text):
        lexer = get_lexer()
        lexer.input(text)

        while 1:
            tok = lexer.token()
            if tok is None:
                print (tok)
                break
            print (tok)

    while 1:
        try:
            text = raw_input('text > ')
        except EOFError:
            break
        print_all(text)