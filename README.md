# Book Vision TUI

Point your camera at a bookshelf — YOLO detects the books, Gemini identifies them, Google Books fills in the details, and everything renders live in your terminal.

## How it works

1. **Camera** captures a live video feed (OpenCV)
2. **YOLO** detects book objects in each frame and draws bounding boxes
3. When a book is detected, the frame is **cropped** to the bounding box
4. The cropped image is sent to **Gemini** to identify the book's title and author
5. That title/author is used to query the **Google Books API** for full metadata (cover, publisher, description, ISBN, etc.)
6. The result is displayed in a **Textual** TUI alongside a scan history table

```
Camera → YOLO detection → Crop frame → Gemini (identify) → Google Books API (metadata) → Textual TUI
```

## Requirements

- Python 3.10+
- A webcam
- Gemini API key
- (Optional) A Sixel or Kitty-graphics-capable terminal to render book covers inline

## Setup

```fish
git clone git@github.com:yion-dev/book-vision-tui.git
cd book-vision-tui
python -m venv venv
source venv/bin/activate.fish   # or venv/bin/activate for bash/zsh
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

## Usage

```fish
python main.py
```

| Key | Action |
|---|---|
| `Ctrl+P` | Open command palette |
| `q` | Quit |

In the TUI:

- **Stop / Resume** — pause or resume the camera scanning loop
- **Export CSV** — saves the scan history table to `book_history.csv`

## Models

YOLO weights are not committed to this repo (see `.gitignore`). Download the one you want from [Ultralytics](https://github.com/ultralytics/ultralytics) and place it in `models/`:

| File | Size | Speed | Accuracy |
|---|---|---|---|
| `yolo11n.pt` | smallest | fastest | lowest |
| `yolo11s.pt` | small | fast | good |
| `yolo11l.pt` | large | slower | highest |

## Project structure

```
.
├── config.py
├── interfaces.py
├── main.py
├── state.py
├── models/                  # YOLO weights (not tracked)
├── screens/
│   ├── app.py               # Textual App entrypoint
│   └── widgets/
│       ├── book_card.py
│       ├── camera_view.py
│       └── scan_history.py
└── services/
    ├── cv2.py                # Camera capture loop
    ├── genai.py               # Gemini integration
    └── yolo.py                # YOLO detection service
```

## License

MIT — see [LICENSE](./LICENSE).
