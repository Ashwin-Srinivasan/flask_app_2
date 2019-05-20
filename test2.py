import os
from flask import Flask, flash, request, redirect, url_for, render_template, g
from werkzeug.utils import secure_filename
from flask import send_from_directory
import api
from flask_jsglue import JSGlue

fileList = []
values_dict = {}

UPLOAD_FOLDER = '/Users/ashwin/Documents/MIT/Spring 2019/UROP/flask_app'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
jsglue = JSGlue(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/2', methods=['GET', 'POST'])
def upload_file():
    global fileList
    global values_dict
    if request.method == 'POST':
        fileList = []
        # check if the post request has the file part
        filelist = [ f for f in os.listdir("static")]
        for f in filelist:
            os.remove(os.path.join("static", f))
        filenames = []
        uploaded_files = request.files.getlist("file-1[]")
        for file in uploaded_files:
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = secure_filename(file.filename)
                # Move the file form the temporal folder to the upload
                # folder we setup
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'static', filename))
                # Save the filename into a list, we'll use it later
                filenames.append(os.path.join(app.config['UPLOAD_FOLDER'], 'static', filename))

                #pass the file paths to azure
        values_dict = api.call(filenames)
        for file in os.listdir("static"):
             filename = os.fsdecode(file)
             #print(filename)
             fileList.append(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], "display_2.html")

@app.route('/3')
def render_file():
    global fileList
    #print(fileList)
    return render_template('display_3.html', files = fileList)

@app.route('/4')
def render_json():
    global values_dict
    return render_template('display.html', data = values_dict)
#Store the list of file paths on database or use global variable?
#in render_file, get list from database
#combos of two bounding boxes for each image
