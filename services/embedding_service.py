import os
from google import genai

class EmbeddingService:
    def __init__(self, api_key=None, model=None):
        key=api_key or os.getenv("GEMINI_API_KEY")
        if not key: raise ValueError("GEMINI_API_KEY is missing.")
        self.client=genai.Client(api_key=key)
        self.model=model or os.getenv("GEMINI_EMBEDDING_MODEL","gemini-embedding-001")

    def generate_embedding(self,text):
        result=self.client.models.embed_content(model=self.model, contents=text)
        emb=getattr(result,"embeddings",None)
        if emb: return list(emb[0].values)
        raise RuntimeError("Embedding API returned no embedding.")

    def split_text(self,text,chunk_size=1500,overlap=200):
        text=text or ""; chunks=[]; start=0
        while start<len(text):
            end=min(len(text),start+chunk_size); chunks.append(text[start:end])
            if end>=len(text): break
            start=max(0,end-overlap)
        return chunks
