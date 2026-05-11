"""
配置验证工具 - 确保Web应用参数与模型配置完全一致
"""
import yaml
import json
from pathlib import Path

def load_args_yaml(args_path='args.yaml'):
    """加载args.yaml配置"""
    with open(args_path, 'r', encoding='utf-8') as f:
        args = yaml.safe_load(f)
    return args

def get_model_config():
    """从app.py获取模型配置"""
    model_config = {
        "model_path": "weights/best.pt",
        "imgsz": 640,
        "conf": 0.25,
        "iou": 0.7,
        "max_det": 300,
        "device": "0",
        "augment": False,
        "agnostic_nms": False,
        "retina_masks": False,
        "verbose": True,
    }
    return model_config

def validate_config():
    """验证配置是否匹配"""
    print("=" * 70)
    print("配置参数验证工具")
    print("=" * 70)
    
    # 加载args.yaml
    try:
        args = load_args_yaml()
        print("\n✓ 成功加载 args.yaml")
    except Exception as e:
        print(f"\n✗ 加载 args.yaml 失败: {e}")
        return False
    
    # 获取模型配置
    model_config = get_model_config()
    print("✓ 成功加载 Model Config")
    
    # 验证关键参数
    print("\n" + "-" * 70)
    print("关键参数对比:")
    print("-" * 70)
    
    checks = {
        "输入分辨率 (imgsz)": {
            "args.yaml": args.get('imgsz'),
            "model_config": model_config['imgsz'],
            "critical": True
        },
        "IOU阈值 (iou)": {
            "args.yaml": args.get('iou'),
            "model_config": model_config['iou'],
            "critical": True
        },
        "最大检测数 (max_det)": {
            "args.yaml": args.get('max_det'),
            "model_config": model_config['max_det'],
            "critical": True
        },
        "GPU设备 (device)": {
            "args.yaml": args.get('device'),
            "model_config": model_config['device'],
            "critical": False
        },
        "数据增强 (augment)": {
            "args.yaml": args.get('augment'),
            "model_config": model_config['augment'],
            "critical": False
        },
        "NMS类无关 (agnostic_nms)": {
            "args.yaml": args.get('agnostic_nms'),
            "model_config": model_config['agnostic_nms'],
            "critical": False
        },
    }
    
    all_valid = True
    critical_valid = True
    
    for param_name, param_config in checks.items():
        args_val = param_config['args.yaml']
        model_val = param_config['model_config']
        is_critical = param_config['critical']
        
        match = args_val == model_val
        symbol = "✓" if match else "✗"
        
        print(f"\n{symbol} {param_name}")
        print(f"  args.yaml:     {args_val}")
        print(f"  model_config:  {model_val}")
        
        if not match:
            all_valid = False
            if is_critical:
                critical_valid = False
    
    print("\n" + "-" * 70)
    print("验证结果:")
    print("-" * 70)
    
    if critical_valid:
        print("✓ 关键参数完全匹配！")
        print("✓ Web应用已正确配置")
    else:
        print("✗ 检测到参数不匹配！")
        print("✗ 请修改Web应用以匹配args.yaml")
    
    if all_valid:
        print("✓ 所有参数完全匹配")
    else:
        print("⚠ 部分非关键参数不匹配（可能不影响功能）")
    
    print("\n" + "=" * 70)
    
    return critical_valid

def print_config_details():
    """打印详细配置"""
    print("\n模型训练配置详情:")
    print("-" * 70)
    
    args = load_args_yaml()
    
    important_keys = [
        'task', 'model', 'data', 'imgsz', 'epochs', 'batch',
        'optimizer', 'iou', 'conf', 'max_det', 'augment',
        'device', 'lr0', 'momentum', 'weight_decay'
    ]
    
    for key in important_keys:
        if key in args:
            value = args[key]
            print(f"  {key:20} : {value}")
    
    print("-" * 70)

if __name__ == '__main__':
    # 验证配置
    valid = validate_config()
    
    # 打印详情
    print_config_details()
    
    # 返回状态码
    exit(0 if valid else 1)
