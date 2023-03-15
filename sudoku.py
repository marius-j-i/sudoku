
from   board import Board
import numpy as np

class Sudoku:
	""" 
	Solver for a sudoku puzzle, inspired from: 
	https://www.mn.uio.no/math/english/research/projects/focustat/the-focustat-blog%21/sudokustory.html
	"""
	def __init__(self:"Sudoku", puzzle:np.ndarray, trackQscore:bool=False) -> None:
		self.board = Board(puzzle)
		self.Q = trackQscore
		self.checkpoints = []
		self.steps = 0
	
	def solve(self:"Sudoku", maxSteps:int) -> Board:
		""" Return solved board sudoku puzzle board. """
		Q = np.zero( (maxSteps,) ) if self.Q else None
		# for epoch in range(maxSteps):
		while self.steps < maxSteps:
			self.checkpoint()
			try: ok = self.step() 
			except AssertionError as e:
				print(f"rolling back: {e}")
				self.rollback()
				continue
			
			if ok is True:
				break
			if Q is not None:
				Q[self.steps] = self.board.Q()

			self.steps += 1

		if Q is not None:
			self.Q = Q[:self.steps+1]
		return self.board
	
	def checkpoint(self:"Sudoku") -> None:
		""" Record board checkpoint. """
		self.checkpoints.append(self.board.setCheckpoint())

	def step(self:"Sudoku") -> bool:
		"""
		Do one puzzle step.
		Raise assertion on error.
		Return true if puzzle is done.
		"""
		# single solution slots first
		cand, ok = self.setObviousCandidates()
		assert ok
		if len(cand) == 0:
			return True # no candidates -> full board
		# wrong steps can occur between checkpoints
		# since subsequent random selections lack global view of board
		ok = self.setRandom(cand)
		assert ok
		# not done yet
		return False

	def rollback(self:"Sudoku") -> None:
		""" Revert to previous board checkpoint. """
		k = self.checkpoints.pop(-1)
		self.board.resetCheckpoint(k)

	def setObviousCandidates(self:"Sudoku") -> "tuple[list[tuple[int,int,list[int]]],bool]":
		"""
		Find and set candidates with only one possibility. 
		Return candidate set with no single slots and true.
		Return empty set and false on an illegal insertion.
		"""
		ok = True
		updated = False
		C = self.board.candidates()
		for (x,y), c in C.items():
			# skip non-deterministic suggestions
			if len(c) != 1:
				continue
			rc = self.board.setSlot(x, y, c[0])
			if rc is False:
				return [], not ok
			# last slot might give board more deterministic insight
			updated = True
		# recurse to find potential new singular candidate slots
		if updated:
			C, ok = self.setObviousCandidates()
		return C, ok

	def setRandom(self:"Sudoku", cand:"list[tuple[int,int,list[int]]]") -> bool:
		"""
		Set a random puzzle coordinate and candidate. 
		Return false on error. 
		"""
		ok = True
		i = np.random.randint(0, len(cand))
		x, y, c = cand[i]
		if len(c) == 0:
			return 0, 0, 0, not ok
		i = np.random.randint(0, len(c))
		n = c[i]
		ok = self.board.setSlot(x, y, n)
		return ok

	def Qscores(self:"Sudoku") -> np.ndarray:
		"""
		Return Q-scores from solving puzzle. 
		Return None if creation argument was False.
		"""
		return self.Q
