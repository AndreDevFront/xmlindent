from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import xml.dom.minidom

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'

# Formulário
class UploadForm(FlaskForm):
    xml_file = FileField('XML File')
    submit = SubmitField('Enviar')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    download_file_content = None
    download_filename = None
    
    if form.validate_on_submit():
        file = form.xml_file.data
        if not file.filename.endswith('.xml'):
            return "Por favor, envie um arquivo XML!", 400
        
        original_filename = secure_filename(file.filename)
        
        # Ler o XML diretamente do upload
        try:
            xml_content = file.read().decode('utf-8')
            tree = ET.ElementTree(ET.fromstring(xml_content))
        except ET.ParseError:
            return "Arquivo XML inválido!", 400
        
        root = tree.getroot()
        
        # Transformar em string sem formatação
        xml_string = StringIO()
        ET.ElementTree(root).write(xml_string, encoding='unicode', xml_declaration=True)
        xml_string.seek(0)
        
        # Formatá-lo com minidom
        xml_prettified = xml.dom.minidom.parseString(xml_string.getvalue())
        formatted_xml = xml_prettified.toprettyxml(indent="  ")
        
        # Preparar o arquivo para download na memória
        download_filename = original_filename.replace('.xml', '_indentado.xml')
        download_file_content = BytesIO(formatted_xml.encode('utf-8'))
        download_file_content.seek(0)
    
    if download_file_content:
        return send_file(
            download_file_content,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/xml'
        )
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)