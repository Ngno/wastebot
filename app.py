from http import HTTPStatus
from dashscope import Application, MultiModalConversation
from uploadthing_py import UTApi
import gradio as gr
import json
import asyncio, os


import dashscope
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
dashscope.api_key = api_key


title = """
<center>
<h1>Waste Management</h1>
</center>
"""


def visual_model(prompt, image):   
   
    image = "https://2.bp.blogspot.com/-kBhp7kSTUmI/Tq5YG6tWM8I/AAAAAAAAABw/BOfPCHKxYBQ/s1600/DSC_5706.JPG"

    messages = [
        {
            "role": "user",
            "content": [
                {"image": image},
                {"text":prompt}
            ]
        }
    ]
    response = MultiModalConversation.call(model='qwen-vl-max',
                                           messages=messages,
                                           stream=True)
    last_response = ''
    for res in response:
        last_response = res

    data = json.loads(str(last_response)) 
    return data['output']['choices'][0]['message']['content'][0]['text']

def llm_model(prompt):
    response = Application.call(app_id,
                                prompt=prompt,
                                api_key,)

    if response.status_code != HTTPStatus.OK:
        return response.message
    else:
        return response.output.text
    
#==================================================================

def chatbot(message, history):
    history_openai_format = []
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    history_openai_format.append({"role": "user", "content": message})

    llm_response = llm_model(message)
  
   
    return llm_response

with gr.Blocks() as wasteChat:
    gr.Markdown("## Waste Edu Chat")
    gr.ChatInterface(chatbot)
# ========================================================================

def process_input(image):
    message = "Kamu adalah pengempul sampah profesional. Sebutkan apa saja sampah yang ada didalam gambar tersebut dalam bentuk sebuah daftar"
    visual_response = visual_model(message, image)
    print(visual_response)
    prompt = f"Dari list sampah berikut {visual_response} berapakah harga masing-masing dalam Indonesia rupiah (Rp). Hasilkan hanya dalam bentuk list tanpda kalimat pembuka atau penutup dengan format list \n<nama sampah> \n - Harga Sampah : harga sampah \n - Rekomendasi Pengolahan Mandiri : rekomendasi"
    llm_response = llm_model(prompt)
    return llm_response

with gr.Blocks() as wasteAppraisal:   
    gr.Markdown("## Waste Appraisal")
    image_input = gr.Image()
            
    submit_btn = gr.Button("Submit")
    output = gr.Textbox(label="Result")
    
    submit_btn.click(
        fn=process_input,
        inputs=[image_input],
        outputs=output
    )

    gr.Markdown("")

#==================================================

with gr.Blocks() as fullApp:
    gr.HTML(title)
    gr.TabbedInterface([ wasteChat, wasteAppraisal], ["Chatbot","Appraisal"])

demo = fullApp

    
demo.launch(share=True)