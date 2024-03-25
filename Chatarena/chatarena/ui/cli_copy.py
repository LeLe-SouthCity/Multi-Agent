import gradio as gr
from ..arena import Arena, TooManyInvalidActions
from ..backends.human import HumanBackendError

class ArenaGUI:
    def __init__(self, arena: Arena):
        self.arena = arena
        self.console_output = ""
        self.max_steps = 5
        self.step_count = 0
        env = self.arena.environment
        players = self.arena.players

        env_desc = self.arena.global_prompt
        num_players = env.num_players
        self.console_output += f"Environment ({env.type_name}) description:\n{env_desc}\n"
        # 打印玩家名称、角色描述和后端类型
        for i, player in enumerate(players):
            self.console_output += f"[{player.name} ({player.backend.type_name})] Role Description:\n{player.role_desc}\n\n"
        self.console_output += "\n========= 我是卧底 走起! ==========\n"

    def step_arena(self, human_input):
        need_update_output = ""
        try:
            player_name = self.arena.environment.get_next_player()
            timestep = self.arena.step()
            for msg in timestep.observation:
                full_msg = msg.agent_name + " -> " + str(msg.visible_to) + " : " + msg.content + '\n'
                need_update_output += full_msg
            
            # last_message = timestep.observation[-1]
            # self.console_output = self.console_output + last_message.agent_name + " -> " + str(last_message.visible_to) + " : " + last_message.content + '\n'
        except HumanBackendError as e:
            human_player_name = self.arena.environment.get_next_player()
            timestep = self.arena.environment.step(human_player_name, human_input)
            last_message = human_input
            need_update_output = need_update_output + human_player_name + " : " + last_message + '\n'
        except TooManyInvalidActions as e:
            print(str(e))
            pass
        return self.console_output + need_update_output

    def launch(self):
        with gr.Blocks() as demo:
            gr.Markdown("### Ug多智能体《谁是卧底》")
            output_text = gr.Textbox(label="Console Output", lines=10, value="欢迎来到《谁是卧底》", readonly=True)
            input_text = gr.Textbox(label="")
            step_button = gr.Button("你敢点一次鸡哥马上打折你狗腿")

            step_button.click(fn=self.step_arena, inputs=input_text, outputs=output_text)

        demo.launch(share=True)

