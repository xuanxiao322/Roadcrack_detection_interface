import os, traceback
import numpy as np
import cv2
from app import predict_source

os.makedirs('temp_uploads', exist_ok=True)
path = 'temp_uploads/test_video_debug.mp4'
if not os.path.exists(path):
    h,w=128,128; fps=5
    fourcc=cv2.VideoWriter_fourcc(*'mp4v')
    out=cv2.VideoWriter(path,fourcc,fps,(w,h))
    for _ in range(3):
        frame=(np.random.rand(h,w,3)*255).astype('uint8')
        out.write(frame)
    out.release()
with open('temp_debug_output.txt','w',encoding='utf-8') as f:
    try:
        results=predict_source(path, conf=0.25)
        f.write(f'results type: {type(results)}\n')
        try:
            f.write(f'results len: {len(results)}\n')
        except Exception as e:
            f.write(f'len error: {e}\n')
        if hasattr(results, '__getitem__'):
            try:
                r = results[0]
                f.write(f'first type: {type(r)}\n')
                f.write(f'first plot shape: {r.plot().shape}\n')
                f.write(f'first boxes: {r.boxes}\n')
            except Exception as e:
                f.write(f'first access error: {e}\n')
        else:
            f.write('no __getitem__\n')
    except Exception as e:
        f.write('exception:\n')
        traceback.print_exc(file=f)
