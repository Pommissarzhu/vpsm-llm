from openai import OpenAI
from IPython.display import Image, display, Audio, Markdown
import base64
import json
import pandas as pd


IMG_PATH = "hb.jpg"
display(Image(IMG_PATH))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(IMG_PATH)


with open("api_key_config", "r", encoding="utf-8") as file:
    api_key = file.read()

MODEL = "qwen-vl-max"

client = OpenAI(api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你将收到一张或多张图片，这些图片对应着一个店铺及其菜单，你的任务是识别并告诉用户店铺的名字是什么以及有哪些菜和对应的价格，并以json的形式返回，其中价格只需返回数字即可，不需要加单位，例如：{'shop_name': '陕味食族', 'menu': [{'dish': '西红柿鸡蛋面', 'price': 8}, {'dish': '肉块鸡汤面', 'price': 12}, {'dish': '香菇鸡块面', 'price': 12}, {'dish': '酸菜牛肉面', 'price': 14}, {'dish': '红烧牛肉面', 'price': 14}, {'dish': '老陕油泼面', 'price': 8}, {'dish': '炸酱面', 'price': 10}, {'dish': '火爆剁椒面', 'price': 11}, {'dish': '瘦肉干拌面', 'price': 12}, {'dish': '双味二合一', 'price': 12}, {'dish': '网红爆肚面', 'price': 14}]}"},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpg;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.0,
)

# print(response.choices[0].message.content)

target = response.choices[0].message.content[7:-3]
print(target)

target = target.strip()  # 去除字符串首尾空白字符

try:
    finalStr = json.loads(target)
except json.JSONDecodeError as e:
    print("JSON 解析错误:", e)
    finalStr = None

# 确保 finalStr 是一个字典
if isinstance(finalStr, dict) and 'menu' in finalStr:
    rows = []
    for item in finalStr['menu']:
        rows.append({'shop': finalStr['shop_name'], 'dish': item['dish'], 'price': item['price']})

    df_new = pd.DataFrame(rows)

    # 将新数据追加到 CSV 文件中，指定编码为 utf-8-sig
    csv_file = 'output.csv'
    try:
        # 如果文件存在则追加数据，否则创建文件
        df_existing = pd.read_csv(csv_file, encoding='utf-8')
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(csv_file, index=False, encoding='utf-8')
    except FileNotFoundError:
        df_new.to_csv(csv_file, index=False, encoding='utf-8')

    print("数据已成功追加到 output.csv")
else:
    print("finalStr 不是有效的字典或者不包含 'menu' 键")