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

def submit_changes(shop_name, menu_list, floor):
    # 将用户编辑后的菜单重新转换为字典格式

    updated_menu = {'shop_name': shop_name, 'floor': floor, 'menu': [ {'dish': item[0], 'price': item[1]} for item in menu_list.itertuples(index=False)]}

    write_menu_to_csv(updated_menu)
    # 处理提交的数据（例如保存到文件或数据库中）
    print("Updated Shop Name:", shop_name)
    print("Updated Menu:", updated_menu)
    return f"Data for '{shop_name}' submitted successfully!"

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
