# Image to G-code API

## Overview
This API converts PNG and JPEG images into G-code files for a pen-based CNC machine. It was developed for the *Desenhando Conexões* project, part of the *Umibots* robotics team from *UMI Tânia Leite Santos*. The project aims to make robotics more inclusive by integrating artistic expression through drawing.

## Features
- Accepts **PNG** and **JPEG** images
- Converts images into **G-code** for a pen-based CNC machine
- Provides a single **POST** endpoint (`/convert`) for file conversion
- Designed to be used with **form-data** submission

## Installation

```bash
# Clone the repository
git clone https://github.com/marcoslucas28/Convert-gcode
cd <repository-folder>

# Install dependencies
pip install -r requirements.txt
```

## Usage

### API Endpoint
#### `POST /convert`
- **Description**: Converts a PNG or JPEG image into a G-code file
- **Content-Type**: `multipart/form-data`
- **Request Parameter**:
  - `file`: The image file to be converted (must be PNG or JPEG)
- **Response**: A downloadable G-code file

### Example Request
Using **cURL**:
```bash
curl -X POST "http://localhost:5000/convert" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/image.png"
```

Using **Python (requests library)**:
```python
import requests

url = "http://localhost:5000/convert"
files = {"file": open("path/to/image.png", "rb")}
response = requests.post(url, files=files)

with open("output.gcode", "wb") as f:
    f.write(response.content)
```

## Running the API

Start the server:
```bash
python app.py
```

By default, the API runs on `http://localhost:5000/`.

## About the Project
**Desenhando Conexões** is a research project under **FAPEMA**, offered through the **Prototipando Sonhos** initiative. It aims to make robotics more engaging by integrating artistic drawing with CNC machines. Participants can customize and visualize their drawings as they are brought to life through a mini CNC plotter.

This API plays a crucial role in the project by enabling users to convert their drawings into G-code, which can then be processed by the CNC machine.

## License
This project is open-source. Feel free to contribute or modify as needed!

