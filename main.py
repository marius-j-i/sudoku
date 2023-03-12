
from   matplotlib import pyplot as plt
import numpy as np
import os
from   sys import argv
from   sudoku import Sudoku
from   time import time

def main(argv:"list[str]") -> None:
	""" Consume sudoku class. """
	if len(argv) < 2:
		usage = f"python {os.path.basename(__file__)} <puzzle-path> "
		exit(usage)
	# arguments
	filename = argv[1]
	Qscore = "--Q-score" in argv
	maxSteps = 16384
	if "--steps" in argv:
		maxSteps = nextarg("--steps", argv, int)
	# sudoku instance
	puzzle = loadPuzzle(filename)
	sudoku = Sudoku(puzzle)
	t = time()
	board  = sudoku.solve(maxSteps)
	t = time() - t
	# output
	if not board.validate():
		print(f"solution is incorrect!")
	else:
		print(f"solution is correct!")
	print(f"puzzle took {t} sec.")
	print(board)
	if Qscore:
		Q = sudoku.Qscores()
		plt.plot(Q, "-x")
		plt.xlabel("Steps")
		plt.ylabel("$\mathcal{Q}(x)$")
		plt.show()

def loadPuzzle(filename:str) -> np.ndarray:
	""" Return array of puzzle from .csv-file. """
	return np.genfromtxt(filename, dtype = np.int_, delimiter = ",", comments = "#")

def nextarg(arg:str, argv:list, callback:callable=None) -> str:
	"""Return argument after arg in argv with a dtype of callback if given."""
	if arg not in argv:
		if callback is not None:
			errmsg = f"{arg} flag requires positional argument {callback.__name__}"
			exit(errmsg)
		return None

	i = argv.index(arg) + 1

	if len(argv) == i or argv[i].startswith("--"):
		if callback is None:
			return None
		errmsg = f"{arg} flag requires positional argument {callback.__name__}"
		exit(errmsg)
	
	arg = argv[i]
	if callback is None:
		callback = str

	return callback(arg)

if __name__ == "__main__":
	main(argv)
