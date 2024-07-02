import chromadb
import ollama


class Embedor:
    def __init__(self, model='nomic-embed-text'):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="test")
        self.documents = []
        self.embedding_model = model

    def add_doc(self, text):
        self.documents.append(text)

    def embedding(self, prompt: str) -> str:
        if len(self.documents) == 0:
            return None
        
        for i, d in enumerate(self.documents):
            response = ollama.embeddings(model=self.embedding_model, prompt=d)
            embedding = response["embedding"]
            self.collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )

        # Create embeddings for the prompt
        response = ollama.embeddings(
            prompt=prompt,
            model=self.embedding_model
        )

        # Query the collection for the most similar document
        results = self.collection.query(
            query_embeddings=[response["embedding"]],
            n_results=1
        )

        # Get the most similar document
        data = results['documents'][0][0]        
        return data

    def has_data(self):
        return len(self.documents) > 0
    