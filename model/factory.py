"""
模型工厂类
用于创建不同的模型实例
"""
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from utils.config_handler import rag_config


class BaseModelFactory(ABC): 
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_config["chat_model_name"])

class EmbeddingsModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_config["embedding_model_name"])


chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingsModelFactory().generator()