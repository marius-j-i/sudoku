
import numpy as np

class Board:
		
	def __init__(self:"Board", puzzle:np.ndarray) -> None:
		assert len(puzzle.shape) == 2 and puzzle.shape[0] == puzzle.shape[1]

		# number of boxes, also row + column dimensions in puzzle
		self.N = puzzle.shape[0]
		# number of rows and columns inside each puzzle box
		self.boxLen = int(np.sqrt(self.N))
		
		# never seen lower that 4x4 puzzle, so...
		assert self.N >= 4
		assert self.boxLen > 1
		
		self.original   = puzzle.copy()
		self.puzzle     = puzzle
		# a correct puzzle should have numbers in each 
		# row, column, and box should sum up to this number
		self.truth      = np.sum(range(1, self.N+1))
		# sequence of puzzle steps to enable reverting 
		# back to a previously stable state
		self.changes    = []
		self.changes:"list[tuple[int,int,list[int]]]"
		self.checkpoint = 0

	def setCheckpoint(self:"Board") -> int:
		"""
		Store state of puzzle. 
		Return checkpoint indicator. 
		"""
		self.checkpoint = len(self.changes)
		return self.checkpoint
	
	def resetCheckpoint(self:"Board", k:int) -> None:
		"""
		Revert state of puzzle back to checkpoint k. 
		Return new checkpoint indicator.
		"""
		revert = self.changes[k:]
		self.changes = self.changes[:k]
		for x, y, _ in revert:
			self.puzzle[x,y] = 0
		return self.setCheckpoint()

	def validate(self:"Board") -> bool:
		""" 
		Return true if rows, columns and N'x N' boxes 
		in NxN puzzle, where N'< N, are valid solutions. 
		"""
		# assert per row
		rowDiscrepancies:np.bool_ = self.puzzle.sum(axis = 0) - self.truth != 0
		if rowDiscrepancies.any():
			return False
		# assert per column
		colDiscrepancies:np.bool_ = self.puzzle.sum(axis = 1) - self.truth != 0
		if colDiscrepancies.any():
			return False
		# assert per box
		for x in range(0, self.boxLen, self.boxLen):
			for y in range(0, self.boxLen, self.boxLen):
				boxDiscrepancies:np.bool_ = self.box(x,y).sum() - self.truth != 0
				if boxDiscrepancies.any():
					return False
		# box assertion might be overkill,
		# but now atleast sure it is correct
		return True
	
	def candidates(self:"Board")-> "list[tuple[int,int,list[int]]]":
		"""
		Return list of (x,y,[n...]) where x,y are indices into puzzle that can hold values n...
		"""
		C = []
		for x in range(self.N):
			for y in range(self.N):
				# skip slots with candidates
				if self.puzzle[x,y] != 0:
					continue
				c = self._candidates(x,y)
				C.append( (x,y,c) )
		return C
	
	def _candidates(self:"Board", x:int, y:int) -> "list[int]":
		""" Return candidates for (x,y) in puzzle. """
		c = []
		for n in range(1, self.N+1):
			if not self.validCandidate(x, y, n):
				continue
			c.append(n)
		return c

	def validCandidate(self:"Board", x:int, y:int, n:int) -> bool:
		""" Return true if n is a sufficient candidate to put into (x,y). """
		if n in self.row(x) or n in self.column(y) or n in self.box(x,y):
			return False
		return True

	def row(self:"Board", x:int) -> np.ndarray:
		""" Return row for coordinate x. """
		return self.puzzle[x,:]

	def column(self:"Board", y:int) -> np.ndarray:
		""" Return column for coordinate y. """
		return self.puzzle[:,y]

	def box(self:"Board", x:int, y:int) -> np.ndarray:
		""" Return box related to coordinates (x,y). """
		x -= x % self.boxLen
		y -= y % self.boxLen
		return self.puzzle[x:x+self.boxLen, y:y+self.boxLen]

	def setSlot(self:"Board", x:int, y:int, n:int) -> bool:
		"""
		Set n as element in (x,y) position of puzzle and assert operation is valid. 
		Return true if operation was successful, false otherwise.
		"""
		if not self.validCandidate(x, y, n):
			return False
		self.changes.append( (x,y,n) )
		self.puzzle[x,y] = n
		return True

	def Q(self:"Board") -> float:
		"""
		Return Q-score for board as is now. 
		This is not a ground truth but an estimate of how 
		far off from an optimum solution current board is. 
		"""
		return self.puzzle.sum() - self.truth*self.N

	def __str__(self) -> str:
		return str(self.puzzle)
