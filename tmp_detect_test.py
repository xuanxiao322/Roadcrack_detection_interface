from PIL import Image
import io
import urllib.request

img = Image.new('RGB', (100, 100), (255, 255, 255))
buf = io.BytesIO()
img.save(buf, 'PNG')
data = buf.getvalue()
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = b''
body += ('--' + boundary + '\r\n').encode()
body += b'Content-Disposition: form-data; name="file"; filename="test.png"\r\n'
body += b'Content-Type: image/png\r\n\r\n'
body += data + b'\r\n'
body += ('--' + boundary + '\r\n').encode()
body += b'Content-Disposition: form-data; name="conf"\r\n\r\n'
body += b'0.25\r\n'
body += ('--' + boundary + '--\r\n').encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/detect', data=body)
req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
with urllib.request.urlopen(req, timeout=60) as resp:
    print(resp.status)
    print(resp.read().decode()[:1200])
