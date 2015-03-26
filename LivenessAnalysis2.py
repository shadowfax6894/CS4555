from PythonASTExtension import *

class LivenessAnalysis2:
	
	def __init__(self,ignore):
		self.ignore = ignore

	def livenessFolding(self,ast,acc):
		if isinstance(ast,AssName):
			ast.liveness = acc
			return acc - set([ast.name])
		elif isinstance(ast,Name):
			ast.liveness = acc
			if ast.name not in self.ignore: return acc | set([ast.name])
			else: return acc
		elif isinstance(ast,Function) or isinstance(ast,Lambda):
			if len(acc) > 0: raise Exception("Functions must not have any live variables outside of the function definition.")
			ast.liveness = acc
			return acc
		else:
			ast.liveness = acc
			return acc