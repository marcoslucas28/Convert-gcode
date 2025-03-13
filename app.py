from flask import Flask, request, send_file
import os
import uuid
from image_to_gcode import ImageToGcode  # Importando o conversor diretamente

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert_image():
    if "image" not in request.files:
        return {"error": "No image uploaded"}, 400

    image = request.files["image"]
    filename = f"{uuid.uuid4()}.png"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename.replace(".png", ".gcode"))
    
    image.save(input_path)
    
    # Executando a conversão diretamente
    converter = ImageToGcode(img=input_path, spread=3.175, area=[200, 200], feedrate=1000, offsets=[[0, 0]])
    with open(output_path, "w") as f:
        f.write(converter.output)
    
    return send_file(output_path, as_attachment=True, download_name="output.gcode")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=True)
