
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
	
	def solve(self:"Sudoku", maxSteps:int) -> Board:
		""" Return solved board sudoku puzzle board. """
		checkpoint = 0
		Q = np.zero( (maxSteps,) ) if self.Q else None
		for epoch in range(maxSteps):
			# checkpoint every now and then
			if epoch % self.board.N**2 == 0:
				checkpoint = self.board.setCheckpoint()
			# single solution slots first
			cand, ok = self.setObviousCandidates()
			# wrong steps can occur between checkpoints
			# since subsequent random selections lack global view of board
			if not ok:
				checkpoint = self.board.resetCheckpoint(checkpoint)
				continue
			elif len(cand) == 0:
				break # no candidates -> full board
			# just pick one
			x, y, n, ok = self.random(cand)
			if not ok:
				checkpoint = self.board.resetCheckpoint(checkpoint)
				continue
			ok = self.board.setSlot(x, y, n)
			if not ok:
				checkpoint = self.board.resetCheckpoint(checkpoint)
				continue
			if Q:
				Q[epoch] = self.board.Q()
		if Q:
			self.Q = Q[:epoch+1]
		return self.board
	
	def setObviousCandidates(self:"Sudoku") -> "tuple[list[tuple[int,int,list[int]]],bool]":
		"""
		Find and set candidates with only one possibility. 
		Return candidate set with no single slots and true.
		Return empty set and false on an illegal insertion.
		"""
		ok = True
		updated = False
		C = self.board.candidates()
		for x, y, c in C:
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

	def random(self:"Sudoku", cand:"list[tuple[int,int,list[int]]]") -> "tuple[int,int,int]":
		""" Return a random puzzle coordinate and candidate. """
		ok = True
		i = np.random.randint(0, len(cand))
		x, y, c = cand[i]
		if len(c) == 0:
			return 0, 0, 0, not ok
		i = np.random.randint(0, len(c))
		n = c[i]
		return x, y, n, ok

	def Qscores(self:"Sudoku") -> np.ndarray:
		"""
		Return Q-scores from solving puzzle. 
		Return None if creation argument was False.
		"""
		return self.Q
