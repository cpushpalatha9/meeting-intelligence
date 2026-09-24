from services.database_service import get_meeting, get_all_meetings
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

class MeetingIndexingService:
    def __init__(self):
        self.emb=EmbeddingService(); self.vec=VectorService()

    def index_meeting(self,meeting_id):
        m=get_meeting(meeting_id)
        if not m: return {"success":False,"error":"Meeting not found"}
        self.vec.delete_meeting(meeting_id)
        chunks=self.emb.split_text(m["transcript"])
        ids=[]; docs=[]; embs=[]; metas=[]
        for i,ch in enumerate(chunks):
            ids.append(f"meeting_{meeting_id}_chunk_{i}"); docs.append(ch)
            embs.append(self.emb.generate_embedding(ch))
            metas.append({"meeting_id":str(meeting_id),"chunk_id":str(i),"meeting_title":m["title"]})
        if ids:self.vec.add_chunks(ids,docs,embs,metas)
        return {"success":True,"meeting_id":meeting_id,"chunks_indexed":len(ids)}

    def index_all_meetings(self):
        return [self.index_meeting(m["id"]) for m in get_all_meetings()]

    def get_index_status(self):
        return {"count":self.vec.collection_count()}
