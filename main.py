from PIL import Image

Pixel = 20  # pixel for each cell

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
        # TODO: Randomly generate a valid path from start to finish
        self.matrix[10] = [1 for x in range(self.size)]

    def generate_fake_path(self):
        # TODO: Randomly generate fake paths splitting from the correct path
        pass
    
    def generate(self, size):
        self.path = []
        self.matrix = [[0 for x in range(size)] for x in range(size)]
        self.size = size
        self.create_path()
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
    