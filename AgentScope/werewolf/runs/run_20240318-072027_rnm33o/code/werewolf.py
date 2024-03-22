# -*- coding: utf-8 -*-
"""A werewolf game implemented by agentscope."""
from functools import partial

from prompt import Prompts
from werewolf_utils import (
    check_winning,
    update_alive_players,
    majority_vote,
    extract_name_and_id,
    n2s,
)
from agentscope.message import Msg
from agentscope.msghub import msghub
from agentscope.pipelines.functional import sequentialpipeline
import agentscope


# pylint: disable=too-many-statements
def main() -> None:
    """werewolf game"""
    # default settings 主持人类获取
    HostMsg = partial(Msg, name="Moderator", echo=True)
    # 女巫的治疗 ，毒药 默认设置
    healing, poison = True, True
    # 狼人的讨论轮数
    MAX_WEREWOLF_DISCUSSION_ROUND = 2
    # 最大游戏轮数
    MAX_GAME_ROUND = 11
    # read model and agent configs, and initialize agents automatically 从文件读取参数，并初始化
    survivors = agentscope.init(
        model_configs="./configs/model_configs.json",
        agent_configs="./configs/agent_configs.json",
    )
    #角色设定
    roles = ["werewolf", "werewolf", "villager", "villager", "seer", "witch"]
    
    #agents的 分配
    wolves, witch, seer = survivors[:2], survivors[-1], survivors[-2]

    # 开始游戏
    for _ in range(1, MAX_GAME_ROUND + 1):
        # night phase, werewolves discuss 夜晚狼人的讨论 （记忆存储在狼人部分）
        hint = HostMsg(content=Prompts.to_wolves.format(n2s(wolves)))
        # 狼人之间进行代理prompt记忆共享 
        with msghub(wolves, announcement=hint) as hub:
            for _ in range(MAX_WEREWOLF_DISCUSSION_ROUND):
                x = sequentialpipeline(wolves)
                if x.get("agreement", False):
                    break

            # werewolves vote 
            hint = HostMsg(content=Prompts.to_wolves_vote)
            votes = [
                # 从字符串中提取所有狼人玩家的 姓名和 ID
                extract_name_and_id(wolf(hint).content)[0] for wolf in wolves
            ]
            # broadcast the result to werewolves
            # 投票函数 狼人之间进行投票
            dead_player = [majority_vote(votes)]
            # 广播狼人玩家 要杀死的角色
            hub.broadcast(
                HostMsg(content=Prompts.to_wolves_res.format(dead_player[0])),
            )

        # witch 女巫玩家
        # 治疗默认未使用
        healing_used_tonight = False
        # 如果女巫在幸存者中
        if witch in survivors:
            # 还有治疗
            if healing:
                hint = HostMsg(
                     #使用 预制的prompt 
                    content=Prompts.to_witch_resurrect.format_map(
                        {
                            "witch_name": witch.name,
                            "dead_name": dead_player[0],
                        },
                    ),
                )
                # # 给代理传递 prompt 并检索相关内容 如果未使用复活
                if witch(hint).get("resurrect", False):
                    # 今晚使用了治疗
                    healing_used_tonight = True
                    #死亡角色出栈
                    dead_player.pop()
                    # 治疗已使用
                    healing = False
            #如果毒药未使用 并且今晚没有治疗
            if poison and not healing_used_tonight:
                #使用 预制的prompt 
                x = witch(HostMsg(content=Prompts.to_witch_poison))
                if x.get("eliminate", False):
                    dead_player.append(extract_name_and_id(x.content)[0])
                    poison = False

        # seer 预言家部分
        if seer in survivors:
            #使用 预制的prompt 
            hint = HostMsg(
                content=Prompts.to_seer.format(seer.name, n2s(survivors)),
            )
            # 给代理传递 prompt
            x = seer(hint)
            # 使用方法 获取信息
            player, idx = extract_name_and_id(x.content)
            #   非狼即好人
            role = "werewolf" if roles[idx] == "werewolf" else "villager"
            # 
            hint = HostMsg(content=Prompts.to_seer_result.format(player, role))
            seer.observe(hint)
        
        # 更新存活人数
        survivors, wolves = update_alive_players(
            survivors,
            wolves,
            dead_player,
        )
        # 检查游戏是否结束
        if check_winning(survivors, wolves, "Moderator"):
            break

        # daytime discussion 白天的讨论时间
        content = (
            Prompts.to_all_danger.format(n2s(dead_player))
            if dead_player
            else Prompts.to_all_peace
        )
        # 使用预制的prompt 让所有玩家发言
        hints = [
            HostMsg(content=content),
            HostMsg(content=Prompts.to_all_discuss.format(n2s(survivors))),
        ]
        # 为所有存活者 共享发言
        with msghub(survivors, announcement=hints) as hub:
            # discuss 玩家之间进行讨论
            x = sequentialpipeline(survivors)

            # vote 选举
            hint = HostMsg(content=Prompts.to_all_vote.format(n2s(survivors)))
            #提取取每个幸存者的投票人
            votes = [
                extract_name_and_id(_(hint).content)[0] for _ in survivors
            ]
            #计算投票数
            vote_res = majority_vote(votes)
            # broadcast the result to all players
            result = HostMsg(content=Prompts.to_all_res.format(vote_res))
            hub.broadcast(result)
            #幸存者更新
            survivors, wolves = update_alive_players(
                survivors,
                wolves,
                vote_res,
            )
            #检查游戏是否胜利
            if check_winning(survivors, wolves, "Moderator"):
                break
            # 对所有新幸存者更新promtp
            hub.broadcast(HostMsg(content=Prompts.to_all_continue))


if __name__ == "__main__":
    main()
