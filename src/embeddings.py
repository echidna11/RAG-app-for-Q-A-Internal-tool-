import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from pymilvus import MilvusClient
from pymilvus import MilvusClient, Collection, connections, CollectionSchema, FieldSchema, DataType
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from db import MySQLDatabase


class EmbeddingsGenerator:
    def __init__(self, model_name, text_file, collection_name, milvus_host="127.0.0.1", milvus_port="19530"):
        self.model_name = model_name
        self.file_name = text_file
        self.collection_name = collection_name
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        self.client = MilvusClient(
            uri=f"http://{self.milvus_host}:{self.milvus_port}",
            token="root:Milvus"
        )
        self.vector_db = None  
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)  

    def generate_embeddings(self, id):
        connections.connect(host='localhost', port='19530')
        print('default file id is :', id)

        documents = []
        loader = TextLoader(self.file_name)

        if self.file_name.endswith('.txt') or self.file_name.endswith('.md'):
            pass
        elif self.file_name.endswith('.pdf'):
            loader = PyPDFLoader(self.file_name)
        elif self.file_name.endswith('.csv'):
            loader = CSVLoader(self.file_name)
        else:
            print("File type not supported")
            return
        
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=25)
        docs = text_splitter.split_documents(documents)
        file_texts =[]
        for i, chunked_text in enumerate(docs):
            file_texts.append(Document(page_content=chunked_text.page_content,
                                   metadata={"id" : id, "doc_title": f"Chunk-{i}", "chunk_num": i}))
            
        self.vector_db = Milvus.from_documents(
            file_texts,
            self.embeddings,
            collection_name=self.collection_name,
            connection_args={"alias": "default", "host": self.milvus_host, "port": self.milvus_port}
        )

        return self.vector_db
    
    def add_to_collection(self, file, id):
        print("File ID is :", id)
        loader = TextLoader(file)

        if file.endswith('.txt') or file.endswith('.md'):
            pass
        elif file.endswith('.pdf'):
            loader = PyPDFLoader(file)
        elif file.endswith('.csv'):
            loader = CSVLoader(file)
        else:
            print("File type not supported")
            return
        
        new_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=25)
        new_docs = text_splitter.split_documents(new_documents)
        file_texts =[]
        for i, chunked_text in enumerate(new_docs):
            file_texts.append(Document(page_content=chunked_text.page_content,
                                    metadata={"id" : id, "doc_title": f"Chunk-{i}", "chunk_num": i}))
        self.vector_db.upsert(documents = file_texts)


if __name__ == "__main__":


    embeddings_generator = EmbeddingsGenerator(
        model_name='intfloat/e5-large-v2',
        text_file='text/sample.txt',
        collection_name='bobble_1'
    )

    vector_db = embeddings_generator.generate_embeddings(1)

    new_documents_file = 'text/text_1.txt'
    embeddings_generator.add_to_collection(new_documents_file, 2)
    docs = vector_db.as_retriever(
        search_kwargs={"expr": 'id == 2'}
    ).get_relevant_documents("")
    print(docs)
    pks = []
    for doc in docs:
        pks.append(doc.metadata['pk'])
    res = embeddings_generator.vector_db.delete(pks)
    print(res)