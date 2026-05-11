import urllib.request
import os, json, base64

url = 'http://127.0.0.1:5000/api/detect'
filepath = 'temp_uploads/test_video.mp4'
if not os.path.exists(filepath):
    import cv2, numpy as np
    os.makedirs('temp_uploads', exist_ok=True)
    h,w=80,80; fps=5
    fourcc=cv2.VideoWriter_fourcc(*'mp4v')
    out=cv2.VideoWriter(filepath,fourcc,fps,(w,h))
    for i in range(3):
        frame=(np.random.rand(h,w,3)*255).astype('uint8')
        out.write(frame)
    out.release()
    print('created sample video')

boundary='----WebKitFormBoundary7MA4YWxkTrZu0gW'
headers={'Content-Type':f'multipart/form-data; boundary={boundary}'}
body=[]
body.append(f'--{boundary}')
body.append('Content-Disposition: form-data; name="file"; filename="test_video.mp4"')
body.append('Content-Type: video/mp4')
body.append('')
with open(filepath,'rb') as f:
    filedata=f.read()
body_bytes=b'\r\n'.join(s.encode('utf-8') if isinstance(s,str) else s for s in body)+b'\r\n'+filedata+b'\r\n'+f'--{boundary}--\r\n'.encode('utf-8')
req=urllib.request.Request(url,data=body_bytes,headers=headers,method='POST')
with urllib.request.urlopen(req,timeout=120) as resp:
    data=json.loads(resp.read().decode('utf-8'))
    print(data.keys())
    print('frame_count',data.get('frame_count'))
    print('len frames', len(data.get('frames',[])))
    print('first frame keys', list(data.get('frames',[{}])[0].keys()) if data.get('frames') else None)
    print('first frame detection count', len(data.get('frames',[{'detections':[]}])[0]['detections']) if data.get('frames') else None)
    print('first frame image length', len(data.get('frames',[{'image':''}])[0]['image']) if data.get('frames') else None)
