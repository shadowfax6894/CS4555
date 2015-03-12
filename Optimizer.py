from compiler.ast import *
from PythonASTExtension import *

INT_t = 0		#00
BOOL_t = 1		#01
BIG_t = 3		#11
MASK = 3		#11

class Optimizer:

	@staticmethod
	def constantFoldingMap(ast):
		if isinstance(ast,Add):
			if (isinstance(ast.left,Const) or isinstance(ast.left,Boolean)) and (isinstance(ast.right,Const) or isinstance(ast.right,Boolean)): 
				return Const(ast.left.value+ast.right.value)
			else: return ast
		elif isinstance(ast,UnarySub):
			if isinstance(ast.expr,Const) or isinstance(ast.expr,Boolean): return Const(-ast.expr.value)
			elif isinstance(ast.expr,UnarySub): return ast.expr.expr
			else: return ast
		elif isinstance(ast,And):
			if isinstance(ast.nodes[0],Const) or isinstance(ast.nodes[0],Boolean):
				return ast.nodes[1] if ast.nodes[0].value else ast.nodes[0]
			else: return ast
		elif isinstance(ast,Or):
			if isinstance(ast.nodes[0],Const) or isinstance(ast.nodes[0],Boolean):
				return ast.nodes[0] if ast.nodes[0].value else ast.nodes[1]
			else: return ast
		elif isinstance(ast,Not):
			if isinstance(ast.expr,Const) or isinstance(ast.expr,Boolean):
				return Boolean(not ast.expr.value)
			else: return ast
		elif isinstance(ast,Compare):
			if (isinstance(ast.expr,Const) or isinstance(ast.expr,Boolean)) and (isinstance(ast.ops[0][1],Const) or isinstance(ast.ops[0][1],Boolean)):
				return Boolean(ast.expr == ast.ops[0][1])
			else: return ast
		else: return ast

	@staticmethod
	def explicateFoldingMap(ast):
		if isinstance(ast,InjectFrom):
			if isinstance(ast.arg,Const): return Const(ast.arg.value * 4 + ast.typ.value)
			else: return ast
		elif isinstance(ast,ProjectTo):
			if isinstance(ast.arg,Const): return Const(int(ast.arg.value / 4))
			else: return ast
		elif isinstance(ast,Let):
			if isinstance(ast.body,Const): return ast.body
			else: return ast
		else: return ast

