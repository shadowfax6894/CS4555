import compiler
from compiler.ast import *
import ply.lex as lex
import ply.yacc as yacc

debug = False

class Parser_hw2:

	lexer = None
	parser = None
	stmtList = None
	
	def __init__(self):
		reserved = {'print' : 'PRINT', 'input' : 'INPUT'}
		tokens = ['INT','PLUS','MINUS','EQUALS','NAME','RIGHT_PARENTH','LEFT_PARENTH'] + list(reserved.values())

		t_PLUS = r'\+'
		t_MINUS = r'-'
		t_EQUALS = r'='
		t_RIGHT_PARENTH = r'\)'
		t_LEFT_PARENTH = r'\('

		def t_NAME(t):
			r'[a-zA-Z_][a-zA-Z_0-9]*'
			t.type = reserved.get(t.value,'NAME') # Check for reserved words
			return t

		def t_INT(t):
			r'\d+'
			try:
				t.value = int(t.value)
			except ValueError:
				print "integer value too large", t.value
				t.value = 0

		t_ignore = ' \t'

		def t_newline(t):
			r'\n+'
			t.lexer.lineno += t.value.count("\n")

		def t_error(t):
			print "Illegal character '%s'" % t.value[0]
			t.lexer.skip(1)

		self.lexer = lex.lex()

		precedence = (
			('right','EQUALS'),
			('left','PLUS'),
			('right','MINUS'),
			('left','LEFT_PARENTH','RIGHT_PARENTH')
		)

		self.stmtList = Stmt([])

		def p_program_module(t):
			'program : module'
			t[0] = Module(None, t[1])

		def p_empty(t):
			'empty :'
			t[0] = Stmt([])

		def p_module_statement(t):
			'''module : statement
					  | empty'''
			t[0] = t[1]

		def p_statements_statement(t):
			'''statement : statement simple_statement
						 | simple_statement'''
			if( len(t) == 2 ):
				self.stmtList.nodes.append(t[1])
			elif( len(t) == 3):
				self.stmtList.nodes.append(t[2])
			t[0]=self.stmtList

		def p_print_statement(t):
			'statement : PRINT expression'
			t[0] = Printnl([t[2]],None)

		def p_expression_statement(t):
			'simple_statement : expression'
			t[0] = t[1]

		def p_assign_expression(t):
			'expression : expression EQUALS expression'
			t[0] = Assign([AssName(t[1],'OP_ASSIGN')],t[3])

		def p_plus_expression(t):
			'expression : expression PLUS expression'
			t[0] = Add((t[1],t[3]))

		def p_minus_expression(t):
			'expression : MINUS expression'
			t[0] = UnarySub(t[2])

		def p_int_expression(t):
			'expression : INT'
			t[0] = Const(t[1])

		def p_name_expression(t):
			'expression : NAME'
			t[0] = Name(t[1])

		def p_func_expression(t):
			'expression : INPUT LEFT_PARENTH RIGHT_PARENTH'
			t[0] = CallFunc(Name(t[1]),[],None,None)

		def p_l_paren_expression_r_paren(t):
			'expression : LEFT_PARENTH expression RIGHT_PARENTH'
			t[0] = t[2]

		def p_error(t):
			print "Syntax error at '%s'" % t.value

		self.parser = yacc.yacc(debug=0, write_tables=0)

		def testLexer(self, to_lex):
			self.lexer.input(to_lex)
			while True:
				tok = self.lexer.token()
				if not tok: break
				print tok

	def parseFile(self, path):
		file_to_parse = open(path, 'r')
		text_to_parse = file_to_parse.read()
		return self.parser.parse(text_to_parse)

	def parse(self, to_parse):
		return self.parser.parse(to_parse)