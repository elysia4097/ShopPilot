"""
日志记录器logger, 包含日志格式配置, 日志文件保存路径
"""
import datetime
import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

#日志保存的根目录
LOG_ROOT = get_abs_path("logs")

#确保日志根目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

#日志的格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
    name: str = "agent",
    console_level: int = logging.INFO,  # 只输出info级别以上的日志信息，避免debug垃圾信息
    file_level: int = logging.DEBUG,  # 文件日志级别，默认debug级别
    log_file: str = None,  # 日志文件名，默认根据时间戳生成
) -> logging.Logger:
    """
    获取日志记录器
    :param name: 日志记录器的名称
    :param console_level: 控制台日志级别
    :param file_level: 文件日志级别
    :param log_file: 日志文件名
    :return: 日志记录器
    """
    logger = logging.getLogger(name)  #创建日志记录器
    logger.setLevel(logging.DEBUG)  #设置日志级别，默认debug级别
    #避免重复添加Handler
    if logger.handlers:
        return logger   #如果日志记录器已经存在Handler，直接返回
    
    #添加控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)
    
    #添加文件Handler
    if not log_file:  #日志文件的存放路径
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    
    return logger

#快捷获取日志记录器
logger = get_logger()