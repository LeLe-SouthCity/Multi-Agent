import streamlit as st
import subprocess
import threading
import re
import queue
import time

# 创建一个队列用于线程间通信
output_queue = queue.Queue()

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    # 定义正则表达式来匹配发言
    pattern = r"Player(\d+): (.*)"
    matches = re.findall(pattern, output)

    # 检查matches是否为空
    if matches:
        # 遍历匹配结果，提取发言，并将其放入队列中
        for label, message in matches:
            output_queue.put({'label': f'Player{label}', 'message': message.strip()})
            print(f"'label': Player{label}, 'message': {message.strip()}")

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

# 启动一个后台线程来更新聊天历史
def update_chat_history():
    while True:
        if not output_queue.empty():
            with chat_history_container.container():
                # 清空之前的内容
                chat_history_container.empty()
                # 显示所有消息
                while not output_queue.empty():
                    message = output_queue.get()
                    with st.chat_message(message["label"]):
                        st.markdown(message["message"])
        # 等待一段时间再次检查队列
        time.sleep(1)

# 如果后台线程还没有启动，就启动它
if 'chat_update_thread' not in st.session_state:
    st.session_state.chat_update_thread = threading.Thread(target=update_chat_history, daemon=True)
    st.session_state.chat_update_thread.start()

# 创建一个持续更新的占位符
chat_history_container = st.empty()
