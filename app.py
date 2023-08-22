from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image, ExifTags
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('File successfully uploaded')
            
            return redirect(url_for('view_metadata', filename=filename))
    
    return render_template('index.html')

@app.route('/view/<filename>')
def view_metadata(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    img = Image.open(filepath)
    exif_data = get_exif_data(img)
    
    return render_template('view_metadata.html', filename=filename, exif_data=exif_data)

@app.route('/delete/<filename>/<tag>', methods=['POST'])
def delete_metadata(filename, tag):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    img = Image.open(filepath)
    try:
        del img.info[tag]
        img.save(filepath)
        flash(f"Metadata '{tag}' deleted successfully")
    except KeyError:
        flash(f"Metadata '{tag}' not found in image")
    
    return redirect(url_for('view_metadata', filename=filename))

def get_exif_data(image):
    exif_data = {}
    try:
        info = image._getexif()
        for tag, value in info.items():
            decoded_tag = ExifTags.TAGS.get(tag, tag)
            exif_data[decoded_tag] = value
    except AttributeError:
        pass
    return exif_data

if __name__ == '__main__':
    app.run(debug=True)
