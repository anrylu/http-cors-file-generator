from flask import Flask, request, send_file
from flask_cors import CORS
import os
import random

app = Flask(__name__)
CORS(app)

@app.route('/download')
def generate_random_file():
    file_size = int(request.args.get('size', default=1024))  # default size is 1024 bytes
    
    # Generate random content for the file
    random_content = os.urandom(file_size)
    
    # Save the content to a temporary file
    temp_filename = f"temp_{random.randint(1000, 9999)}.bin"
    with open(temp_filename, 'wb') as file:
        file.write(random_content)
    
    # Check if the 'Range' header is present in the request
    range_header = request.headers.get('Range')
    if range_header:
        # Parse the range header to determine the requested byte range
        start, end = range_header.strip().replace('bytes=', '').split('-')
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1
        
        # Calculate the length of the requested byte range
        length = end - start + 1
        
        # Open the temporary file in binary mode
        with open(temp_filename, 'rb') as file:
            file.seek(start)
            data = file.read(length)
        
        # Set the appropriate headers for a partial response
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Content-Length': str(length),
            'Accept-Ranges': 'bytes'
        }
        
        # Create a partial response with the requested byte range
        return data, 206, headers
    
    # Set the headers for the full response
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(file_size),
        'Content-Disposition': 'attachment; filename=random_file.bin',
        'Accept-Ranges': 'bytes'
    }
    
    # Send the full file as a response to the client
    return send_file(temp_filename, as_attachment=True, attachment_filename='random_file.bin', headers=headers)

if __name__ == '__main__':
    app.run()

