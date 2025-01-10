from embeddings import EmbeddingsGenerator
from milvus_util import MilvusStore

class RagUtil:
    def __init__(self):
        self.embeddings_generator = None
        self.store = MilvusStore('bobble_1')

    def set_collection(self, collection_name):
        self.embeddings_generator = EmbeddingsGenerator(
            model_name='intfloat/e5-large-v2',
            text_file='text/sample.txt',
            collection_name=collection_name
        )
        self.embeddings_generator.generate_embeddings(0)
        self.store = MilvusStore(collection_name=collection_name)
    
    def fetch_collection(self, collection_name):
        self.store.load_from_milvus(collection_name)

    def add_file_to_collection(self, file_path, file_id):
        self.embeddings_generator.add_to_collection(file_path, file_id)

    def remove_file_from_collection(self, file_id):
        self.store.delete_from_collection(file_id)

    def search(self, query):
        return self.store.search(query)


if __name__ == "__main__":
    rag_util = RagUtil()
