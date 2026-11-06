from langchain.agents.middleware import wrap_tool_call,before_model,ModelRequest,dynamic_prompt
from langchain.agents import AgentState
from langchain.tools.tool_node import ToolCallRequest
from typing import Callable
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.runtime import Runtime
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompts,load_report_prompts

@wrap_tool_call
def monitor_tool(
    request:ToolCallRequest,#请求的数据封装
    handler:Callable[[ToolCallRequest],ToolMessage | Command],#执行的函数本身
) ->ToolMessage | Command:
    """
    工具执行的监控
    """
    logger.info(f"[monitor_tool]工具调用：{request.tool_call['name']}")
    logger.info(f"[monitor_tool]传入参数：{request.tool_call['args']}")
    try:
        result = handler(request)
        logger.info(f"[monitor_tool]工具调用成功：{request.tool_call['name']}")

        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"[monitor_tool]工具{request.tool_call['name']}调用异常：{str(e)}")
        raise 


@before_model
def log_before_model(
    state:AgentState, #整个智能体中的状态记录
    runtime:Runtime,  #记录了整个执行过程中的上下文信息
):
    """
    模型调用前输出日志
    """
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息")
    logger.debug(f"[log_before_model] {type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()} ")
    return None

@dynamic_prompt  #每次在生成提示词时调用此函数
def report_prompt_switch(request:ModelRequest):
    """
    动态切换提升词
    """
    is_request = request.runtime.context.get("report",False)  #拿不到report的值默认False
    if is_request:
        return load_report_prompts()   #是生成报告场景，加载报告提示词
    else:
        return load_system_prompts()   #不是生成报告场景，加载系统提示词
