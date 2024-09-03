# coding: utf-8
import os

from flask import Flask, request, render_template, jsonify
import base64
import requests
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('jianli3.html')


# 定义文件上传的路由
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('./uploads/' + file.filename)

    return '文件上传成功'


@app.route('/analyze', methods=['POST'])
def analyze_resume():
    directory = "./uploads"  # 指定目录路径

    file_list = []
    for root, dirs, files in os.walk(directory):  # 遍历目录
        for file in files:
            file_path = os.path.join(root, file)  # 获取文件路径
            file_path = file_path.replace("\\", "/")  # 将反斜杠替换为斜杠
            file_list.append(file_path)

    print(file_list)

    url = 'http://resumesdk.market.alicloudapi.com/ResumeParser'
    fname = file_list[0]
    # TODO: 遍历uploads 解析多个简历 加数据库
    print(fname)
    res_js=test_parse(url, fname)
    print(res_js)

    # 将 res_js 保存为 JSON 文件
    with open('res_js.json', 'w', encoding='utf-8') as f:
        json.dump(res_js, f, ensure_ascii=False)

    return jsonify(res_js)


def test_parse(url, fname):
    # 读取文件内容
    cont = open(fname, 'rb').read()
    base_cont = base64.b64encode(cont).decode('utf8')  # python3

    # 构造json请求
    data = {
        'file_name': fname,  # 简历文件名（需包含正确的后缀名）
        'file_cont': base_cont,  # 简历内容（base64编码的简历内容）
        'need_avatar': 0,  # 是否需要提取头像图片
        'ocr_type': 1,  # 1为高级ocr
    }

    appcode = 'a1f8f5075ea44bd19c7cb1c4d8c8dd24'
    headers = {'Authorization': 'APPCODE ' + appcode,
               'Content-Type': 'application/json; charset=UTF-8',
               }
    # 发送请求
    data_js = json.dumps(data)
    res = requests.post(url=url, data=data_js, headers=headers)

    # 解析结果
    res_js = json.loads(res.text)
    print(json.dumps(res_js, indent=4, ensure_ascii=False))  # 打印全部结果

    # 要删除的目录路径
    directory_path = "./uploads"

    # 遍历目录下的文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # 判断是否为文件
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"已删除文件: {file_path}")

    return res_js


if __name__ == '__main__':

    app.run()
