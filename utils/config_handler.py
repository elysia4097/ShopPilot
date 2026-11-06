"""
yaml配置文件处理
"""
import yaml
from utils.path_tool import get_abs_path

def load_rag_config(config_path: str=get_abs_path("config/rag.yaml"),encoding: str="utf-8"):
    """
    加载rag配置文件
    :param config_path: 配置文件路径
    :param encoding: 编码方式
    :return: 配置文件内容(dict)
    """
    with open(config_path, encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)# 加载yaml文件

def load_chroma_config(config_path: str=get_abs_path("config/chroma.yaml"),encoding: str="utf-8"):
    with open(config_path, encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def load_prompts_config(config_path: str=get_abs_path("config/prompts.yaml"),encoding: str="utf-8"):
    with open(config_path, encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def load_agent_config(config_path: str=get_abs_path("config/agent.yaml"),encoding: str="utf-8"):
    with open(config_path, encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()


if __name__ == "__main__":
    print(rag_config)
    print(chroma_config)
    print(prompts_config)
    print(agent_config)