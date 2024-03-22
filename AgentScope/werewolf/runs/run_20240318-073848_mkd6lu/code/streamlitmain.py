import streamlit as st
import time
import subprocess
import re

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
    return matches

# 启动werewolf.py脚本并处理输出
def start_werewolf_script():
    command = ["python", "werewolf.py"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    return proc

# 显示聊天历史
def display_chat_history():
    for message in st.session_state.chat_history:
        st.text(f"{message['label']}: {message['message']}")

# 在Streamlit界面上添加一个按钮来启动脚本
if 'proc' not in st.session_state or st.session_state.proc.poll() is not None:
    if st.button('Start Werewolf Script'):
        st.session_state.proc = start_werewolf_script()

# 定期刷新聊天历史
if 'proc' in st.session_state and st.session_state.proc.poll() is None:
    output = st.session_state.proc.stdout.readline()
    if parse_and_save_output(output):
        display_chat_history()
        time.sleep(1)  # 等待一秒钟以减少刷新频率
        st.experimental_rerun()  # 重新运行应用以更新显示
