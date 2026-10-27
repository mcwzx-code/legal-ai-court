import asyncio
import os
from openai import AsyncOpenAI

# ================= 第1步：只在这里填入你的 API Key =================
DEEPSEEK_API_KEY ="*************************************************************"
KIMI_API_KEY ="*************************************************************"
GLM_API_KEY ="******************************************************************"
# ====================================================================

# 下面别动
clients = {
    "prosecutor": AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1"),
    "defender": AsyncOpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.cn/v1"),
    "judge": AsyncOpenAI(api_key=GLM_API_KEY, base_url="https://open.bigmodel.cn/api/paas/v4/"),
}

MODEL_MAP = {
    "prosecutor": "deepseek-chat",
    "defender": "kimi-k3",                    
    "judge": "glm-4",              # 这里改成了智谱通用的模型名，更稳
}

SYSTEM_PROMPTS = {
    "prosecutor": "你是一位经验丰富的控方检察官，逻辑严密，善于从案卷中提取对己方有利的事实和证据，对辩方的反驳进行精准打击。",
    "defender": "你是一位资深的辩护律师，思维敏捷，善于从控方证据中寻找程序瑕疵和逻辑漏洞，为当事人争取最大权益。",
    "judge": "你是一位中立公正的法官，负责听取控辩双方发言，归纳争议焦点，控制庭审节奏，不偏向任何一方。",
}

async def call_role(role: str, system_prompt: str, case_context: str, history: list) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": "user", "content": h})
    messages.append({"role": "user", "content": f"案卷：{case_context}\n请基于以上信息，输出你的发言。"})
    
    try:
        resp = await clients[role].chat.completions.create(
            model=MODEL_MAP[role],
            messages=messages,
            temperature=1,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"调用失败，错误信息: {e}"

async def main():
    case_context = "张三因涉嫌故意伤害罪被提起公诉。控方指控张三在2025年3月15日晚与李四发生争执，用木棍将李四手臂打断，构成轻伤。辩方主张张三系正当防卫，李四先动手。"
    
    history_p, history_d, history_j = [], [], []
    
    for round_num in range(5):
        print(f"\n{'='*20} 第 {round_num + 1} 轮 {'='*20}")
        
        p_speech, d_speech = await asyncio.gather(
            call_role("prosecutor", SYSTEM_PROMPTS["prosecutor"], case_context, history_p),
            call_role("defender", SYSTEM_PROMPTS["defender"], case_context, history_d),
        )
        
        print(f"\n【控方】\n{p_speech}")
        print(f"\n【辩方】\n{d_speech}")
        
        judge_summary = await call_role("judge", SYSTEM_PROMPTS["judge"], case_context, history_j)
        print(f"\n【法官】\n{judge_summary}")
        
        history_p.append(f"控方：{p_speech}\n辩方：{d_speech}\n法官：{judge_summary}")
        history_d.append(f"控方：{p_speech}\n辩方：{d_speech}\n法官：{judge_summary}")
        history_j.append(f"控方：{p_speech}\n辩方：{d_speech}\n法官：{judge_summary}")
        
        lawyer_input = input("\n>>> 律师插话（直接回车跳过）：")
        if lawyer_input.strip() != "":
            history_p.append(f"律师介入：{lawyer_input}")
            history_d.append(f"律师介入：{lawyer_input}")
            history_j.append(f"律师介入：{lawyer_input}")
            print(f"已记录律师意见：{lawyer_input}")

if __name__ == "__main__":
    asyncio.run(main())
