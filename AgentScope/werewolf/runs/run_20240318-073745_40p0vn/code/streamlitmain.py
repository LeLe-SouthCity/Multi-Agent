import streamlit as st
import subprocess
import threading
import re

# 初始化会话状态中的聊天历史记录列表
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 创建一个可更新的聊天历史区域
chat_history_container = st.empty()

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    pattern = r"Player(\d+): (.*)"
    matches = re.findall(pattern, output)
    if matches:
        for label, message in matches:
            st.session_state.chat_history.append({'label': f'Player{label}', 'message': message.strip()})
            # 更新聊天历史显示
            display_chat_history()

# 处理命令行输出
def handle_command_output(proc):
    for line in iter(proc.stdout.readline, ''):
        parse_and_save_output(line)
    proc.stdout.close()

# 启动werewolf.py脚本并处理输出
def start_werewolf_script():
    command = ["python", "werewolf.py"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    thread = threading.Thread(target=handle_command_output, args=(proc,))
    thread.start()

# 定义一个函数来显示聊天历史
def display_chat_history():
    with chat_history_container.container():
        for message in st.session_state.chat_history:
            st.text(f"{message['label']}: {message['message']}")

# 在Streamlit界面上添加一个按钮来启动脚本
if st.button('Start Werewolf Script'):
    start_werewolf_script()
