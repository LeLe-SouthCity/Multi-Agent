import streamlit as st
import subprocess
import threading
import re

# 创建一个列表用于保存聊天记录
chat_history = []

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    # 定义正则表达式来匹配发言
    pattern = r"Player(\d+): (.*)"
    matches = re.findall(pattern, output)

    # 检查matches是否为空
    if matches:
        # 遍历匹配结果，提取发言，并将其保存到列表中
        for label, message in matches:
            chat_history.append({'label': f'Player{label}', 'message': message.strip()})
            print(f"'label': Player{label}, 'message': {message.strip()}")
            display_history()

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
    # 使用 Streamlit 的 container 和 expander 来显示聊天历史
    with st.container():
        for message in chat_history:
            with st.expander(f"{message['label']} says:", expanded=True):
                st.write(message['message'])

# 使用 Streamlit 的按钮或其他触发器来定期刷新聊天历史
# if st.button('Refresh Chat History'):
#     display_history()
