
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
		self.truth = np.sum(range(1, self.N+1))
		# sequence of puzzle steps to enable reverting 
		# back to a previously stable state
		self.changes:"list[tuple[int,int,int]]" = []
		self.checkpoint = 0
		# candidate cache
		self.cand:"dict['tuple[int,int]':'list[int]']" = {}
		# indirect rules for infering extra invalidations on slots in puzzle
		self.excl:"dict['tuple[int,int]':'list[int]']" = {}

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
		self.clearCache()
		return self.setCheckpoint()
	
	def clearCache(self:"Board") -> None:
		""" Empty board caching. """
		self.cand:"dict['tuple[int,int]':'list[int]']" = {}
		self.excl:"dict['tuple[int,int]':'list[int]']" = {}

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
	
	def candidates(self:"Board") -> "dict['tuple[int,int]':'list[int]']":
		"""
		Return map of x,y to [n...] where x,y are indices into puzzle that can hold values n...
		"""
		C = {}
		for x,y in np.ndindex(self.N, self.N):
			# skip slots with candidates
			if self.puzzle[x,y] != 0:
				continue
			c = self._candidates(x,y)
			# no candidates for 0-slot means puzzle has become wrong
			# assert len(c) > 0
			C[x,y] = c
		self.cand = C
		if len(self.excl) == 0:
			self.excl = self.exclusions()
			if len(self.excl) != 0: # redo candidates with exclusions
				C = self.candidates()
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
		if n in self.row(x) or n in self.column(y) or n in self.box(x,y) or self.isExluded(n,x,y):
			return False
		return True

	def row(self:"Board", x:int) -> np.ndarray:
		""" Return row for coordinate x. """
		return self.puzzle[x,:]

	def column(self:"Board", y:int) -> np.ndarray:
		""" Return column for coordinate y. """
		return self.puzzle[:,y]

	def isExluded(self:"Board", n:int, x:int, y:int) -> bool:
		""" Return true if n cannot be in (x,y) due to indirect exclusion. """
		return (x,y) in self.excl.keys() and n in self.excl[x,y]

	def box(self:"Board", x:int, y:int) -> np.ndarray:
		""" Return box related to coordinates (x,y). """
		x, y = self.boxCoordinate(x,y)
		return self.puzzle[x:x+self.boxLen, y:y+self.boxLen]
	
	def boxRow(self, x:int) -> np.ndarray:
		""" Return boxes along row coordinate x. """
		x,_ = self.boxCoordinate(x,0)
		return self.puzzle[x:x+self.boxLen,:]
	
	def boxColumn(self, y:int) -> np.ndarray:
		""" Return boxes along column coordinate y. """
		_,y = self.boxCoordinate(0,y)
		return self.puzzle[:,y:y+self.boxLen]
	
	def withoutBox(self, boxes:np.ndarray, x:int=-1, y:int=-1) -> np.ndarray:
		""" Return argument boxes excluding x or y box. """
		if x >= 0: # boxes are columnwise
			return np.vstack( (boxes[:x,:], boxes[x+self.boxLen:,:]) )
		if y >= 0:
			return np.hstack( (boxes[:,:y], boxes[y+self.boxLen:,:]) )
		# one must be negative (unspecified)
		assert x < 0 or y < 0
	
	def boxCoordinate(self:"Board", x:int, y:int) -> "tuple[int,int]":
		""" Return argument coordinates bounded to their respective puzzle box top-left coordinates. """
		x -= x % self.boxLen
		y -= y % self.boxLen
		return x, y

	def exclusions(self:"Board") -> "dict['tuple[int,int]':'list[int]']":
		"""
		Return map of x,y to [n...] where x,y are coordinates in puzzle that cannot hold values n...
		"""
		assert len(self.cand) > 0
		excl = {}
		for (x,y),cand in self.cand.items():
			for n in cand:
				if not self.exclude(x,y,n):
					continue
				if (x,y) not in excl.keys():
					excl[x,y] = [ n ]
				else:
					excl[x,y].append(n)
		return excl
	
	def exclude(self, x:int, y:int, n:int) -> bool:
		"""
		Return true if n is not able to be at x,y due to indirect reference.
		"""
		return self.excludeByRow(x,y,n) and self.excludeByColumn(x,y,n)

	def excludeByRow(self, x:int, y:int, n:int) -> bool:
		"""
		Return true if n is not able to be in box-row x because of indirect inference.
		"""
		boxes = self.boxRow(x)
		# list of row-indices where n appears
		nAppearsIn = -1
		for i,j in np.ndindex(boxes.shape):
			if y < j < y+self.boxLen:
				continue
			i += x
			if (i,j) in self.cand.keys() and n in self.cand[i,j]:
				if nAppearsIn < 0:
					nAppearsIn = i
				elif nAppearsIn != i:
					return False # no row-indirect if n can be in more than one row-index
		excluding = nAppearsIn == x
		return excluding
	
	def excludeByColumn(self, x:int, y:int, n:int) -> bool:
		"""
		Return true if n is not able to be in box-column y because of indirect inference.
		"""
		boxes = self.boxColumn(y)
		# list of column-indices where n appears
		nAppearsIn = -1
		for i,j in np.ndindex(boxes.shape):
			if i < x < i+self.boxLen:
				continue
			j += y
			if (i,j) in self.cand.keys() and n in self.cand[i,j]:
				if nAppearsIn < 0:
					nAppearsIn = j
				elif nAppearsIn != j:
					return False # no column-indirect if n can be in more than one column-index
		excluding = nAppearsIn == y
		return excluding
	
	def setSlot(self:"Board", x:int, y:int, n:int) -> bool:
		"""
		Set n as element in (x,y) position of puzzle and assert operation is valid. 
		Return true if operation was successful, false otherwise.
		"""
		if not self.validCandidate(x, y, n):
			return False
		self.changes.append( (x,y,n) )
		self.puzzle[x,y] = n
		self.clearCache()
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
