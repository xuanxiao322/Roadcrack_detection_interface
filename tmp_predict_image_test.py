import io
from PIL import Image
from app import predict_image

img = Image.new('RGB', (100, 100), (255, 255, 255))
path = 'temp_uploads/tmp_test.png'
img.save(path)
try:
    result = predict_image(path, conf=0.25)
    print('result:', result)
    if result is not None and hasattr(result, 'boxes'):
        print('boxes count:', len(result.boxes))
        for box in result.boxes:
            print('box', box)
except Exception as e:
    import traceback
    traceback.print_exc()
