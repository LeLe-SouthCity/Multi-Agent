import streamlit as st
import subprocess
import re

# 初始化会话状态中的聊天历史记录列表
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 解析命令行输出并提取发言
def parse_and_save_output(output):
    player_pattern = r"Player(\d+): (.*)"
    moderator_pattern = r"Moderator: (.*)"
    player_matches = re.findall(player_pattern, output)
    moderator_matches = re.findall(moderator_pattern, output)
    
    # 保存玩家的发言
    for label, message in player_matches:
        st.session_state.chat_history.append({'label': f'Player{label}', 'message': message.strip()})
    
    # 保存主持人的发言
    for message in moderator_matches:
        st.session_state.chat_history.append({'label': 'Moderator', 'message': message.strip()})

    # 如果有任何匹配，返回 True
    return bool(player_matches or moderator_matches)

# 启动 werewolf.py 脚本并处理输出
def start_werewolf_script():
    command = ["python", "werewolf.py"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    return proc

# 显示聊天历史
def display_chat_history():
    for message in st.session_state.chat_history:
        with st.container():
            st.markdown(f"**{message['label']}:** {message['message']}")

# 在 Streamlit 界面上添加一个按钮来启动脚本
if st.button('Start Werewolf Script'):
    st.session_state.proc = start_werewolf_script()

# 定期刷新聊天历史
if 'proc' in st.session_state:
    proc = st.session_state.get('proc')
    if proc and proc.poll() is None:
        output = proc.stdout.readline()
        if output:
            if parse_and_save_output(output):
                display_chat_history()
        else:
            # 当没有输出时（脚本可能已结束），我们结束脚本并清除进程状态
            proc.terminate()
            st.session_state.proc = None
        # 使用 Streamlit 的机制，定期重新运行脚本
        st.rerun()
    else:
        # 如果进程不存在或已结束，显示聊天历史
        display_chat_history()
