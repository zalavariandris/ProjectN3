# -*- coding: utf-8 -*-
import re
import sys
import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from PIL import Image

class FileUploadHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        wasSuccess, files_uploaded = self.handle_file_uploads()

        # Compose a response to the client
        response_obj = {
            "wasSuccess": wasSuccess,
            "files_uploaded": files_uploaded,
            "client_address": self.client_address
        }

        print(response_obj)

        blob = response_obj['files_uploaded'][0]
        img = Image.open(blob)
        print("Image:", img)
        img.save("screenshot", "PNG")

        response_str = json.dumps(response_obj)
        # Send our response code, header, and data
        self.send_response(200)
        self.send_header("Content-type", "Application/json")
        self.send_header("Content-Length", len(response_str))
        self.end_headers()
        self.wfile.write(response_str.encode('utf-8'))


    def read_line(self):
        line_str = self.rfile.readline().decode('ISO-8859-1')
        self.char_remaining -= len(line_str)
        return line_str

    def handle_file_uploads(self):
        """
        Take the post request and save any files received to the same folder
        as this script.
        Returns
            wasSuccess: bool: whether the process was a success
            files_uploaded: list of string: files that were created
        """
        self.char_remaining = int(self.headers['content-length'])
        # Find the boundary from content-type, which might look like:
        # 'multipart/form-data; boundary=----WebKitFormBoundaryUI1LY7c2BiEKGfFk'
        boundary = self.headers['content-type'].split("=")[1]

        basepath = self.translate_path(self.path)
        # Strip this script's name from the path so it's just a folder
        basepath = os.path.dirname(basepath)

        # ----WebKitFormBoundaryUI1LY7c2BiEKGfFk
        line_str = self.read_line()
        if not boundary in line_str:
            self.log_message("Content did NOT begin with boundary as " +
                             "it should")
            return False, []

        files_uploaded = []
        while self.char_remaining > 0:
            # Breaking out of this loop on anything except a boundary
            # an end-of-file will be a failure, so let's assume that
            wasSuccess = False

            # Content-Disposition: form-data; name="file"; filfile.tile_position.x, tile_position.yename="README.md"
            line_str = self.read_line()
            filename = re.findall('Content-Disposition.*name="file"; ' +
                                  'filename="(.*)"', line_str)
            if not filename:
                self.log_message("Can't find filename " + filename)
                break
            else:
                filename = filename[0]
            filepath = os.path.join(basepath, filename)
            try:
                outfile = open(filepath, 'wb')
            except IOError:
                self.log_message("Can't create file " + str(filepath) +
                                 " to write; do you have permission to write?")
                break

            # Content-Type: application/octet-stream
            line_str = self.read_line()

            # Blank line
            line_str = self.read_line()

            # First real line of code
            preline = self.read_line()
            # Loop through the POST until we find another boundary line,
            # signifying the end of this file and the possible start of another
            while self.char_remaining > 0:
                line_str = self.read_line()

                # ----WebKitFormBoundaryUI1LY7c2BiEKGfFk
                if boundary in line_str:
                    preline = preline[0:-1]
                    if preline.endswith('\r'):
                        preline = preline[0:-1]
                    outfile.write(preline.encode('ISO-8859-1'))
                    outfile.close()
                    self.log_message("File '%s' upload success!" % filename)
                    files_uploaded.append(filename)
                    # If this was the last file, the session was a success!
                    wasSuccess = True
                    break
                else:
                    outfile.write(preline.encode('ISO-8859-1'))
                    preline = line_str

        from merge_files import merge_images
        img = merge_images(files_uploaded)
        img.save("joined.tiff", "TIFF")

        return wasSuccess, files_uploaded

def startup_server():
    httpd = HTTPServer(("", 8000), FileUploadHTTPRequestHandler)
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":    
    startup_server()
