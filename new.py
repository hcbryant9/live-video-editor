import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import os
import threading
from tqdm import tqdm
from datetime import datetime
import random

class VideoMixerEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Mixer and Editor")

        # Frame for video uploads
        self.upload_frame = tk.Frame(self.root)
        self.upload_frame.pack(side=tk.TOP, pady=10)

        # Buttons for video uploads
        self.upload_buttons = []
        self.videos = [None, None, None, None]  # Store video frame sequences
        self.current_video_index = 0

        for i in range(4):
            button = tk.Button(self.upload_frame, text=f"Upload Video {i + 1}", command=lambda idx=i: self.upload_video(idx), width=20, height=10)
            button.grid(row=0, column=i, padx=5)
            self.upload_buttons.append(button)

        # Frame for video playback
        self.playback_frame = tk.Frame(self.root)
        self.playback_frame.pack(side=tk.TOP, pady=10)

        self.canvas = tk.Canvas(self.playback_frame, width=640, height=480, bg="black")
        self.canvas.pack()

        # Navigation buttons
        self.nav_frame = tk.Frame(self.root)
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

        self.save_button = tk.Button(self.nav_frame, text="Save Frame", command=self.save_frame)
        self.save_button.pack(side="left", padx=5)

        # Key bindings for switching videos
        self.root.bind("1", lambda event: self.switch_video(0))
        self.root.bind("2", lambda event: self.switch_video(1))
        self.root.bind("3", lambda event: self.switch_video(2))
        self.root.bind("4", lambda event: self.switch_video(3))

        # Key bindings for movement and interaction
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
        self.current_frame_index = 0
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

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

    def save_frame(self):
        """Save the current frame as a jpg file."""
        if self.is_playing:
            self.pause_video()  # Pause the video if it's playing

        # Get the current frame and save it as a JPG file
        frame = self.frames[self.current_frame_index]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        image = Image.fromarray(frame_rgb)

        # Create a file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"saved_frame_{timestamp}.jpg"
        
        # Save the image as JPG
        image.save(save_path)
        print(f"Frame saved as {save_path}")

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
        if self.videos:
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def zoom_out_key(self, event):
        """Zoom out using a keyboard key."""
        self.zoom_factor /= 1.1
        if self.videos:
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])
        else:
            print("can't zoom out")

    def move_up(self, event):
        self.offset_y -= 10  # Move up
        if self.videos:
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])
        

    def move_left(self, event):
        self.offset_x -= 10  # Move left
        if self.videos:
            
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def move_down(self, event):
        self.offset_y += 10  # Move down
        if self.videos:
            
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def move_right(self, event):
        self.offset_x += 10  # Move right
        if self.videos:
            
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    # def random_frame(self):
    #     self.current_frame_index = random.randint(0, len(self.frames) - 1)
    #     self.display_frame(self.frames[self.current_frame_index])

    def random_frame(self):
        # Check if there are videos loaded for the current index
        if self.videos[self.current_video_index]:
            # Generate a random frame index within the range of the loaded video
            self.current_frame_index = random.randint(0, len(self.videos[self.current_video_index]) - 1)
            # Display the random frame
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])
        else:
            print("No video loaded for the current index.")

    def upload_video(self, index):
        file_path = filedialog.askopenfilename(filetypes=[["Video files", "*.mp4;*.avi;*.mov"]])
        if not file_path:
            return

        frames = self.load_video_frames(file_path)
        if frames:
            self.videos[index] = frames
            thumbnail = self.get_thumbnail(frames[0])
            self.upload_buttons[index].config(image=thumbnail, text="")
            self.upload_buttons[index].image = thumbnail  # Prevent garbage collection

    def get_thumbnail(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((160, 120), Image.Resampling.LANCZOS)  # Resize to 4:3 aspect ratio
        return ImageTk.PhotoImage(image)

    def load_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []

        if not cap.isOpened():
            print(f"Error: Could not open video file '{video_path}'")
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        with tqdm(total=total_frames, desc="Loading video frames", unit="frame") as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
                pbar.update(1)

        cap.release()
        return frames

    def display_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        
        new_width = int(image.width * self.zoom_factor)
        new_height = int(image.height * self.zoom_factor)
        image = image.resize((new_width, new_height))
    
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

    def play_video(self):
        if not self.is_playing and self.videos[self.current_video_index]:
            self.is_playing = True
            self.play_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self._play_video()

    def _play_video(self):
        if self.is_playing and self.current_frame_index < len(self.videos[self.current_video_index]) - 1:
            self.current_frame_index += 1
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])
            self.root.after(30, self._play_video)
        else:
            self.is_playing = False
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")

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
        # release_frames(self.frames)  

    def reset_video(self):
        self.is_playing = False
        self.current_frame_index = 0
        if self.videos[self.current_video_index]:
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def prev_frame(self):
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def next_frame(self):
        if self.current_frame_index < len(self.videos[self.current_video_index]) - 1:
            self.current_frame_index += 1
            self.display_frame(self.videos[self.current_video_index][self.current_frame_index])

    def switch_video(self, index):
        if self.videos[index]:
            self.current_video_index = index
            self.current_frame_index = 0
            self.reset_video()

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

    def reset(self):
        """Reset the zoom, pan, and frame to their initial state."""
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.current_frame_index = 0
        self.display_frame(self.frames[self.current_frame_index])

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoMixerEditor(root)
    root.mainloop()
