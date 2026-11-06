"""
为整个工程提供统一的绝对路径获取, 包含项目根目录获取, 相对路径转绝对路径获取
"""
import os

def get_project_root():
    """
    获取项目根目录
    :return: 项目根目录
    """
    current_file = os.path.abspath(__file__)#获取当前文件的绝对路径
    current_dir = os.path.dirname(current_file)#获取当前文件所在目录
    project_root = os.path.dirname(current_dir)#获取项目根目录
    return project_root

def get_abs_path(relative_path) -> str:
    """
    传入相对路径，获取绝对路径
    :param relative_path: 相对路径
    :return: 绝对路径
    """
    project_root = get_project_root()
    abs_path = os.path.join(project_root, relative_path)
    return abs_path

