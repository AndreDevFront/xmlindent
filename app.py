from flask import Flask, render_template, request, send_file
import os
import xml.etree.ElementTree as ET
from io import StringIO
import xml.dom.minidom

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html', download_link=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'xml_file' not in request.files:
        return "Nenhum arquivo enviado!", 400
    file = request.files['xml_file']
    
    if file.filename == '':
        return "Nenhum arquivo selecionado!", 400
    if not file.filename.endswith('.xml'):
        return "Por favor, envie um arquivo XML!", 400
    
    original_filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    file.save(filepath)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    xml_string = StringIO()
    ET.ElementTree(root).write(xml_string, encoding='unicode', xml_declaration=True)
    xml_string.seek(0)
    
    xml_prettified = xml.dom.minidom.parseString(xml_string.getvalue())
    formatted_xml = xml_prettified.toprettyxml(indent="  ")
    
    formatted_filename = original_filename.replace('.xml', '_indentado.xml')
    formatted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], formatted_filename)
    with open(formatted_filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)
    
    os.remove(filepath)
    
    return render_template('index.html', download_link=f'/download/{formatted_filename}')

@app.route('/download/<filename>')
def download_file(filename):
    formatted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(formatted_filepath, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run()