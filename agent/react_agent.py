from agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch
from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize,get_target_shop,get_time_range,fetch_operation_alerts,
fetch_sales_metrics,fetch_transaction_summary,fetch_supply_chain_topology,fetch_report_data,fill_context_for_report)
import time

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt = load_system_prompts(),
            tools = [rag_summarize,get_target_shop,get_time_range,fetch_operation_alerts,
            fetch_sales_metrics,fetch_transaction_summary,fetch_supply_chain_topology,
            fetch_report_data,fill_context_for_report],
            middleware = [monitor_tool,log_before_model,report_prompt_switch]
        )
    def _extract_text(self, result) -> str:
        """
        从模型返回的结果中提取文本内容。
        """
        if isinstance(result, dict):
            messages = result.get("messages", [])
            if messages:
                last = messages[-1]
                content = getattr(last, "content", "") # 提取最后一个消息的内容
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("text"):
                            texts.append(block["text"])
                    return "".join(texts)
        return str(result)

    def execute_stream(self, query: str):
        """
        执行流式查询，返回模型的流式输出。
        """
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        # 非流式调用，先拿完整结果
        result = self.agent.invoke(
            input_dict,
            context={"report": False}
        )

        final_text = self._extract_text(result)

        # 伪流式：按固定长度切块输出
        chunk_size = 20
        for i in range(0, len(final_text), chunk_size):
            yield final_text[i:i + chunk_size]
            time.sleep(0.02)
        