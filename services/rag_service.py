from services.search_service import SearchService
from services.llm_service import LLMService, GeminiQuotaError, GeminiTemporaryError, GeminiPermanentError

class RAGService:
    def __init__(self):
        self.search=SearchService()

    def answer(self,question,top_k=5,meeting_id=None):
        results=self.search.search(question,top_k,meeting_id)
        if not results:
            return {"answer":"No relevant information was found in the meeting repository.","sources":[],"mode":"no_results"}
        context="\n\n".join(f"[Meeting #{r['meeting_id']} | {r['meeting_title']} | Chunk {r['chunk_id']}]\n{r['document']}" for r in results)
        try:
            answer=LLMService().generate_rag_answer(question,context)
            return {"answer":answer,"sources":results,"mode":"gemini"}
        except GeminiQuotaError:
            best=results[0]["document"]
            return {"answer":"Gemini generation quota is currently unavailable. The most relevant retrieved meeting evidence is:\n\n"+best,"sources":results,"mode":"local_fallback"}
        except (GeminiTemporaryError,GeminiPermanentError) as e:
            return {"answer":f"AI answer generation is unavailable: {e}\n\nMost relevant evidence:\n{results[0]['document']}","sources":results,"mode":"fallback"}
