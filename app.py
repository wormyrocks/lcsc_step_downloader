from flask import Flask, send_file, request, abort
from io import BytesIO
from easyeda2kicad.easyeda.easyeda_api import EasyedaApi
from easyeda2kicad.easyeda.easyeda_importer import Easyeda3dModelImporter

def get_lcsc_model(id):
    try:
        api = EasyedaApi()
        cad_data = api.get_cad_data_of_component(lcsc_id=id)
        m = Easyeda3dModelImporter(cad_data, download_raw_3d_model=False).create_3d_model()
        name = m.name
        data = api.get_step_3d_model(m.uuid)
        return name, data
    except:
        return None, None
    
app = Flask(__name__)

@app.route("/get_model", methods=['GET'])
@app.route("/get_model/<lcsc_id>", methods=['GET'])
def get_model(lcsc_id=None):
    if not lcsc_id:
        lcsc_id = request.args['lcsc_id']

    print(lcsc_id)
    name,data = get_lcsc_model(lcsc_id)
    if name and data:
        buffer = BytesIO()
        buffer.write(data)
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=name+".step",
            mimetype='application/step'
        )
    else:
        abort(404)

@app.route("/")
def index():
    return """<form action="/get_model" method="GET">LCSC ID : <input type="text" name="lcsc_id"> <input type="submit" value="Download"></form>"""
    
if __name__ == '__main__':
    app.run()