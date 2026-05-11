"""
道路裂缝检测Web应用 - Flask后端
参数完全匹配模型配置
"""
from flask import Flask, render_template, request, jsonify, send_file
from ultralytics import YOLO
import cv2
import numpy as np
import os
from pathlib import Path
import io
from PIL import Image
import base64
import json
import torch

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# 自动选择设备：如果没有可用 CUDA，回退到 CPU
DEVICE = "0" if torch.cuda.is_available() else "cpu"

# ==================== 模型配置参数 ====================
# 与args.yaml完全一致
MODEL_CONFIG = {
    "model_path": "weights/best.pt",  # 使用最佳权重
    "imgsz": 640,                      # 与args.yaml一致
    "conf": 0.25,                      # 置信度阈值
    "iou": 0.7,                        # IOU阈值，与args.yaml一致
    "max_det": 300,                    # 最大检测数，与args.yaml一致
    "device": DEVICE,                  # 设备自动选择
    "augment": False,                  # 推理不使用增强，与args.yaml一致
    "agnostic_nms": False,             # 与args.yaml一致
    "retina_masks": False,             # 与args.yaml一致
    "verbose": True,                   # 与args.yaml一致
}
# ====================================================

# 全局模型实例
model = None

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mpg', '.mpeg', '.m4v'}
MAX_VIDEO_FRAMES = 30

def is_video_file(file_path):
    return Path(file_path).suffix.lower() in VIDEO_EXTENSIONS


def sample_frame_indices(total_frames, max_frames=MAX_VIDEO_FRAMES):
    if total_frames <= max_frames:
        return list(range(total_frames))
    step = max(1, total_frames // max_frames)
    indices = list(range(0, total_frames, step))
    return indices[:max_frames]


def is_image_file(file_path):
    return Path(file_path).suffix.lower() in IMAGE_EXTENSIONS


def encode_file_to_base64(file_path):
    with open(file_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def encode_array_to_base64(image_array):
    success, buffer = cv2.imencode('.png', image_array)
    if not success:
        raise ValueError('图像编码失败')
    return base64.b64encode(buffer).decode('utf-8')


def load_model():
    """加载模型"""
    global model
    if model is None:
        model_path = os.path.join(os.path.dirname(__file__), MODEL_CONFIG['model_path'])
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        model = YOLO(model_path)
        print(f"模型已加载: {model_path}")
        print(f"配置参数: {json.dumps(MODEL_CONFIG, indent=2, ensure_ascii=False)}")
    
    return model

def predict_source(source_path, conf=None):
    """对单张图像或视频源进行预测"""
    model = load_model()
    
    if conf is None:
        conf = MODEL_CONFIG['conf']
    
    results = model.predict(
        source=source_path,
        imgsz=MODEL_CONFIG['imgsz'],
        conf=conf,
        iou=MODEL_CONFIG['iou'],
        max_det=MODEL_CONFIG['max_det'],
        device=MODEL_CONFIG['device'],
        augment=MODEL_CONFIG['augment'],
        agnostic_nms=MODEL_CONFIG['agnostic_nms'],
        retina_masks=MODEL_CONFIG['retina_masks'],
        verbose=False
    )
    
    return results


def annotate_video(video_path, results, output_path):
    """对视频的每一帧进行标注并输出完整视频"""
    if not results:
        return None

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    if width == 0 or height == 0:
        fallback_frame = None
        if hasattr(results[0], 'orig_img') and results[0].orig_img is not None:
            fallback_frame = results[0].orig_img
        else:
            fallback_frame = results[0].plot()
        if fallback_frame is not None:
            height, width = fallback_frame.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame_result in results:
        frame = frame_result.plot()
        if frame is None:
            continue
        if frame.shape[1] != width or frame.shape[0] != height:
            frame = cv2.resize(frame, (width, height))
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        out.write(frame)

    out.release()
    return output_path


def predict_image(image_path, conf=None):
    """
    对图像进行预测
    
    Args:
        image_path: 图像文件路径
        conf: 置信度阈值（如果为None使用配置的默认值）
    
    Returns:
        预测结果
    """
    results = predict_source(image_path, conf)
    return results[0] if results else None

def draw_results(image_path, result, output_path):
    """
    绘制检测结果
    
    Args:
        image_path: 原图路径
        result: 预测结果
        output_path: 输出图路径
    """
    if result is None:
        return None
    
    # 使用result的plot方法绘制
    annotated_frame = result.plot()
    cv2.imwrite(output_path, annotated_frame)
    
    return output_path

def encode_image_to_base64(image_path):
    """将图像编码为base64"""
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取模型配置信息"""
    return jsonify({
        'model_config': MODEL_CONFIG,
        'status': 'ready'
    })

@app.route('/api/detect', methods=['POST'])
def detect():
    """
    检测端点
    接受上传的图像或视频
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取可选的置信度阈值
        conf = request.form.get('conf', MODEL_CONFIG['conf'], type=float)
        
        # 验证置信度范围
        if not 0 <= conf <= 1:
            return jsonify({'error': f'置信度必须在0-1之间, 当前值: {conf}'}), 400
        
        # 保存上传的文件
        temp_dir = 'temp_uploads'
        os.makedirs(temp_dir, exist_ok=True)
        
        upload_path = os.path.join(temp_dir, file.filename)
        file.save(upload_path)
        
        # 进行预测
        is_video = is_video_file(upload_path)
        results = predict_source(upload_path, conf=conf)

        if not results:
            os.remove(upload_path)
            return jsonify({'error': '预测失败'}), 500

        detections = []
        output_image_base64 = None
        frames_data = None

        if is_video:
            frames_data = []
            total_frames = len(results)
            sampled_indices = sample_frame_indices(total_frames)

            for frame_index, frame_result in enumerate(results):
                if frame_result is None:
                    continue

                if frame_index not in sampled_indices:
                    continue

                annotated_frame = frame_result.plot()
                if annotated_frame is None:
                    continue

                frame_image_b64 = encode_array_to_base64(annotated_frame)
                frame_detections = []
                if frame_result.boxes is not None:
                    for i, box in enumerate(frame_result.boxes):
                        bbox = box.xyxy[0].tolist() if box.xyxy is not None else []
                        detection = {
                            'frame': frame_index,
                            'id': i,
                            'class': int(box.cls[0]) if box.cls is not None else -1,
                            'confidence': float(box.conf[0]) if box.conf is not None else 0,
                            'bbox': bbox,
                            'area': float((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) if bbox else 0
                        }
                        frame_detections.append(detection)
                        detections.append(detection)

                frames_data.append({
                    'frame': frame_index,
                    'image': frame_image_b64,
                    'detections': frame_detections
                })

            if frames_data:
                output_image_base64 = frames_data[0]['image']
        else:
            result = results[0]
            if result is None:
                os.remove(upload_path)
                return jsonify({'error': '预测失败'}), 500

            if result.boxes is not None:
                for i, box in enumerate(result.boxes):
                    detection = {
                        'id': i,
                        'class': int(box.cls[0]) if box.cls is not None else -1,
                        'confidence': float(box.conf[0]) if box.conf is not None else 0,
                        'bbox': box.xyxy[0].tolist() if box.xyxy is not None else [],
                        'area': float((box.xyxy[0][2] - box.xyxy[0][0]) * (box.xyxy[0][3] - box.xyxy[0][1])) if box.xyxy is not None else 0
                    }
                    detections.append(detection)

            output_path = os.path.join(temp_dir, f'result_{file.filename}')
            draw_results(upload_path, result, output_path)
            output_image_base64 = encode_file_to_base64(output_path)

        # 清理临时文件
        os.remove(upload_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

        response_payload = {
            'success': True,
            'detections': detections,
            'detection_count': len(detections),
            'image': output_image_base64,
            'image_format': 'base64',
            'frames': frames_data,
            'frame_count': len(frames_data) if frames_data is not None else 0,
            'video_total_frames': total_frames if is_video else 0,
            'video_returned_frames': len(frames_data) if frames_data is not None else 0,
            'video_frame_sample_rate': max(1, total_frames // MAX_VIDEO_FRAMES) if is_video and total_frames else 1,
            'model_config': MODEL_CONFIG,
            'inference_config': {
                'conf': conf,
                'iou': MODEL_CONFIG['iou'],
                'imgsz': MODEL_CONFIG['imgsz'],
                'max_det': MODEL_CONFIG['max_det']
            }
        }

        return jsonify(response_payload)
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    try:
        load_model()
        return jsonify({'status': 'healthy', 'model_loaded': True})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("道路裂缝检测 - Web应用")
    print("=" * 60)
    print("\n模型配置参数:")
    print(json.dumps(MODEL_CONFIG, indent=2, ensure_ascii=False))
    print("\n启动Flask服务器...")
    print("访问: http://localhost:5000")
    print("=" * 60 + "\n")
    
    # 加载模型
    load_model()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)
