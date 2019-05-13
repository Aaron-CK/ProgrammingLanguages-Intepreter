from sly import Parser
from sly import Lexer

# Program:
# 	Assignment*

# Assignment:
# 	Identifier = Exp;

# Exp: 
# 	Exp + Term | Exp - Term | Term

# Term:
# 	Term * Fact  | Fact

# Fact:
# 	( Exp ) | - Fact | + Fact | Literal | Identifier

class ToyLexer(Lexer):
    # Set of token names.   This is always required
    tokens = { IDENTIFIER, LITERAL, ADD, SUB, MUL, PARENL, PARENR, SEMICOLON, ASSIGN }

    ignore = ' \t\n\r\b'

    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    LITERAL  = r'0|([1-9][0-9]*)'
    ADD    = r'\+'
    SUB   = r'-'
    MUL   = r'\*'
    PARENL  = r'\('
    PARENR  = r'\)'
    SEMICOLON  = r';'
    ASSIGN  = r'='

class ToyParser(Parser):
    tokens = ToyLexer.tokens

    # Program:
    # 	Assignment*
    @_('assignments')
    def program(self, p):
        return p.assignments
    @_('assignment assignments')
    def assignments(self, p):
        return [p.assignment,*p.assignments]
    @_('')
    def assignments(self, p):
        return []
    @_('IDENTIFIER ASSIGN exp SEMICOLON')
    def assignment(self, p):
        return ('assign',p.IDENTIFIER,p.exp)


    # Exp: 
    # 	Exp + Term | Exp - Term | Term
    @_('exp ADD term')
    def exp(self, p):
        return ('add',p.exp,p.term)
    @_('exp SUB term')
    def exp(self, p):
        return ('sub',p.exp,p.term)
    @_('term')
    def exp(self, p):
        return p.term

    # Term:
    # 	Term * Fact  | Fact
    @_('term MUL fact')
    def term(self, p):
        return ('mul',p.term,p.fact)
    @_('fact')
    def term(self, p):
        return p.fact

    # Fact:
    # 	( Exp ) | - Fact | + Fact | Literal | Identifier
    @_('PARENL exp PARENR')
    def fact(self, p):
        return p.exp
    @_('SUB fact')
    def fact(self, p):
        return ('negate', p.fact)
    @_('ADD fact')
    def fact(self, p):
        return p.fact
    @_('LITERAL')
    def fact(self, p):
        return ('literal',int(p.LITERAL))
    @_('IDENTIFIER')
    def fact(self, p):
        return ('identifier',p.IDENTIFIER)

def evaluate(parsetree,scope):
  (treetype,*data) = parsetree
  if treetype == 'add':
    [lhs,rhs] = data
    return evaluate(lhs,scope) + evaluate(rhs,scope)
  elif treetype == 'sub':
    [lhs,rhs] = data
    return evaluate(lhs,scope) - evaluate(rhs,scope)
  elif treetype == 'mul':
    [lhs,rhs] = data
    return evaluate(lhs,scope) * evaluate(rhs,scope)
  elif treetype == 'negate':
    [subtree] = data
    return - evaluate(subtree,scope)
  elif treetype == 'literal':
    [literal] = data
    return literal
  elif treetype == 'identifier':
    [identifier] = data
    if identifier in scope:
      return scope[identifier]
    else:
      raise ValueError("uninitialized variable: " + identifier)
  else:
    raise ValueError("unknown parse tree node type " + treetype)

if __name__ == '__main__':
    data = """
      a = 1 + 2;
      asdad_a = a + 2;
    """
    lexer = ToyLexer()
    parser = ToyParser()
    scope = {}
    for (_,identifier,parsetree) in parser.parse(lexer.tokenize(data)):
      scope[identifier] = evaluate(parsetree,scope)
    for key, value in scope.items():
      print(key + " = " + str(value))