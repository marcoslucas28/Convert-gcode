from flask import Flask, request, send_file
from image_to_gcode import convert_image_to_gcode
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400
    
    # Salva o arquivo recebido
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    use_curves = request.form.get("use_curves", "true").lower() == "true"

    # Define o nome do arquivo de saída
    output_filename = os.path.splitext(file.filename)[0] + ".gcode"
    output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        if file.filename.lower().endswith(".svg"):
            gcode = convert_svg_to_gcode(filepath, use_curves)
        else:
            gcode = convert_image_to_gcode(filepath, use_curves)

        # Salva o G-code em um arquivo
        with open(output_filepath, "w") as f:
            f.write(gcode)

        os.remove(filepath)  # Remove o arquivo original após a conversão

        # Envia o arquivo para download
        return send_file(output_filepath, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500  # Tratamento de erros

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=True)
