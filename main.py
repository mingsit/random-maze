from PIL import Image
import random
from copy import deepcopy
import os

Cell_pixel = 30  # pixel per each cell
Choices = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

class MazeGenerateor():
    ''' Usage
    call MazeGenerateor().generate(horizontal_size, vertical_size) to generate the maze as image
    '''

    @staticmethod
    def is_undo(delta, target):
        return delta[0] + target[0] == 0 and delta[1] + target[1] == 0

    def check_goal(self, target):
        if target[0] <= -1 or target[0] >= self.size_x:
            return True
        if target[1] <= -1 or target[1] >= self.size_y:
            return True
        return False
    
    def change_walls(self, path):
        # Change value of horizontal / vertical walls by inputted path
        for step in range(len(path)-1):  # Don't loop last
            try:
                self.empty_cell.remove(path[step])  # can't remove first one
            except KeyError:
                pass
            horizontal_action = path[step + 1][0] - path[step][0]
            vertical_action = path[step + 1][1] - path[step][1]
            if horizontal_action == 1:  # right
                self.vertical_walls[path[step][1]][path[step][0]+1] = 1  # [which_column][which_row]
            elif horizontal_action == -1:  # left
                self.vertical_walls[path[step][1]][path[step][0]] = 1
            elif vertical_action == 1:  # down
                self.horizontal_walls[path[step][1]+1][path[step][0]] = 1
            elif vertical_action == -1:  # up
                self.horizontal_walls[path[step][1]][path[step][0]] = 1


    def create_path(self):
        # Randomly generate a valid path from start to finish
        # Return Boolean (True if successfully generated path, False if not)

        path = []  # (x, y)
        mode = random.choice(['top', 'left'])
        if mode == 'top':
            start_pos = random.randint(0, self.size_x)
            path.append((start_pos, -1))
            path.append((start_pos, 0))
            last_move = (0, 1)  # move down
        if mode == 'left':
            start_pos = random.randint(0, self.size_y)
            path.append((-1, start_pos))
            path.append((0, start_pos))
            last_move = (1, 0)  # move right

        step = 1
        goal = False
        while not goal:
            # Check whether path can go to target
            can_move = False
            all_choices = deepcopy(Choices)
            while not can_move:
                if not all_choices:
                    # Cannot generate path for this random set
                    return False
                delta = random.choice(all_choices)
                all_choices.remove(delta)
                if MazeGenerateor.is_undo(delta, last_move):
                    # ensure it doesn't undo the last move
                    continue
                current_cell = path[-1]
                target_cell = (current_cell[0] + delta[0], current_cell[1] + delta[1])
                if target_cell in path:
                    # Already walked into the cell before
                    continue
                goal = self.check_goal(target_cell)
                if goal:
                    if step < (self.size_x+self.size_y)/2 * self.path_length:
                        # Too short for a path
                        goal = False
                        continue
                    path.append(target_cell)
                    break
                # Update value for another loop
                step += 1
                last_move = delta
                path.append(target_cell)
                can_move = True
        
        # Change value of horizontal and vertical walls
        self.change_walls(path)
        self.path = deepcopy(path)
        return True

    def create_fake_path(self):
        # Randomly generate fake paths, end if it overlaps any current path.

        path = []  # (x, y)
        path.append(random.choice(list(self.empty_cell)))
        last_move = (0, 0)

        goal = False
        while not goal:
            # Check whether path can go to target
            can_move = False
            all_choices = deepcopy(Choices)
            while not can_move:
                if not all_choices:
                    # Cannot generate path for this random set
                    return False
                delta = random.choice(all_choices)
                all_choices.remove(delta)
                if MazeGenerateor.is_undo(delta, last_move):
                    # ensure it doesn't undo the last move
                    continue
                current_cell = path[-1]
                target_cell = (current_cell[0] + delta[0], current_cell[1] + delta[1])
                if target_cell in path:
                    # Already walked into the cell before
                    continue
                if self.check_goal(target_cell):
                    # Fake path cannot break outside
                    continue
                goal = target_cell not in self.empty_cell  # if it walks into a non-empty cell = connected to existing path
                if goal:
                    path.append(target_cell)
                    break
                # Update value for another loop
                last_move = delta
                path.append(target_cell)
                can_move = True
        
        # Change value of horizontal and vertical walls
        self.change_walls(path)
        self.fake_paths.append(deepcopy(path))
        return True
    
    def output(self, outside_thickness=5, name="maze"):
        ''' Visualize the maze and save as png '''
        
        new_im = Image.new('RGB', (self.size_x*Cell_pixel+outside_thickness*2, self.size_y*Cell_pixel+outside_thickness*2), (255, 255, 255))

        pixels = new_im.load() # create the pixel map

        width = new_im.size[0]
        height = new_im.size[1]

        # Make outside walls
        for x in range(outside_thickness):
            for y in range(height):
                pixels[x,y] = (0, 0 ,0)
        for x in range(width-outside_thickness, width):
            for y in range(height):
                pixels[x,y] = (0, 0 ,0)

        for x in range(width):
            for y in range(outside_thickness):
                pixels[x,y] = (0, 0 ,0)
        for x in range(width):
            for y in range(height-outside_thickness, height):
                pixels[x,y] = (0, 0 ,0)

        # Make inside walls
        for x in range(outside_thickness, width, Cell_pixel):
            for y in range(height):
                pixels[x-1,y] = (0, 0 ,0)
                pixels[x,y] = (0, 0 ,0)
                pixels[x+1,y] = (0, 0 ,0)
                
        for x in range(width):
            for y in range(outside_thickness, height, Cell_pixel):
                pixels[x,y-1] = (0, 0 ,0)
                pixels[x,y] = (0, 0 ,0)
                pixels[x,y+1] = (0, 0 ,0)

                
        # Remove walls if it's not a wall
        for y, row in enumerate(self.horizontal_walls):
            for x, wall in enumerate(row):
                if wall == 1:  # no wall
                    if y == 0:  # break top wall
                        for pixel_x in range(Cell_pixel-3):
                            for pixel_y in range(outside_thickness+2):
                                pixels[2+x*Cell_pixel + pixel_x + outside_thickness, pixel_y] = (255, 255, 255)
                    elif y == self.size_y:  # break bottom wall
                        for pixel_x in range(Cell_pixel-3):
                            for pixel_y in range(outside_thickness+2):
                                pixels[2+x*Cell_pixel + pixel_x + outside_thickness, height-pixel_y-1] = (255, 255, 255)
                    else:  # inside walls
                        for pixel_x in range(Cell_pixel-3):
                            for pixel_y in range(3):
                                pixels[2+x*Cell_pixel + pixel_x + outside_thickness, y*Cell_pixel + pixel_y + outside_thickness-1] = (255, 255, 255)

        for y, row in enumerate(self.vertical_walls):
            for x, wall in enumerate(row):
                if wall == 1:  # no wall
                    if x == 0:  # break left wall
                        for pixel_y in range(Cell_pixel-3):
                            for pixel_x in range(outside_thickness+2):
                                pixels[pixel_x, 2+y*Cell_pixel + pixel_y + outside_thickness] = (255, 255, 255)
                    elif x == self.size_x:  # break right wall
                        for pixel_y in range(Cell_pixel-3):
                            for pixel_x in range(outside_thickness+2):
                                pixels[width-pixel_x-1, 2+y*Cell_pixel + pixel_y + outside_thickness] = (255, 255, 255)
                    else:  # inside walls
                        for pixel_x in range(3):
                            for pixel_y in range(Cell_pixel-3):
                                pixels[x*Cell_pixel + pixel_x + outside_thickness-1, 2+y*Cell_pixel + pixel_y + outside_thickness] = (255, 255, 255)

        new_im.save(os.path.join('output', f'{name}.png'))

    def generate(self, size_x:int, size_y:int, path_length=4):
        # Run self.generate(size) to generate a maze
        # size_x: horizontal number of cells, size_y: vertical number of cells

        self.path_length = path_length  # lenght of the correct path, ratio to size : 2 to 5
        self.path = []  # Valid path from start to finish
        self.fake_paths = []  # list of list, stores fake path, no practical use just yet
        self.horizontal_walls = [[0 for x in range(size_x+1)] for y in range(size_y+1)]  # 0: wall, 1: through
        self.vertical_walls = [[0 for x in range(size_x+1)] for y in range(size_y+1)]  # 0: wall, 1: through
        self.empty_cell = set([(x, y) for x in range(size_x) for y in range(size_y)])
        # 0 is black (wall), 1 is white (route)
        self.size_x = size_x
        self.size_y = size_y
        success = self.create_path()
        while not success:
            success = self.create_path()
        self.output(name="maze_solution")

        while not self.empty_cell == set():
            self.create_fake_path()
        self.output()


if __name__ == '__main__':
    MazeGenerateor().generate(30, 20)
