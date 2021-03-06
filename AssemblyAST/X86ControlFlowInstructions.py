from X86Instructions import *
from X86JumpInstructions import *
from X86GeneralInstructions import *
from X86Registers import *
from X86ArithmeticInstructions import *

class CompareInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		self.fromOperand = fromOperand
		self.toOperand = toOperand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("cmp",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class SectionHeaderInstruction(NoOperandInstruction):
	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return  x86InstructionToString(self.__class__.__name__,[self.name])

	def __str__(self):
		return  x86InstructionToString(self.__class__.__name__,[self.name])

	def printInstruction(self):
		return printNoOperandX86Instruction(self.name+":")

class AssemblySection(Instruction):
	def __init__(self,sectionHeader,clusteredInstruction):
		if not isinstance(sectionHeader,SectionHeaderInstruction):
			raise Exception("Unsupported node type. sectionHeader has to be of type SectionHeaderInstruction.")
		if not isinstance(clusteredInstruction,ClusteredInstruction):
			raise Exception("Unsupported node type. clusteredInstruction has to be of type ClusteredInstruction.")
		self.sectionHeader = sectionHeader
		self.clusteredInstruction = clusteredInstruction

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.clusteredInstruction])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.clusteredInstruction])

	def printInstruction(self):
		
		return self.sectionHeader.printInstruction() + self.clusteredInstruction.printInstruction()

class AssemblyFunction(AssemblySection):
	def __init__(self,sectionHeader,clusteredInstruction,activationRecordSize,returnOperand=None):
		print activationRecordSize
		if activationRecordSize < 0:
			raise Exception("activationRecordSize must be grater than or equal to 0.")
		AssemblySection(sectionHeader,clusteredInstruction)
		self.sectionHeader = sectionHeader
		self.clusteredInstruction = clusteredInstruction
		self.activationRecordSize = activationRecordSize
		self.returnOperand = returnOperand

		pushEbp = PushInstruction(RegisterOperand(Registers32.EBP))
		moveEspIntoEbp = MoveInstruction(RegisterOperand(Registers32.ESP),RegisterOperand(Registers32.EBP))
		createActivationStack = SubtractIntegerInstruction(ConstantOperand(DecimalValue(activationRecordSize)),RegisterOperand(Registers32.ESP))

		self.functionSetup = ClusteredInstruction([pushEbp,moveEspIntoEbp,createActivationStack])


		if returnOperand:returnValue = MoveInstruction(returnOperand,RegisterOperand(Registers32.EAX))
		else: returnValue = ClusteredInstruction()
		leave = LeaveInstruction()
		ret = ReturnInstruction()

		if returnOperand: self.functionCleanup = ClusteredInstruction([returnValue,leave,ret])
		else: self.functionCleanup = ClusteredInstruction()
		self.function = ClusteredInstruction([sectionHeader,self.functionSetup,clusteredInstruction,self.functionCleanup])

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.function])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.function])

	def printInstruction(self):
		return self.function.printInstruction()

class AssemblyIf(Instruction):
	def __init__(self,compare,name,trueSection,falseSection):
		if not isinstance(compare,CompareInstruction):
			raise Exception("compare must be of type CompareInstruction.")
		if not isinstance(name,str):
			raise Exception("name must be of type str.")
		if not isinstance(trueSection,ClusteredInstruction):
			raise Exception("trueSection must be of type ClusteredInstruction.")
		if not isinstance(falseSection,ClusteredInstruction):
			raise Exception("falseSection must be of type ClusteredInstruction.")

		self.compare = compare
		self.name = name
		self.trueSection = trueSection
		

		falseNameOperand = NameOperand(name+"False")
		endNameOperand = NameOperand(name+"End")
		falseJumpInstruction = JumpInstruction(falseNameOperand,JumpPredicateEnum.NOTZERO)
		endJumpInstruction = JumpInstruction(endNameOperand)
		endSection = SectionHeaderInstruction(endNameOperand.name)
		
		self.falseSection = AssemblySection(SectionHeaderInstruction(falseNameOperand.name),falseSection)

		clusteredArray = [self.compare,falseJumpInstruction,self.trueSection,endJumpInstruction,self.falseSection,endSection]

		self.ifInstruction = ClusteredInstruction(clusteredArray)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.ifInstruction])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.ifInstruction])

	def printInstruction(self):
		return self.ifInstruction.printInstruction()
