import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import random
import shutil
import string

from flask import Flask, render_template, request, send_file, after_this_request

import easyyoutubemusic.main as yt

app = Flask(__name__)

def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

@app.route("/")
def home(error_message=None):
    return render_template("index.html", error_message=error_message)

@app.route('/downloadLink', methods=['POST'])
def downloadLink():
    youtube_link = request.form['link_text']

    # Create temporary directory.
    dir_name = random_string(16)
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(cur_dir, dir_name)
    os.makedirs(dir_path)

    # Download music into temp folder.
    try:
        yt.download_link(youtube_link, dir_path)
    except BaseException as e:
        # Remove temp dir and return error message.
        shutil.rmtree(dir_path)
        return home(error_message=str(e))

    # Zip temporary folder.
    zip_name = dir_name
    zip_path = os.path.join(cur_dir, zip_name)
    shutil.make_archive(zip_path, 'zip', dir_path)  # Shutil adds .zip at the end of the file.

    # Clean up all temporary files after request.
    @after_this_request
    def cleanup(response):
        shutil.rmtree(dir_path)
        os.remove(zip_path + '.zip')

        return response

    return send_file(zip_path + '.zip', attachment_filename='music_from_nenad.zip', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)