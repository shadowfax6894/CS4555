#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from PythonASTExtension import *
from TraverseIR import *

class ArithmeticFlattener():

	@staticmethod
	def flattenArithmetic(ast,name,isInitial=True):
		if isinstance(ast,UnarySub):
			if not isPythonASTLeaf(ast.expr):
				flattenedExpression = [ArithmeticFlattener.flattenArithmetic(ast.expr,name,isInitial)]
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(Name(name))) 
			else:
				flattenedExpression = []
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(ast.expr))
			return Stmt(flattenedExpression + [assign])

		elif isinstance(ast,Add):
			#Flattens left sub tree
			#Checks to see if left subtree is a leaf
			if not isPythonASTLeaf(ast.left):
				#Recurses down the left subtree and returns a Stmt
				leftFlattenedExpression = ArithmeticFlattener.flattenArithmetic(ast.left,name,isInitial)
			else:
				#Checks to see if name has been assigned its initial value and responses accordingly
				if isInitial: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],ast.left)
				else: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.left)))

			#Assigning value for right name
			#Initially assigns rightName = name
			rightName = name
			#If both the right and left subtree are not leafs then append a value to avoid name clashing
			if not (isPythonASTLeaf(ast.left) or isPythonASTLeaf(ast.right)) or isinstance(ast.right,CallFunc):
				rightName = name+"$AddRight"

			#Final assignment for the tree
			assign = None
			#Checks if the tree is a leaf
			if not isPythonASTLeaf(ast.right):
				#Recurses down the right subtree and returns a Stmt
				rightFlattenedExpression = ArithmeticFlattener.flattenArithmetic(ast.right,rightName,False)
				#Adds the right and left subtrees and sets it equal to name
				assign = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),Name(rightName))))
			else:
				#Adds the right leaf with name
				rightFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.right)))

			#Creates a list for a Stmt node
			stmtArray = [leftFlattenedExpression,rightFlattenedExpression]
			#If assign was assigned add it to the stmtArray
			if assign: stmtArray += [assign]
			#Return Stmt
			return Stmt(stmtArray)
		elif isinstance(ast,CallFunc):
			stmtArray = []
			functionParameters = []
			parameterPrefixName = name + "$" + ast.node.name
			for i in range(len(ast.args)):
				parameter = ast.args[i]
				if not isPythonASTLeaf(parameter):
					parameterName = parameterPrefixName + "$" +str(i)
					functionParameters += [Name(parameterName)]
					stmtArray += [ArithmeticFlattener.flattenArithmetic(parameter,parameterName)]
				else: functionParameters += [parameter]
			assign = Assign([AssName(name,'OP_ASSIGN')],CallFunc(ast.node,functionParameters))
			return Stmt(stmtArray + [assign])

		elif isinstance(ast,List):
			stmtArray = []
			listParameters = []

			parameterPrefixName = name
			for i in range(len(ast.nodes)):
				parameter = ast.nodes[i]
				if not isPythonASTLeaf(parameter):
					parameterName = parameterPrefixName + "$" + str(i)
					listParameters += [Name(parameterName)]
					stmtArray += [ArithmeticFlattener.flattenArithmetic(parameter,parameterName)]
				else: listParameters += [parameter]

			assign = Assign([AssName(name,'OP_ASSIGN')],List(listParameters))
			return Stmt(stmtArray + [assign])

		elif isinstance(ast,Dict):
			stmtArray = []
			dictParameters = []

			parameterPrefixName = name
			valueParameterPrefixName = parameterPrefixName + "$value"
			keyParameterPrefixName = parameterPrefixName + "$key"
			for i in range(len(ast.items)):
				keyValuePair = ast.items[i]
				key = keyValuePair[0]
				value = keyValuePair[1]

				valueName = None
				keyName = None
				if not isPythonASTLeaf(value):
					valueParameterName = valueParameterPrefixName + "$" + str(i)
					valueName = Name(valueParameterName)
					stmtArray += [ArithmeticFlattener.flattenArithmetic(value,valueParameterName)]
				else: valueName = value

				if not isPythonASTLeaf(key):
					keyParameterName = keyParameterPrefixName + "$" + str(i)
					keyName = Name(keyParameterName)
					stmtArray += [ArithmeticFlattener.flattenArithmetic(key,keyParameterName)]
				else: keyName = key

				dictParameters += [(keyName,valueName)]

			dictionary = Dict(dictParameters)
			assign = Assign([AssName(name,'OP_ASSIGN')],dictionary)
			return Stmt(stmtArray + [assign])
		elif isinstance(ast,Subscript):
			stmtArray = []

			exprName = None
			subName = None
			if not isPythonASTLeaf(ast.expr):
				exprStringName = name + "$sub-expr"
				exprName = Name(exprStringName)
				stmtArray += [ArithmeticFlattener.flattenArithmetic(ast.expr,exprStringName)]
			else: exprName = ast.expr

			if not isPythonASTLeaf(ast.subs[0]):
				subStringName = name + "$sub-0"
				subName = Name(subStringName)
				stmtArray += [ArithmeticFlattener.flattenArithmetic(ast.subs[0],subStringName)]
			else: subName = ast.subs[0]

			subscription = Subscript(exprName,ast.flags,[subName])
			assign = Assign([AssName(name,'OP_ASSIGN')],subscription)
			return Stmt(stmtArray + [assign])
		elif isinstance(ast,IfExp):
			testExpr = None
			testName = None
			if not isPythonASTLeaf(ast.test):
				testExpr = ArithmeticFlattener.flattenArithmetic(ast.test,name+"$test")
				testName = Name(name+"$test")
			else:
				testExpr = ast.test

			thenExpr = None
			if not isPythonASTLeaf(ast.then):
				thenExpr = ArithmeticFlattener.flattenArithmetic(ast.then,name)
			else:
				thenExpr = Stmt([Assign([AssName(name,'OP_ASSIGN')],ast.then)])

			elseExpr = None
			if not isPythonASTLeaf(ast.else_):
				elseExpr = ArithmeticFlattener.flattenArithmetic(ast.else_,name)
			else:
				elseExpr = Stmt([Assign([AssName(name,'OP_ASSIGN')],ast.else_)])

			stmtArray = []

			ifexpr = None
			if testName: 
				ifexpr = IfExp(testName,thenExpr,elseExpr)
				stmtArray += [testExpr]

			else: ifexpr = IfExp(testExpr,thenExpr,elseExpr)
			stmtArray += [ifexpr]
			return Stmt(stmtArray)


		elif isinstance(ast,Compare):
			print "Compare"
			return ast
		elif isinstance(ast,Let):
			expr = ArithmeticFlattener.flattenArithmetic(ast.expr,ast.var.name)
			body = ArithmeticFlattener.flattenArithmetic(ast.body,name)
			return Stmt([Let(ast.var,expr,body)])

		else: return ast

class FlattenTracker():
	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name


class Flatten():
	def __init__(self):
		self.count = 0
		self.printTracker = FlattenTracker("print")

	def flattenMap(self,ast):
		if isinstance(ast,Assign):
			return ArithmeticFlattener.flattenArithmetic(ast.expr,ast.nodes[0].name)
		elif isinstance(ast,Printnl):
			name = self.printTracker.getNameAndIncrementCounter()
			if not isPythonASTLeaf(ast.nodes[0]):
				printStmt = ArithmeticFlattener.flattenArithmetic(ast.nodes[0],name)
				assign = Printnl([Name(name)],None)
				cluster = [printStmt,assign]
			else: cluster = [Printnl([ast.nodes[0]],None)]
			return Stmt(cluster)
		else: return ast