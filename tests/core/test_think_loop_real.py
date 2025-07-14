import pytest
import os
from cogletnet import CogletNet
from dotenv import load_dotenv

def setup_cogletnet():
    load_dotenv()
    net = CogletNet(
        storage_config={
            "upstash_url": os.getenv("UPSTASH_URL"),
            "upstash_token": os.getenv("UPSTASH_TOKEN"),
            "set_id": "test_thinkloop"
        },
        llm_config={
            "model": "gpt-4o-mini",
            "max_retries": 3,
            "temperature": 0.7
        },
        memory_config={
            "beta": 0.85,
            "gamma": 0.3,
            "b": 0.05,
            "initial_weight": 0.5,
            "golden_ratio": 0.618,
            "top_k": 10
        },
        thinking_config={
            "max_cycles": 3
        },
        prompts_config={
            "role": "你是一个专业的认知分析系统，擅长从输入内容中提取关键信息并生成结构化的思考。你必须严格按照指定的JSON格式返回结果。",
            "format": (
                "你必须严格按照以下JSON格式返回结果：\n"
                "{\n"
                '  "next_thought": "下一轮思考内容",\n'
                '  "activated_cog_ids": ["实际使用到的认元序号"],\n'
                '  "log": "思考日志",\n'
                '  "generated_cog_texts": ["生成的认元文本列表"],\n'
                '  "function_calls": [{"name": "函数名", "args": {"参数名": "参数值"}}]\n'
                "}"
            ),
            "thinking": (
                "在思考过程中，请注意以下几点：\n"
                "1. 认元应当是基于输入内容的抽象性观点与模式总结\n"
                "2. 生成的认元文本应当简洁、清晰、具有普遍性\n"
                "3. 思考日志应当记录重要的推理过程和决策依据\n"
                "4. 函数调用应当明确具体，包含必要的参数\n"
                "5. 在activated_cog_ids中列出实际用于生成回答的认元ID\n"
                "6. 必须严格按照指定的JSON格式返回结果"
            ),
            "example": (
                """示例输入：'人工智能正在改变我们的生活方式'\n示例输出：\n{\n  "next_thought": "这种改变主要体现在哪些具体方面？",\n  "activated_cog_ids": [1, 2],\n  "log": "识别到技术变革主题，需要进一步探讨具体影响",\n  "generated_cog_texts": ["技术变革往往从日常生活开始", "AI的影响具有普遍性和深远性"],\n  "function_calls": []\n}\n"""
            )
        }
    )
    return net

def test_think_loop_real():
    net = setup_cogletnet()
    set_id = "test_thinkloop"
    # 清理集合，避免脏数据
    net.coglets.clean_set(set_id)
    # 初始化认元集合
    net.coglets.add(set_id, "人工智能正在改变医疗行业", {"weight": 0.8})
    net.coglets.add(set_id, "AI在教育领域的应用日益广泛", {"weight": 0.7})
    net.coglets.add(set_id, "AI带来的伦理挑战", {"weight": 0.6})
    net.coglets.add(set_id, "AI促进了自动化和生产力提升", {"weight": 0.9})

    # 输入一个开放性问题
    input_text = "人工智能对社会有哪些影响？"
    results = net.think_loop(input_text, set_id)

    # 断言至少有两轮思考
    assert len(results) >= 2
    # 检查每一轮输出结构
    for res in results:
        assert "next_thought" in res
        assert "activated_cog_ids" in res
        assert "log" in res
        assert "generated_cog_texts" in res
        assert isinstance(res["generated_cog_texts"], list)
    # 检查最后一轮next_thought为空或到达最大轮数
    assert results[-1]["next_thought"] == "" or len(results) == net.max_think_cycles 