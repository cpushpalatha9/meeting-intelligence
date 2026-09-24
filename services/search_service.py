from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

class SearchService:
    def __init__(self):
        self.emb=EmbeddingService(); self.vec=VectorService()

    def search(self,query,top_k=5,meeting_id=None):
        e=self.emb.generate_embedding(query)
        results=self.vec.search(e,top_k,meeting_id)
        for r in results: r["meeting_id"]=r["metadata"].get("meeting_id"); r["chunk_id"]=r["metadata"].get("chunk_id"); r["meeting_title"]=r["metadata"].get("meeting_title"); r["similarity"]=1/(1+float(r["distance"]))
        return results

    def search_meeting(self,query,meeting_id,top_k=5): return self.search(query,top_k,meeting_id)
