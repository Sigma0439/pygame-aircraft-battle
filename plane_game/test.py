from PIL import Image
try:
    img = Image.open('fly.ico')
    print(f"格式: {img.format}")
    print(f"尺寸: {img.size}")
    print(f"模式: {img.mode}")
    # 尝试获取ICO文件中的所有尺寸
    if hasattr(img, 'n_frames') and img.n_frames > 1:
        print(f"这是一个多尺寸ICO，包含 {img.n_frames} 个图像。")
    else:
        print("⚠️ 警告：这可能是一个单尺寸ICO或非标准文件。")
except Exception as e:
    print(f"❌ 无法打开文件，文件可能已损坏或格式错误: {e}")