import requests
from bs4 import BeautifulSoup
import os

# 在终端中输入目标网址
url = input("请输入要爬取的网页地址: ")

# 让用户输入指定的文件类型，以逗号分隔，如 .pdf,.jpg，直接回车则下载所有类型文件
file_types_input = input("请输入要下载的文件类型（以逗号分隔，如.pdf,.jpg，直接回车则下载所有类型文件）: ")
if file_types_input:
    target_file_types = [t.strip() for t in file_types_input.split(',')]
else:
    # 如果用户直接回车，设置为下载所有类型文件，这里用一个特殊标识表示
    target_file_types = ["ALL"]

# 发送请求获取网页内容
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找所有的<a>标签，因为文件链接一般在<a>标签的href属性里
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href:
            if target_file_types == ["ALL"] or any(href.endswith(file_type) for file_type in target_file_types):
                try:
                    file_response = requests.get(href)
                    if file_response.status_code == 200:
                        # 从链接中提取文件名
                        file_name = href.split('/')[-1]
                        # 创建保存文件的目录（如果不存在）
                        if not os.path.exists('downloads'):
                            os.makedirs('downloads')
                        file_path = os.path.join('downloads', file_name)
                        with open(file_path, 'wb') as f:
                            f.write(file_response.content)
                        print(f"已成功下载 {file_name}")
                except Exception as e:
                    print(f"下载 {href} 时出错: {e}")
else:
    print(f"请求失败，状态码: {response.status_code}")