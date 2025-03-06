from flask import Flask, render_template, request, send_file, redirect, url_for
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import xml.dom.minidom

app = Flask(__name__)

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
    
    try:
        # Ler o conteúdo do arquivo diretamente da memória
        xml_content = file.read().decode('utf-8')
        root = ET.fromstring(xml_content)
        
        # Transformar em string sem formatação
        xml_string = StringIO()
        ET.ElementTree(root).write(xml_string, encoding='unicode', xml_declaration=True)
        xml_string.seek(0)
        
        # Formatá-lo com minidom
        xml_prettified = xml.dom.minidom.parseString(xml_string.getvalue())
        formatted_xml = xml_prettified.toprettyxml(indent="  ")
        
        # Armazenar em uma variável de sessão para download
        formatted_filename = original_filename.replace('.xml', '_indentado.xml')
        
        # Em vez de salvar no sistema de arquivos, passamos uma flag para indicar que o download está pronto
        return render_template('index.html', 
                              download_link=f'/download/{formatted_filename}',
                              formatted_xml=formatted_xml)
    
    except ET.ParseError:
        return "Arquivo XML inválido!", 400
    except Exception as e:
        return f"Erro ao processar o arquivo: {str(e)}", 500

@app.route('/download/<filename>')
def download_file(filename):
    # Recuperar o XML formatado da requisição anterior
    formatted_xml = request.args.get('xml', '')
    
    if not formatted_xml:
        # Se não há XML formatado, usamos o da sessão (via query string)
        formatted_xml = request.args.get('xml_content', '')
    
    # Preparar o arquivo para download diretamente na memória
    mem_file = BytesIO(formatted_xml.encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/xml'
    )

if __name__ == '__main__':
    app.run(debug=True)