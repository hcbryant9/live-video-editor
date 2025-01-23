# Live Video Editor

A Python application using **Tkinter**, **OpenCV**, and **PIL** to display video frames, providing controls to navigate, zoom, and pan through the frames. This project is an experiment to create a live video editor.

## Controls

- **Frame Navigation:** Move through video frames using the **Previous** and **Next** buttons, or the **Left** and **Right** arrow keys.
- **Zooming:** Zoom in and out using the **Mouse Wheel**, **Up Arrow**, and **Down Arrow** keys.
- **Panning:** Move the displayed frame up, down, left, and right using the **WASD** keys or arrow keys.
- **Random Frame:** Jump to a random frame with the **'F'** key.
- **Play/Pause:** Play or pause the video frames at a set frame rate.
- **Reset:** Reset zoom, pan, and the current frame to the initial state.
- **Terminate:** Exit the viewer and release resources.

## Requirements

- Python 3.6+
- **OpenCV** (for video processing)
- **Pillow** (for image handling)
- **Tkinter** (for GUI)

You can install the necessary dependencies using:

```bash
pip install opencv-python pillow

```

## Setup

1. Clone or download this repository.
2. Place your video file (e.g., `.mov`, `.mp4`) inside the **`assets/`** folder. The path should be correctly specified in the code (e.g., `assets/your_video.mov`).
3. Run the application with:

```bash
python app.py
```

note: it will take a while to launch depending on how large the file is since it converts the video to frames

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

