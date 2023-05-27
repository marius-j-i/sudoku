#!/usr/bin/env python3.10
"""
usage:
	--path  <str> : path to .csv-file puzzle
	--q-score     : boolean flag to plot Q-score
	--steps <int> : maximum number of steps for solver to try
"""

import argparse
from   matplotlib import pyplot as plt
import numpy as np
from   sys import argv
from   sudoku import Sudoku
from   time import time

def main(argv:list[str]) -> None:
	""" Consume sudoku class. """
	args = flags(argv)
	# sudoku instance
	puzzle = loadPuzzle(args.filename)
	sudoku = Sudoku(puzzle, args.score)
	t = time()
	board  = sudoku.solve(args.steps)
	t = time() - t
	if board.validate():
		print(f"solution is correct!")
	else:
		print(f"solution is incorrect!")
	print(f"solution took {t} sec.")
	print(board)
	if args.score:
		Q = sudoku.Qscores()
		plt.plot(Q, "-x")
		plt.xlabel("Steps")
		plt.ylabel("$\mathcal{Q}(x)$")
		plt.show()

def flags(argv:list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser()
	parser.add_argument("--filename", type = str, required = True, help = "path to .csv-file puzzle")
	parser.add_argument("--steps", type = int, default = 16384, help = "maximum number of steps for solver to try")
	parser.add_argument("--score", action = "store_true", default = False, help = "boolean flag to plot Q-score")
	args = parser.parse_args(argv)
	return args

def loadPuzzle(filename:str) -> np.ndarray:
	""" Return array of puzzle from .csv-file. """
	return np.genfromtxt(filename, dtype = np.int_, delimiter = ",", comments = "#")

if __name__ == "__main__":
	main(argv[1:])
