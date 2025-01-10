import datetime
from langchain_community.embeddings import HuggingFaceEmbeddings
from pymilvus import MilvusClient
from langchain_community.vectorstores import Milvus
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from db import MySQLDatabase

class MilvusStore:
    def __init__(self, collection_name, host="127.0.0.1", port="19530", model_name='intfloat/e5-large-v2'):
        self.collection_name = collection_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.milvus_host = host
        self.milvus_port = port
        self.model_name = model_name
        self.vectordb = Milvus(
            self.embeddings,
            collection_name=self.collection_name,
            connection_args={"host": self.milvus_host, "port": self.milvus_port}
        )
        self.client = MilvusClient(
            uri=f"http://{host}:{port}",
            token="root:Milvus"
        )
        self.db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')

    def load_from_milvus(self, collection_name):
        self.collection_name = collection_name

    def search(self, query):
        document_content_description = "textbook"
        self.vectordb = Milvus(
            self.embeddings,
            collection_name=self.collection_name,
            connection_args={"host": self.milvus_host, "port": self.milvus_port}
        )
        llm = Ollama(model = "mistral:instruct")
        retriever = self.vectordb.as_retriever()
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Use three sentences maximum and keep the answer as concise as possible. 
        Always say "thanks for asking!" at the end of the answer. 
        {context}
        Question: {question}
        Helpful Answer:"""
        rag_prompt = PromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
        )

        res = rag_chain.invoke(query)
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return res

        
    def delete_from_collection(self, id):
        self.vectordb = Milvus(
            self.embeddings,
            collection_name=self.collection_name,
            connection_args={"host": self.milvus_host, "port": self.milvus_port})
        
        docs = self.vectordb.as_retriever(
            search_kwargs={"expr": f'id == {id}'}
        ).get_relevant_documents("")
        pks = []
        for doc in docs:
            pks.append(doc.metadata['pk'])
        res = self.vectordb.delete(pks)
        print(res)

    def drop_collection(self):
        self.client.drop_collection(collection_name=self.collection_name)


if __name__ == "__main__":
    store = MilvusStore(collection_name="bobble_1")
    store.drop_collection()