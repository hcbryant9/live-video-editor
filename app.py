import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import random
import threading
from tqdm import tqdm

class VideoFrameViewer:
    def __init__(self, root, video_path):
        self.root = root
        self.root.title("Video Frame Viewer")

        # Load video
        self.frames = load_video_frames(video_path)
        if not self.frames:
            print("Error: No frames found!")
            return

        # Get the width and height
        first_frame = self.frames[0]
        self.video_width = first_frame.shape[1] / 1.5
        self.video_height = first_frame.shape[0] / 1.5

        # Set the canvas
        self.canvas = tk.Canvas(root, width=self.video_width, height=self.video_height, bg='black')
        self.canvas.pack()

        
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(pady=10)

        self.prev_button = tk.Button(self.nav_frame, text="Previous", command=self.prev_frame, repeatdelay=100, repeatinterval=50)
        self.prev_button.pack(side="left", padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.next_frame, repeatdelay=100, repeatinterval=50)
        self.next_button.pack(side="left", padx=5)

        self.random_button = tk.Button(self.nav_frame, text="Random Frame", command=self.random_frame)
        self.random_button.pack(side="left", padx=5)

        self.play_button = tk.Button(self.nav_frame, text="Play", command=self.play_video)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = tk.Button(self.nav_frame, text="Pause", command=self.pause_video, state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.terminate_button = tk.Button(self.nav_frame, text="Terminate", command=self.terminate)
        self.terminate_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.nav_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5)

        self.current_frame_index = 0
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

        
        self.display_frame(self.frames[self.current_frame_index])

        # Initialize key press state
        self.key_state = {
            'w': False,
            'a': False,
            's': False,
            'd': False,
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'f': False,  
        }

        # Bind key press events
        self.canvas.bind("<KeyPress-w>", self.key_press)
        self.canvas.bind("<KeyPress-a>", self.key_press)
        self.canvas.bind("<KeyPress-s>", self.key_press)
        self.canvas.bind("<KeyPress-d>", self.key_press)
        self.canvas.bind("<KeyPress-Left>", self.key_press)
        self.canvas.bind("<KeyPress-Right>", self.key_press)
        self.canvas.bind("<KeyPress-Up>", self.key_press)
        self.canvas.bind("<KeyPress-Down>", self.key_press)
        self.canvas.bind("<KeyPress-f>", self.key_press)  
        self.canvas.bind("<KeyRelease-w>", self.key_release)
        self.canvas.bind("<KeyRelease-a>", self.key_release)
        self.canvas.bind("<KeyRelease-s>", self.key_release)
        self.canvas.bind("<KeyRelease-d>", self.key_release)
        self.canvas.bind("<KeyRelease-Left>", self.key_release)
        self.canvas.bind("<KeyRelease-Right>", self.key_release)
        self.canvas.bind("<KeyRelease-Up>", self.key_release)
        self.canvas.bind("<KeyRelease-Down>", self.key_release)
        self.canvas.bind("<KeyRelease-f>", self.key_release)  

        self.canvas.focus_set()

      
        self.root.after(50, self.update)


        self.is_playing = False

    def display_frame(self, frame):
        """Display a single frame on the canvas and handle resizing/zooming."""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        # Apply zoom factor to resize the frame
        new_width = int(image.width * self.zoom_factor)
        new_height = int(image.height * self.zoom_factor)
        image = image.resize((new_width, new_height))

        # Convert the image for Tkinter
        self.tk_image = ImageTk.PhotoImage(image)

        if not hasattr(self, "canvas_image"):
            # Create the image once
            self.canvas_image = self.canvas.create_image(
                self.offset_x, self.offset_y, image=self.tk_image, anchor="nw"
            )
        else:
            # Update the image content and reposition it
            self.canvas.itemconfig(self.canvas_image, image=self.tk_image)
            self.canvas.coords(self.canvas_image, self.offset_x, self.offset_y)

    def on_zoom(self, event):
        """Zoom in or out based on mouse wheel or key events."""
        if event.delta > 0:
            self.zoom_factor *= 1.1  # Zoom in
        else:
            self.zoom_factor /= 1.1  # Zoom out

        # Redraw the current frame with the new zoom factor
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def zoom_in_key(self, event):
        """Zoom in using a keyboard key."""
        self.zoom_factor *= 1.1
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def zoom_out_key(self, event):
        """Zoom out using a keyboard key."""
        self.zoom_factor /= 1.1
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def move_up(self, event):
        self.offset_y -= 10  # Move up
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def move_left(self, event):
        self.offset_x -= 10  # Move left
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def move_down(self, event):
        self.offset_y += 10  # Move down
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def move_right(self, event):
        self.offset_x += 10  # Move right
        if self.frames:
            self.display_frame(self.frames[self.current_frame_index])

    def prev_frame(self):
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.display_frame(self.frames[self.current_frame_index])

    def next_frame(self):
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.display_frame(self.frames[self.current_frame_index])


    def play_video(self):
        """Play the video using root.after for smoother playback."""
        if not self.is_playing:
            self.is_playing = True
            self.play_button.config(state="disabled") 
            self.pause_button.config(state="normal")  
            self._play_video()

    def _play_video(self):
        """Play the video frame-by-frame."""
        if self.is_playing and self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.display_frame(self.frames[self.current_frame_index])
            # Schedule the next frame display after 30ms
            self.root.after(30, self._play_video)
        else:
            self.is_playing = False
            self.play_button.config(state="normal")  
            self.pause_button.config(state="disabled")

    def prev_frame_key(self, event):
        self.prev_frame()

    def next_frame_key(self, event):
        self.next_frame()

    def random_frame(self):
        self.current_frame_index = random.randint(0, len(self.frames) - 1)
        self.display_frame(self.frames[self.current_frame_index])


    def pause_video(self):
        self.is_playing = False
        self.play_button.config(state="normal")  
        self.pause_button.config(state="disabled")  


    def terminate(self):
        self.is_playing = False
        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.root.quit()  
        self.root.destroy()  
        release_frames(self.frames)  

    def reset(self):
        """Reset the zoom, pan, and frame to their initial state."""
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.current_frame_index = 0
        self.display_frame(self.frames[self.current_frame_index])

    def key_press(self, event):
        """Mark the key as pressed."""
        key = event.keysym.lower()
        if key in self.key_state:
            self.key_state[key] = True

    def key_release(self, event):
        """Mark the key as released."""
        key = event.keysym.lower()
        if key in self.key_state:
            self.key_state[key] = False

    def update(self):
        """Check the key states and perform actions."""
        if self.key_state['w']:
            self.move_up(None)
        if self.key_state['a']:
            self.move_left(None)
        if self.key_state['s']:
            self.move_down(None)
        if self.key_state['d']:
            self.move_right(None)
        if self.key_state['left']:
            self.prev_frame()
        if self.key_state['right']:
            self.next_frame()
        if self.key_state['up']:
            self.zoom_in_key(None)
        if self.key_state['down']:
            self.zoom_out_key(None)
        if self.key_state['f']:
            self.random_frame()

        self.root.after(50, self.update)


def load_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    if not cap.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return []

    # Get total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Initialize the progress bar with the total frame count
    with tqdm(total=total_frames, desc="Converting video to frames", unit="frame") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            pbar.update(1)  # Update progress bar after each frame
    
    cap.release()
    return frames


def release_frames(frames):
    for frame in frames:
        frame.release()


if __name__ == "__main__":
    root = tk.Tk()
    video_path = os.path.join("assets", "original.mov")
    if os.path.exists(video_path):
        viewer = VideoFrameViewer(root, video_path)
    else:
        print(f"Error: Video file '{video_path}' not found in the assets folder.")

    root.mainloop()
