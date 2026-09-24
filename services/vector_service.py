import os
import chromadb

class VectorService:
    def __init__(self,path=None):
        path=path or os.getenv("CHROMA_PATH","vector_store/chroma_db")
        self.client=chromadb.PersistentClient(path=path)
        self.collection=self.client.get_or_create_collection("meeting_transcripts")

    def collection_count(self): return self.collection.count()
    def delete_meeting(self,meeting_id):
        self.collection.delete(where={"meeting_id":str(meeting_id)})
    def add_chunks(self, ids, documents, embeddings, metadatas):
        self.collection.add(ids=ids,documents=documents,embeddings=embeddings,metadatas=metadatas)
    def search(self,embedding,top_k=5,meeting_id=None):
        kwargs={"query_embeddings":[embedding],"n_results":top_k}
        if meeting_id is not None: kwargs["where"]={"meeting_id":str(meeting_id)}
        r=self.collection.query(**kwargs)
        out=[]
        for i in range(len(r.get("ids",[[]])[0])):
            out.append({"id":r["ids"][0][i],"document":r["documents"][0][i],"metadata":r["metadatas"][0][i],"distance":r["distances"][0][i]})
        return out
