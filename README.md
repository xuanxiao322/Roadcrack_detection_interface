# 道路裂缝检测Web应用

这是一个基于YOLOv8的道路裂缝检测Web系统，所有参数和配置与训练模型完全一致。

## 📋 功能特性

- ✅ 完全匹配模型训练配置（imgsz=640, iou=0.7, max_det=300）
- ✅ 支持上传JPG、PNG等图像格式
- ✅ 拖拽上传支持
- ✅ 实时参数调整（置信度阈值）
- ✅ 详细的检测结果显示
- ✅ 检测统计信息
- ✅ 响应式设计，支持多设备

## 🔧 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

### 3. 打开浏览器

访问: `http://localhost:5000`

## 📊 模型配置参数

所有参数与 `args.yaml` 完全一致：

| 参数 | 值 | 说明 |
|------|-----|------|
| **输入分辨率** | 640 | 图像被缩放到640×640 |
| **模型** | yolo26m.pt | 中等模型 |
| **IOU阈值** | 0.7 | NMS处理阈值 |
| **最大检测数** | 300 | 每张图最多检测300个目标 |
| **置信度** | 0.25 | 可调（页面提供滑块） |
| **优化器** | SGD | 训练优化器（推理不涉及） |
| **Augmentation** | False | 推理不使用数据增强 |
| **NMS** | 标准 | 按IOU进行非极大值抑制 |

## 🎯 关键参数映射

### 后端配置 (app.py)

```python
MODEL_CONFIG = {
    "model_path": "weights/best.pt",    # 最佳权重
    "imgsz": 640,                       # 与args.yaml一致
    "conf": 0.25,                       # 默认置信度
    "iou": 0.7,                         # NMS IOU阈值
    "max_det": 300,                     # 最大检测数
    "device": "0",                      # GPU设备
}
```

### 前端配置 (index.html)

```javascript
const CONFIG = {
    imgsz: 640,
    iou: 0.7,
    maxDet: 300,
    defaultConf: 0.25
};
```

## 📁 文件结构

```
my_model/
├── app.py                  # Flask后端应用
├── requirements.txt        # Python依赖
├── templates/
│   └── index.html         # 前端界面
├── weights/
│   ├── best.pt            # 最佳模型权重
│   └── last.pt            # 最后模型权重
├── args.yaml              # 模型训练配置
└── README.md              # 本文件
```

## 🚀 使用流程

1. **上传图像**：点击上传区域或拖拽图像
2. **调整参数**：使用置信度滑块调整检测灵敏度
3. **开始检测**：点击"开始检测"按钮
4. **查看结果**：
   - 右侧显示检测后的图像
   - 下方显示检测统计
   - 表格显示每个检测目标的详细信息

## 🎛️ 可调参数

- **置信度阈值（conf）**: 0-1之间，默认0.25
  - 值越小，检测目标越多（可能包含误检）
  - 值越大，检测目标越少（可能遗漏真实目标）
  
- **其他参数固定**：
  - IOU: 0.7（NMS处理用）
  - 分辨率: 640×640
  - 最大检测: 300个

## 📈 模型性能指标

根据 `results.csv` 的最终表现：

- **Precision**: ~0.8-0.85
- **Recall**: ~0.6-0.65
- **mAP50**: ~0.68-0.72
- **mAP50-95**: ~0.48-0.52

## ⚙️ 系统要求

- Python 3.8+
- CUDA 11.8+ (可选，有GPU时使用)
- 4GB+ RAM
- 2GB+ 可用磁盘空间（模型权重）

## 🐛 故障排查

### 问题：模型文件不存在
```
解决方案：确保 weights/best.pt 存在，或修改app.py中的model_path
```

### 问题：GPU内存不足
```
解决方案：在app.py中将device改为"cpu"
MODEL_CONFIG["device"] = "cpu"
```

### 问题：导入错误
```
解决方案：重新安装dependencies
pip install --upgrade -r requirements.txt
```

## 📝 API文档

### GET /api/config
获取模型配置信息
```json
{
  "model_config": {
    "imgsz": 640,
    "conf": 0.25,
    "iou": 0.7,
    "max_det": 300
  },
  "status": "ready"
}
```

### POST /api/detect
执行检测
参数：
- `file`: 上传的图像文件
- `conf`: 置信度阈值（可选，default=0.25）

返回：
```json
{
  "success": true,
  "detections": [
    {
      "id": 0,
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2],
      "area": 12345
    }
  ],
  "detection_count": 1,
  "image": "base64编码的结果图像",
  "model_config": {...}
}
```

### GET /api/health
健康检查
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## 📚 参考资源

- [YOLOv8 官方文档](https://docs.ultralytics.com/)
- [PyTorch 官方文档](https://pytorch.org/)
- [Flask 官方文档](https://flask.palletsprojects.com/)

## ⚖️ 许可证

仅供研究和教学使用。

## 👨‍💻 开发信息

- 框架：Flask + YOLOv8
- 前端：HTML5 + CSS3 + Vanilla JavaScript
- 后端：Python 3.8+
- 数据处理：OpenCV + NumPy + PIL

## 📞 支持

如遇到问题，请检查：
1. 所有依赖是否正确安装
2. 模型权重文件是否存在
3. GPU/CPU是否正确配置
4. 浏览器控制台是否有错误信息

---

**参数验证时间**: 2024年
**模型版本**: best.pt
**配置版本**: args.yaml （完全同步）
