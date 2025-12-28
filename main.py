from PIL import Image
import random
from copy import deepcopy

Pixel = 20  # pixel for each cell
Choices = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class MazeGenerateor():
    ''' Usage
    1. call MazeGenerateor()
    2. use .generate(size) function to generate the maze
    3. use .output() to output the maze as image
    4. (Optional) use .show_path() to output the path
    '''

    def __init__(self):
        image_list = ['black.png', 'white.png']
        # 0 is black (wall), 1 is white (route)
        self.images = [Image.open(i) for i in image_list]

    def create_path(self):
        # Randomly generate a valid path from start to finish
        def is_contradict(delta, target):    
            return delta[0] + target[0] == 0 and delta[1] + target[1] == 0

        def has_overlap(path, target):
            for cells in path[:-1]:
                if (cells[0] + 1 == target[0] or cells[0] - 1 == target[0]) and (cells[1] == target[1]):
                    return True
                elif (cells[1] + 1 == target[1] or cells[1] - 1 == target[1]) and (cells[0] == target[0]):
                    return True
            return False

        def check_goal(target):
            for i in range(2):
                if target[i] == 0 or target[i] == self.size - 1:
                    return True
            return False

        path = []  # (x, y)
        mode = random.choice(['top', 'left'])
        start_pos = random.randint(1, self.size)  # Can't start at the corner
        if mode == 'top':
            path.append((start_pos, 0))
            path.append((start_pos, 1))
            last_move = (0, 1)  # down
        if mode == 'left':
            path.append((0, start_pos))
            path.append((1, start_pos))
            last_move = (1, 0)  # right

        step = 1
        goal = False
        while not goal:
            # Check whether path can go to target
            can_move = False
            all_choices = deepcopy(Choices)
            while not can_move:
                if not all_choices:
                    # No more move
                    break
                delta = random.choice(all_choices)  # left, right, up, down
                all_choices.remove(delta)
                if is_contradict(delta, last_move):
                    # contradict with last delta
                    continue
                current_cell = path[-1]
                target_cell = (current_cell[0] + delta[0], current_cell[1] + delta[1])
                goal = check_goal(target_cell)
                if goal and step < self.size * 3:
                    # Too short for a path
                    goal = False
                    continue
                can_move = not has_overlap(path, target_cell)
                if can_move:
                    # Update value for another loop
                    step += 1
                    last_move = delta
                    path.append(target_cell)
            if not all_choices:
                # Cannot generate path for this random set
                return False
        for cells in path:
            self.matrix[cells[1]][cells[0]] = 1
        return True

    def generate_fake_path(self):
        # TODO: Randomly generate fake paths splitting from the correct path
        pass
    
    def generate(self, size):
        self.path = []
        self.matrix = [[0 for x in range(size)] for x in range(size)]
        self.size = size
        generated_path = False
        while not generated_path:
            generated_path = self.create_path()
        self.generate_fake_path()

    def output(self):
        # Show the maze and save as png

        # Create a new image, 
        new_im = Image.new('RGB', (Pixel*self.size, Pixel*self.size))

        # Paste image by looping each cell
        y_offset = 0
        for row in self.matrix:
            x_offset = 0
            for cell in row:
                new_im.paste(self.images[cell], (x_offset,y_offset))
                x_offset += Pixel
            y_offset += Pixel

        new_im.save('maze.png')

    def show_path(self):
        # TODO: Show the path of the maze and save as png
        pass
    