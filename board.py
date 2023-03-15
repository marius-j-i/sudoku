
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
		self.indirects:"dict['tuple[int,int]':'list[int]']" = {}

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
		self.indirects:"dict['tuple[int,int]':'list[int]']" = {}

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
		if len(self.cand) != 0:
			return self.cand
		C = {}
		for x,y in np.ndindex(self.N, self.N):
			# skip slots with candidates
			if self.puzzle[x,y] != 0:
				continue
			c = self._candidates(x,y)
			# no candidates for 0-slot means puzzle has become wrong
			assert len(c) > 0
			C[x,y] = c
		self.cand = C
		if len(self.indirects) != 0:
			self.indirects = self.findIndirects()
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

	def box(self:"Board", x:int, y:int) -> np.ndarray:
		""" Return box related to coordinates (x,y). """
		x, y = self.boxCoordinate(x,y)
		return self.puzzle[x:x+self.boxLen, y:y+self.boxLen]
	
	def boxCoordinate(self:"Board", x:int, y:int) -> "tuple[int,int]":
		""" Return argument coordinates bounded to their respective puzzle box top-left coordinates. """
		x -= x % self.boxLen
		y -= y % self.boxLen
		return x, y

	def isExluded(self:"Board", n:int, x:int, y:int) -> bool:
		""" Return true if n cannot be in (x,y) due to indirect exclusion. """
		for (i,j),excl in self.indirects.items():
			# find candidate exclusions for (x,y)
			if (i,j) != (x,y):
				continue
			elif n in excl:
				return True
		return False

	def FindExclusions(self:"Board") -> "dict['tuple[int,int]':'list[int]']":
		"""
		Return map of x,y to [n...] where x,y are coordinates in puzzle that cannot hold values n...
		"""
		assert len(self.cand) > 0
		excl = {}
		for (x,y),cand in self.cand.items():
			i,j = self.boxCoordinate(x, y)
			for n in cand:
				row = self.row(x)[:j][j+self.boxLen:]
		return excl

	def findIndirects(self:"Board") -> "dict['tuple[int,int]':'list[int]']":
		"""
		Return list of (x,y,[n...]) where (x,y) are coordinates in puzzle that cannot hold values n...
		"""
		assert len(self.cand) >= 0
		indirects = []
		return indirects
		for x,y,c in self.cand:
			c = self._findIndirects(x,y,c)
			indirects.append( (x,y,c) )
		self.indirects = indirects
		return indirects

	def _findIndirects(self:"Board", x:int, y:int, cand:"list[int]") -> "list[int]":
		"""
		Return exclusive list of candidates that cannot be at (x,y).
		"""
		excl = []

		i, j = self.boxCoordinate(x, y)
		for n in cand:
			self.horizontalExclusion(n, x,)
			if n in self.row(x)[:j][j+self.boxLen:]:
				pass

		boxes = self.mapCoordinatesToBox( (x,y) )
		# find horizontal and vertical set of coordinates 
		# in boxes of (i,j) where candidates align
		for v in boxes.values():
			box, coordinates = v
			for i in range(self.boxLen):
				# horizontal
				if 0 in box[i,:]:
					pass
				# vertical
				if 0 in box[:,i]:
					pass
		return excl
	
	def mapCoordinatesToBox(self:"Board", xy:"tuple[int,int]") -> "dict[np.ndarray,list[tuple[int,int]]]":
		""" Return dictionary mapping candidate coordinates to puzzle box, excluding (x,y). """
		boxes = {}
		for i,j,_ in self.cand:
			ij = self.boxCoordinate(i,j)
			# indirect exclusion comes from outside box of (x,y)
			if self.isSameBox(xy, ij):
				continue
			if ij not in boxes:
				boxes[ij] = self.box(*ij), [ (i,j) ]
			else:
				boxes[ij][1].append( (i,j) )
		return boxes

	def isSameBox(self:"Board", xy:"tuple[int,int]", ij:"tuple[int,int]") -> bool:
		""" Return true if arrgument coordinates belong to the same puzzle box. """
		xy, ij = self.boxCoordinate(*xy), self.boxCoordinate(*ij)
		return xy == ij

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
