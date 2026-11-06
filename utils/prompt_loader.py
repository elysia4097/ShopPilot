from utils.config_handler import prompts_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def load_system_prompts():
    """
    加载系统提示词
    """
    try:
        system_prompt_path = get_abs_path(prompts_config["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置中未找到main_prompt_path键: {str(e)}")
        raise e
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]加载系统提示词失败: {str(e)}")
        raise e

def load_rag_prompts():
    """
    加载RAG提示词
    """
    try:
        rag_prompt_path = get_abs_path(prompts_config["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompts]在yaml配置中未找到rag_summarize_prompt_path键: {str(e)}")   
        raise e
    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()  
    except Exception as e:
        logger.error(f"[load_rag_prompts]加载RAG提示词失败: {str(e)}")
        raise e

def load_report_prompts():
    """
    加载报告提示词
    """
    try:
        report_prompt_path = get_abs_path(prompts_config["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompts]在yaml配置中未找到report_prompt_path键: {str(e)}")
        raise e
    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()   
    except Exception as e:
        logger.error(f"[load_report_prompts]加载报告提示词失败: {str(e)}")
        raise e


