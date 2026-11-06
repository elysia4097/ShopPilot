from langchain_core.documents import Document

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser


class RagSummarizeService(object):
    """
    总结服务类：用户提问，搜索相关文档，将提问和文档内容提交给模型，让模型总结回复
    """
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.retriever = self.vector_store_service.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()
    
    def _init_chain(self):
        """
        初始化链
        """
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain
    
    def retriever_docs(self,query:str) ->list[Document]:
        """
        检索相关文档
        :param query: 查询字符串
        :return: 相关文档列表
        """
        docs = self.retriever.invoke(query)
        return docs

    def rag_summarize(self,query:str) ->str:
        """
        总结回复
        :param query: 查询字符串
        :return: 总结回复
        """
        context_docs :list[Document] = self.retriever_docs(query)
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        result = self.chain.invoke(
            {
                "input": query, 
                "context": context
            }
            )
        return result

if __name__ == "__main__":
    rag_service = RagSummarizeService()
    query = "服务器没响应"
    result = rag_service.rag_summarize(query)
    print(result)