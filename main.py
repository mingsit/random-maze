from PIL import Image
import random
from copy import deepcopy
import os

Pixel = 20  # pixel for each cell
Choices = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

class MazeGenerateor():
    ''' Usage
    1. call MazeGenerateor()
    2. use .generate(size) function to generate the maze
    3. use .output() to output the maze as image
    4. (Optional) use .show_path() to output the path
    '''

    def __init__(self, path_length=3, fake_path_complexity=0.3):
        self.path_length = path_length  # lenght of the correct path, ratio to size : 2 to 5
        self.fake_path_complexity = fake_path_complexity
        # 0.2 to 0.3, higher value means more fake paths, but with higher chance the maze can't be generated
        image_list = ['black.png', 'white.png', 'green.png']
        corner_image_list = ['top-left.png', 'bottom-left.png', 'bottom-right.png', 'top-right.png']
        # 0 is black (wall), 1 is white (route)
        self.images = [Image.open(os.path.join('asset', i)) for i in image_list]
        self.corner_images = [Image.open(os.path.join('asset', i)).convert('RGBA') for i in corner_image_list]

    @staticmethod
    def is_contradict(delta, target):
        return delta[0] + target[0] == 0 and delta[1] + target[1] == 0

    @staticmethod
    def has_overlap(path, target):
        for cells in path[:-1]:
            if (cells[0] + 1 == target[0] or cells[0] - 1 == target[0]) and (cells[1] == target[1]):
                return True
            elif (cells[1] + 1 == target[1] or cells[1] - 1 == target[1]) and (cells[0] == target[0]):
                return True
        return False
    
    def check_goal(self, target):
        for i in range(2):
            if target[i] == 0 or target[i] == self.size - 1:
                return True
        return False

    def create_path(self):
        # Randomly generate a valid path from start to finish       
        
        path = []  # (x, y)
        mode = random.choice(['top', 'left'])
        start_pos = random.randint(1, self.size)  # Don't start at the corner
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
                delta = random.choice(all_choices)
                all_choices.remove(delta)
                if MazeGenerateor.is_contradict(delta, last_move):
                    # contradict with last delta
                    continue
                current_cell = path[-1]
                target_cell = (current_cell[0] + delta[0], current_cell[1] + delta[1])
                goal = self.check_goal(target_cell)
                if goal and step < self.size * self.path_length:
                    # Too short for a path
                    goal = False
                    continue
                can_move = not MazeGenerateor.has_overlap(path, target_cell)
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
        self.path = deepcopy(path)
        return True

    def generate_fake_path(self):
        # Randomly generate fake paths splitting from the correct path

        found_fake_start = False
        fake_path = []
        # Pick a random start point for fake path
        while not found_fake_start:
            random_pick = (random.randint(1, self.size), random.randint(1, self.size))
            if not MazeGenerateor.has_overlap(self.path, random_pick) and not MazeGenerateor.has_overlap(self.fake_path, random_pick):
                found_fake_start = True
                fake_path.append(random_pick)
        # Generate random route from fake start to a path (either valid or fake)
        connected_to_any_path = False
        last_move = (0, 0)
        while not connected_to_any_path:
            can_connect = False
            all_choices = deepcopy(Choices)
            while not can_connect:
                if not all_choices:
                    # Cannot generate fake path for this random set
                    return
                delta = random.choice(all_choices)
                all_choices.remove(delta)
                if MazeGenerateor.is_contradict(delta, last_move):
                    # contradict with last delta
                    continue
                current_cell = fake_path[-1]
                target_cell = (current_cell[0] + delta[0], current_cell[1] + delta[1])
                if self.check_goal(target_cell):
                    # fake path cannot break the maze
                    continue
                can_connect = not MazeGenerateor.has_overlap(fake_path, target_cell)
                if can_connect:
                    # Update value for another loop
                    last_move = delta
                    fake_path.append(target_cell)
                # Check whether target_cell is connected to whatever path
                connected_to_any_path  = MazeGenerateor.has_overlap(self.path, target_cell) or MazeGenerateor.has_overlap(self.fake_path, target_cell)

        for cells in fake_path:
            self.matrix[cells[1]][cells[0]] = 1
        self.fake_path += deepcopy(fake_path)
    
    def generate(self, size):
        # Run self.generate(size) to generate a maze

        self.path = []  # Valid path from start to finish
        self.fake_path = []  # Fake paths
        self.matrix = [[0 for x in range(size)] for x in range(size)]
        self.size = size
        generated_path = False
        while not generated_path:
            generated_path = self.create_path()
        route_percent = sum(sum(self.matrix, [])) / self.size ** 2
        # Generate fake paths until a portion of the maze is filled
        while route_percent < self.fake_path_complexity:
            self.generate_fake_path()
            route_percent = sum(sum(self.matrix, [])) / self.size ** 2

    def output(self, show_path=False):
        ''' Visualize the maze and save as png 
        show_path: False means don't indicate the correct path, True means indicating the correct path'''

        matrix = deepcopy(self.matrix)
        if not show_path:
            start = self.path[0]
            finish = self.path[-1]
            matrix[start[1]][start[0]] = 2
            matrix[finish[1]][finish[0]] = 2
        else:
            for solution in self.path:
                matrix[solution[1]][solution[0]] = 2

        # Create a new image, 
        new_im = Image.new('RGBA', (Pixel*self.size, Pixel*self.size))
        # Paste image by looping each cell
        y_offset = 0
        for r, row in enumerate(matrix):
            x_offset = 0
            for c, cell in enumerate(row):
                new_im.paste(self.images[cell], (y_offset, x_offset))  # Paste the block of the maze
                # Cover corner to make it looks better
                if cell > 0:
                    if r > 0 and r < self.size-1 and c > 0 and c < self.size-1:
                        # Check top left
                        if matrix[r-1][c-1] > 0:
                            if matrix[r][c-1] == 0 and matrix[r-1][c] == 0:
                                new_im.paste(self.corner_images[0], (y_offset, x_offset), self.corner_images[0])
                        # Check bottom left
                        if matrix[r-1][c+1] > 0:
                            if matrix[r][c+1] == 0 and matrix[r-1][c] == 0:
                                new_im.paste(self.corner_images[1], (y_offset, x_offset), self.corner_images[1])
                        # Check bottom right
                        if matrix[r+1][c+1] > 0:
                            if matrix[r][c+1] == 0 and matrix[r+1][c] == 0:
                                new_im.paste(self.corner_images[2], (y_offset, x_offset), self.corner_images[2])
                        # Check top right
                        if matrix[r+1][c-1] > 0:
                            if matrix[r][c-1] == 0 and matrix[r+1][c] == 0:
                                new_im.paste(self.corner_images[3], (y_offset, x_offset), self.corner_images[3])
                x_offset += Pixel
            y_offset += Pixel

        filename = 'maze.png' if not show_path else 'maze_solution.png'
        new_im.save(os.path.join('output', filename))
