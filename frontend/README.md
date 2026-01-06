# AutoRAG Diagnostic Assistant - Frontend

This folder handles what you see in the browser. It is a simple website that talks to the Backend.

## Code File Explanations

### `index.html` (The Skeleton)
This is the main structure of the webpage.
- **What it does:** It defines the layout: the sidebar for uploads, the chat window, the input box, and the buttons.
- **Simple analogy:** The frame and walls of the car.

### `styles.css` (The Paint & Interior)
This file controls how everything looks.
- **What it does:** It sets the dark theme, the neon blue accents, the fonts, and the animations. It gives the app its "Futuristic Automotive" look.
- **Simple analogy:** The paint job, leather seats, and dashboard lights.

### `script.js` (The Controls)
This file makes the page interactive.
- **What it does:**
    - When you drag-and-drop a file, this script sends it to the backend.
    - When you type a message and hit Enter, this script sends it to the backend and waits for the answer.
    - It also updates the "System Status" light.
- **Simple analogy:** The steering wheel, pedals, and touchscreen interface.
