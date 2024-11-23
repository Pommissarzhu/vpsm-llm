import gradio as gr
from image_preprocess import resize_and_encoding
from parsing_menu import get_menu_text, write_menu_to_csv

def main_app(img):
    img_base64 = resize_and_encoding(img)
    menu_dict, menu_JSON = get_menu_text(img_base64)
    write_menu_to_csv(menu_dict)
    shop_name = menu_dict['shop_name']
    return shop_name, menu_JSON

main_ui = gr.Interface(fn=main_app,
             inputs=gr.Image(),
             outputs=[gr.Text(), gr.JSON()])
main_ui.launch()