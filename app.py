import gradio as gr
from image_preprocess import resize_and_encoding
from parsing_menu import get_menu_text, write_menu_to_csv


def main_app(img):
    img_base64 = resize_and_encoding(img)
    menu_dict, menu_JSON = get_menu_text(img_base64)
    # write_menu_to_csv(menu_dict)
    shop_name = menu_dict['shop_name']
    menu = menu_dict['menu']
    # 转换菜单格式，以便在 Dataframe 中显示
    menu_list = [[item['dish'], item['price']] for item in menu]
    return shop_name, menu_list

# def submit_changes(shop_name, menu_list, floor):
#     # 将用户编辑后的菜单重新转换为字典格式

#     updated_menu = {'shop_name': shop_name, 'floor': floor, 'menu': [ {'dish': item[0], 'price': item[1]} for item in menu_list.itertuples(index=False)]}

#     write_menu_to_csv(updated_menu)
#     # 处理提交的数据（例如保存到文件或数据库中）
#     print("Updated Shop Name:", shop_name)
#     print("Updated Menu:", updated_menu)
#     return f"Data for '{shop_name}' submitted successfully!"

def submit_changes(shop_name, menu_list, floor):
    """提交用户编辑后的菜单数据，包含严格价格校验"""
    try:
        # 参数基础校验
        if not shop_name.strip():
            raise gr.Error("店铺名称不能为空")
        if not isinstance(menu_list, (list, pd.DataFrame)):
            raise gr.Error("菜单格式异常，请重新解析图片")
        # 转换数据格式并校验价格
        validated_menu = []
        for idx, item in enumerate(menu_list.itertuples(index=False), 1):
            dish = str(item[0]).strip()
            price_str = str(item[1]).strip()
            # 菜品名称校验
            if not dish:
                raise gr.Error(f"第 {idx} 行：菜品名称不能为空")
            # 价格校验
            if not price_str:
                raise gr.Error(f"第 {idx} 行：价格不能为空")
            try:
                price = float(price_str)
                if price <= 0:
                    raise gr.Error(f"第 {idx} 行：价格必须大于零 ({price_str})")
                if price > 1000:  # 设置合理上限
                    raise gr.Error(f"第 {idx} 行：价格异常偏高 ({price_str})")
            except ValueError:
                raise gr.Error(f"第 {idx} 行：无效价格格式 '{price_str}'")
            
            validated_menu.append({ 'dish': dish, 'price': price })
        # 构建数据结构
        updated_menu = {
            'shop_name': shop_name.strip(),
            'floor': floor,
            'menu': validated_menu
        }
        # 写入CSV
        write_menu_to_csv(updated_menu)
        # 返回成功状态
        return f"'{shop_name}' 数据提交成功！已保存 {len(validated_menu)} 个菜品"
        
    except gr.Error as e:
        # 将错误直接抛给前端显示
        raise e
    except Exception as e:
        # 捕获未预期的异常
        raise gr.Error(f"系统错误：{str(e)}")

with gr.Blocks() as demo:
    # 上传图片并获取初始数据
    img_input = gr.Image(label="Upload Menu Image")
    floor_input = gr.Radio(['1', '2', '3'], label="Floor")
    shop_name_output = gr.Textbox(label="Shop Name")
    menu_output = gr.Dataframe(headers=["Dish", "Price"], label="Menu", datatype=["str", "number"])

    # 提交按钮和输出结果
    submit_button = gr.Button("Submit Changes")
    submit_output = gr.Textbox(label="Submission Status", interactive=False)

    # 获取初始数据按钮
    main_ui_btn = gr.Button("Get Initial Data")
    main_ui_btn.click(main_app, inputs=img_input, outputs=[shop_name_output, menu_output])

    # 处理提交内容
    submit_button.click(submit_changes, inputs=[shop_name_output, menu_output, floor_input], outputs=submit_output)

demo.launch()
