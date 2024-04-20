import os
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('image_render.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    print(type(file))
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
    return file.filename
    # return f'''<img src="{url_for('static', filename=file.filename)}"
    #                alt="здесь должна была быть картинка, но не нашлась">'''

if __name__ == '__main__':
    app.run(debug=True)