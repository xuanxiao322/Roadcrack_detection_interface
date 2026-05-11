import os
import cv2
import numpy as np
from app import predict_source

os.makedirs('temp_uploads', exist_ok=True)
path = 'temp_uploads/test_video.mp4'
h, w = 128, 128
fps = 5
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(path, fourcc, fps, (w, h))
for _ in range(3):
    frame = (np.random.rand(h, w, 3) * 255).astype('uint8')
    out.write(frame)
out.release()
print('created', path)
results = predict_source(path, conf=0.25)
print('results type', type(results))
print('len', len(results))
print('first type', type(results[0]))
print('has boxes', results[0].boxes is not None)
print('plot shape', results[0].plot().shape)
