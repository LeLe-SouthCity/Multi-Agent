import streamlit as st
import subprocess
import re
import threading

# 初始化会话状态中的聊天历史记录列表
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    pattern = r"Player(\d+): (.*)"
    matches = re.findall(pattern, output)
    if matches:
        for label, message in matches:
            st.session_state.chat_history.append({'label': f'Player{label}', 'message': message.strip()})

# 启动werewolf.py脚本并处理输出
def start_werewolf_script():
    command = ["python", "werewolf.py"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    return proc

# 显示聊天历史
def display_chat_history(chat_container):
    with chat_container:
        # 清空之前的内容
        chat_container.empty()
        # 显示聊天历史中的所有消息
        for message in st.session_state.chat_history:
            st.text(f"{message['label']}: {message['message']}")

# 创建一个空白的占位符用于聊天历史
chat_placeholder = st.empty()

# 在Streamlit界面上添加一个按钮来启动脚本
if 'proc' not in st.session_state or st.session_state.proc.poll() is not None:
    if st.button('Start Werewolf Script'):
        st.session_state.proc = start_werewolf_script()

# 用于更新聊天历史的函数
def update_chat_history():
    if 'proc' in st.session_state and st.session_state.proc.poll() is None:
        while True:
            output = st.session_state.proc.stdout.readline()
            if output == '' and st.session_state.proc.poll() is not None:
                break
            if output:
                parse_and_save_output(output.strip())
                display_chat_history(chat_placeholder)

# 线程用于读取输出，以免阻塞Streamlit的主线程
if 'thread' not in st.session_state or not st.session_state.thread.is_alive():
    st.session_state.thread = threading.Thread(target=update_chat_history, daemon=True)
    st.session_state.thread.start()
