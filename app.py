from flask import Flask, render_template, request, redirect, abort, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory to store generated HTML files
HTML_DIR = os.path.join(os.getcwd(), 'html_files')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static')

if not os.path.exists(HTML_DIR):
    os.makedirs(HTML_DIR)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    project_name = request.form['project_name']
    project_description = request.form['project_description']


    # Check if an image file was uploaded
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    # If the user does not select a file, the browser submits an empty file without a filename
    if image.filename == '':
        return redirect(request.url)

    # Check if the file is allowed
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
    else:
        return abort(400, 'Invalid file format')

    link_pairs = [(request.form[f'name{i}'], request.form[f'url{i}']) for i in range(1, 6) if request.form.get(f'name{i}') and request.form.get(f'url{i}')]

    # Pass project name, image path, and link pairs to the page.html template
    rendered_template = render_template('page.html', page_name=project_name, project_description=project_description, image_path=os.path.basename(image_path), links=link_pairs)

    # Save the rendered template to an HTML file
    html_filename = os.path.join(HTML_DIR, f"{project_name}.html")
    with open(html_filename, 'w') as html_file:
        html_file.write(rendered_template)

    return redirect(url_for('show_page', page_name=project_name))


@app.route('/pages/<string:page_name>')
def show_page(page_name):
    # Check if the HTML file exists
    filename = os.path.join(HTML_DIR, f"{page_name}.html")
    if os.path.exists(filename):
        return send_from_directory(HTML_DIR, f"{page_name}.html")
    else:
        abort(404)



if __name__ == '__main__':
    app.run(debug=True)
