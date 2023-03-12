# Sudoku Solver

A sudoku solver written in OOP Python using a simple set of rules and some indeterminism to fill out a puzzle from a .csv-file. 
Puzzles should work with 4x4 but is as of now only tried with 9x9.

Inspiration came from reading [this](https://www.mn.uio.no/math/english/research/projects/focustat/the-focustat-blog%21/sudokustory.html) approach using Markov Chain to do a completely probabilistic solution that took two minutes in R on a laptop. 
This program completes puzzles I have never been able to solve in a manner of seconds (not on a laptop, of course).
However, there are uncaught cases with very complex puzzles that no not progress.
