import urllib.request
html = urllib.request.urlopen('http://127.0.0.1:5000').read().decode('utf-8')
print('frameGallery' in html)
print('renderFrameGallery' in html)
print('视频预览已加载' in html)
