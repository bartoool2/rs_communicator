from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi


class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}

            print(postvars)
            self.send_response( 200 )
            self.send_header( "Content-type", "text")
            self.send_header( "Content-length", str(len("response")) )
            self.end_headers()
            self.wfile.write("response")
        except:
          print "Error"