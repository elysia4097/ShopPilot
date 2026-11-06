import hashlib
import os
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

"""
文件处理工具, 包含文件md5计算, 文件夹遍历, 文件加载
"""

def get_file_md5_hex(file_path: str):
    """
    计算文件的md5值的十六进制字符串
    :param file_path: 文件路径
    :return: 文件的md5值的十六进制字符串
    """
    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件{file_path}不存在")
        return 
    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]文件{file_path}不是文件")
        return 

    md5_obj = hashlib.md5()
    chunk_size = 4096  #4KB分片，避免文件过大导致内存不足
    try:
        with open(file_path, "rb") as f:  #必须以二进制模式打开文件
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)  #更新md5对象
            md5_hex = md5_obj.hexdigest()  #获取md5值的十六进制字符串
            return md5_hex
    except Exception as e:
        logger.error(f"[md5计算]文件{file_path}计算md5值失败: {str(e)}")
        return None
    

def listdir_with_allowed_type(dir_path: str, allowed_types: tuple[str]):
    """
    获取文件夹所有指定类型的文件列表
    :param dir_path: 文件夹路径
    :param allowed_types: 允许的文件类型元组
    :return: 允许的文件路径元组
    """
    files = []
    if not os.path.isdir(dir_path):
        logger.error(f"[listdir_with_allowed_type]路径{dir_path}不是文件夹")
        return allowed_types
    for file in os.listdir(dir_path):
        if file.endswith(allowed_types):
            files.append(os.path.join(dir_path, file))
    return tuple(files)

def pdf_loader(file_path: str,passwd=None) -> list[Document]:
    """
    加载pdf文件
    :param file_path: pdf文件路径
    :param passwd: 密码，默认None
    :return: pdf文件内容列表
    """
    return PyPDFLoader(file_path, passwd).load()

def txt_loader(file_path: str) -> list[Document]:
    """
    加载txt文件
    :param file_path: txt文件路径
    :return: txt文件内容列表
    """
    return TextLoader(file_path,encoding="utf-8").load()
