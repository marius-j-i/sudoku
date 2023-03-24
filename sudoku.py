
from   board import Board
import numpy as np
from   random import choice

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
			ok = self.step()
			# try: ok = self.step()
			# except AssertionError:
			# 	k = self.rollback()
			# 	print(f"rolling back from {k} ")
			# 	continue
			
			if ok is True:
				break
			if Q is not None:
				Q[self.steps] = self.board.Q()

			self.steps += 1

		if Q is not None:
			self.Q = Q[:self.steps+1]
		return self.board
	
	def checkpoint(self:"Sudoku") -> int:
		""" Record board checkpoint. """
		self.checkpoints.append(self.board.setCheckpoint())
		return self.checkpoints[-1]

	def rollback(self:"Sudoku") -> int:
		""" Revert to previous board checkpoint. """
		k = self.checkpoints.pop(-1)
		self.board.resetCheckpoint(k)
		return k

	def step(self:"Sudoku") -> bool:
		"""
		Do one puzzle step.
		Raise assertion on error.
		Return true if puzzle is done.
		"""
		# single solution slots first
		cand, updated = self.setObviousCandidates()
		if len(cand) == 0:
			return True # no candidates -> full board
		if not updated:
			self.setRandom(cand)
		# not done yet
		return False

	def setObviousCandidates(self:"Sudoku") -> "tuple[dict['tuple[int,int]':'list[int]'],bool]":
		"""
		Find and set candidates with only one possibility. 
		Return candidate set with no single slots and true.
		Return empty set and false on an illegal insertion.
		"""
		updated = False
		C = self.board.candidates()
		for (x,y), c in C.items():
			# skip non-deterministic suggestions
			if len(c) != 1:
				continue
			rc = self.board.setSlot(x, y, c[0])
			assert rc is True, f"failed::board.setSlot({x}, {y}, {c[0]})"
			# last slot might give board more deterministic insight
			updated = True
		# recurse to find potential new singular candidate slots
		if updated:
			C, updated = self.setObviousCandidates()
		return C, updated

	def setRandom(self:"Sudoku", cand:"dict['tuple[int,int]':'list[int]']"):
		"""
		Set a random puzzle coordinate and candidate. 
		Return false on error. 
		"""
		x,y = choice(list(cand.keys()))
		c = cand[x,y]
		assert len(c) != 0, f"candidates({x}, {y}) = {c}"
		n = choice(c)
		ok = self.board.setSlot(x, y, n)
		assert ok, f"failed::board.setSlot({x}, {y}, {n})"

	def Qscores(self:"Sudoku") -> np.ndarray:
		"""
		Return Q-scores from solving puzzle. 
		Return None if creation argument was False.
		"""
		return self.Q
