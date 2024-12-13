import tkinter as tk

class DrawingGrid:
    def __init__(self, root, video_viewer):
        self.root = root
        self.root.title("Drawing Grid")
        self.video_viewer = video_viewer
        
        # Create a 24x24 grid
        self.grid_size = 24
        self.cell_size = 20  # Each cell is 20x20 pixels
        self.canvas = tk.Canvas(root, width=self.grid_size * self.cell_size, height=self.grid_size * self.cell_size, bg="white")
        self.canvas.pack()

        # Initialize the grid as empty (False means no drawing in that cell)
        self.grid_data = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Draw the grid lines
        self.draw_grid_lines()

        # Bind mouse click to draw
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_grid_lines(self):
        """Draw the grid lines for the 24x24 grid."""
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, fill="black")
            self.canvas.create_line(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, fill="black")

    def on_click(self, event):
        """Handle mouse click to toggle the drawing state."""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        # Toggle the cell (draw or erase)
        self.grid_data[y][x] = not self.grid_data[y][x]
        
        # Redraw the grid
        self.redraw_grid()

        # Send the updated grid to the video player for overlay
        self.video_viewer.update_overlay(self.grid_data)

    def redraw_grid(self):
        """Redraw the grid with the current drawing state."""
        self.canvas.delete("all")
        self.draw_grid_lines()
        
        # Fill in the cells that are marked as True (drawn)
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid_data[y][x]:
                    self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, 
                                                 (x + 1) * self.cell_size, (y + 1) * self.cell_size, 
                                                 fill="black", outline="black")

    def get_drawing(self):
        """Return the grid data for the current drawing."""
        return self.grid_data
