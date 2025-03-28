import cv2
import base64

def resize_and_encoding(img):
    # 防止处理过小的图片
    MIN_PIXELS = 100*100
    if img.size < MIN_PIXELS:
        raise ValueError("图片分辨率过低")

    # 获取原始图片的宽和高
    height, width = img.shape[:2]

    # 计算缩放比例，使得像素点总数不超过921600
    max_pixels = 2073600
    scale = min(1.0, (max_pixels / (width * height)) ** 0.5)

    # 计算新的宽高
    new_width = int(width * scale)
    new_height = int(height * scale)

    # 调整图片大小
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # 将 BGR 转换为 RGB
    rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

    # 将图片编码为JPEG格式，图像质量为75%
    _, buffer = cv2.imencode('.jpg', rgb_img, [cv2.IMWRITE_JPEG_QUALITY, 75])

    # 将编码后的图片转换为base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return img_base64