Random maze generator, output as image

No dependency is required

Code for running:

from main import MazeGenerateor
maze = MazeGenerateor()
maze.generate(50)  # Input size here
maze.output()
maze.output(show_path=True)


![Random maze](https://github.com/mingsit/random-maze/blob/main/output/maze.png)

![Solution](https://github.com/mingsit/random-maze/blob/main/output/maze_solution.png)
