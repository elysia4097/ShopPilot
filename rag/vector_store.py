from langchain_chroma import Chroma
from utils.config_handler import chroma_config
from model.factory import embedding_model, chat_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path
import os
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type,get_file_md5_hex
from utils.logger_handler import logger
from langchain_core.documents import Document

# 向量数据库服务类
class VectorStoreService:
    def __init__(self):
        """
        初始化向量数据库服务
        """
        self.vector_store = Chroma(     # 初始化向量数据库
            collection_name=chroma_config["collection_name"],
            embedding_function=embedding_model,# 向量模型函数
            persist_directory=chroma_config["persist_directory"],
        )
        # 文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],#分割后的文本段最大字符数
            chunk_overlap=chroma_config["chunk_overlap"],# 分割后的文本段最大重叠字符数
            length_function=len,# 文本分割器长度#使用python的len函数计算文本段的字符数
            separators=chroma_config["separators"],# 文本分割器分隔符
        )
    # 获取检索器
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})
    # 加载文档
    def load_documents(self):
       
        def check_md5_hex(md5_for_check: str):
            """
            检查md5值是否已存在知识库
            """
            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
               # 创建文件
               open(get_abs_path(chroma_config["md5_hex_store"]), "w", encoding="utf-8").close()
               return False  #md5没处理过

            with open(get_abs_path(chroma_config["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:  # strip()去掉字符串首尾的换行符
                        return True  #md5已处理过
                return False  #md5没处理过
                
        def save_md5_hex(md5_for_save: str):
            """
            保存md5值到文件
            """
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save + "\n")
        
        def get_file_documents(read_path: str):
            """
            从文件路径加载文档
            """
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            elif read_path.endswith(".txt"):
                return txt_loader(read_path)
            
            return []
        
        allow_files_path : list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]), 
            tuple(chroma_config["allow_knowledge_file_types"])
        )# 获取允许的文件路径列表

        for path in allow_files_path:
            #获取文件的md5值
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[load_documents]文件{path}已存在知识库，跳过")
                continue
            try:
                documents : list[Document] = get_file_documents(path)
                if not documents:
                    logger.warning(f"[load_documents]文件{path}无有效内容，跳过")
                    continue
                split_documents : list[Document] = self.splitter.split_documents(documents)

                if not split_documents:
                    logger.warning(f"[load_documents]文件{path}分割后无有效内容，跳过")
                    continue
                # 加载文档到向量数据库
                self.vector_store.add_documents(split_documents)
                # 保存md5值到文件
                save_md5_hex(md5_hex)
                logger.info(f"[load_documents]文件{path}加载成功")


            except Exception as e:
                #exc_info为true，打印详细异常信息
                logger.error(f"[load_documents]加载文件{path}失败: {str(e)}", exc_info=True)
                continue

if __name__ == "__main__":
    vector_store_service = VectorStoreService()
    vector_store_service.load_documents()
    retriever = vector_store_service.get_retriever()
    results = retriever.invoke("CPU")
    for result in results:
        print(result.page_content)
        print("="*50)
