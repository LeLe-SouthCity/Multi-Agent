import streamlit as st
import subprocess
import threading
import re
import queue

# 创建一个队列用于线程间通信
output_queue = queue.Queue()

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    # 定义正则表达式来匹配发言
    pattern = r"(Moderator|Player\d+): (.*)"
    matches = re.findall(pattern, output)

    # 检查matches是否为空
    if matches:
        # 遍历匹配结果，提取发言，并将其放入队列中
        for label, message in matches:
            output_queue.put({'label': label, 'message': message.strip()})

# 处理命令行输出，并实时更新Streamlit界面
def handle_command_output(proc):
    for line in iter(proc.stdout.readline, ''):
        print("DEBUG: Received line:", line)  # 添加调试打印
        parse_and_save_output(line)
    proc.stdout.close()

# 启动werewolf.py脚本并处理输出
def start_werewolf_script():
    # 定义要执行的命令
    command = ["python", "werewolf.py"]
    # 使用Popen启动子进程
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    # 创建一个线程来处理输出，以免阻塞主线程
    thread = threading.Thread(target=handle_command_output, args=(proc,))
    thread.start()

# 在Streamlit界面上添加一个按钮来启动脚本
if st.button('Start Werewolf Script'):
    start_werewolf_script()

# 显示聊天历史
def display_history():
    # 检查队列中是否有新消息
    while not output_queue.empty():
        message = output_queue.get()
        with st.chat_message(message["label"]):
            st.markdown(message["message"])

# 使用 Streamlit 的空容器来持续显示聊天历史
chat_history_container = st.empty()

# 使用 Streamlit 的按钮或其他触发器来定期刷新聊天历史
if st.button('Refresh Chat History'):
    display_history()
