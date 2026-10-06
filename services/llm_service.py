import json, os, re, time, random
from google import genai
from schemas.meeting_schema import MeetingIntelligence
from prompts.meeting_prompt import build_meeting_prompt, build_rag_prompt

class GeminiTemporaryError(Exception): pass
class GeminiQuotaError(Exception): pass
class GeminiPermanentError(Exception): pass

class LLMService:
    def __init__(self, api_key=None, model=None):
        self.api_key=api_key or os.getenv("GEMINI_API_KEY")
        self.model=model or os.getenv("GEMINI_MODEL","gemini-3.6-flash")
        if not self.api_key: raise ValueError("GEMINI_API_KEY is missing.")
        self.client=genai.Client(api_key=self.api_key)

    def _call(self, prompt):
        for attempt in range(4):
            try:
                response=self.client.models.generate_content(model=self.model, contents=prompt)
                return response.text or ""
            except Exception as e:
                msg=str(e).lower()
                if "generate_content_free_tier_requests" in msg or "perdayperprojectpermodel" in msg or "daily quota" in msg:
                    raise GeminiQuotaError("Gemini daily free-tier generation quota is exhausted. Wait for the quota reset or use available paid/project quota.")
                if "429" in msg or "rate limit" in msg:
                    if attempt < 3: time.sleep(min(20,2**attempt)+random.random()); continue
                    raise GeminiQuotaError("Gemini request rate/quota limit was reached.")
                if any(x in msg for x in ["500","502","503","504","unavailable","timeout"]):
                    if attempt < 3: time.sleep(min(20,2**attempt)+random.random()); continue
                    raise GeminiTemporaryError("Gemini is temporarily unavailable. Please retry later.")
                if any(x in msg for x in ["401","403","api key","authentication","400","404","invalid argument"]):
                    raise GeminiPermanentError(f"Gemini request failed: {e}")
                raise GeminiPermanentError(f"Gemini request failed: {e}")
        raise GeminiTemporaryError("Gemini request failed.")

    def _json(self,text):
        text=re.sub(r"```json|```","",text).strip()
        start=text.find("{"); end=text.rfind("}")
        if start>=0 and end>start: text=text[start:end+1]
        data=json.loads(text)
        return MeetingIntelligence.model_validate(data).model_dump()

    def process_long_transcript(self, transcript):
        if len(transcript)>50000:
            chunks=[transcript[i:i+47000] for i in range(0,len(transcript),45000)]
            results=[self._json(self._call(build_meeting_prompt(c))) for c in chunks]
            return self._merge(results)
        return self._json(self._call(build_meeting_prompt(transcript)))

    def process_transcript(self, transcript): return self.process_long_transcript(transcript)
    def analyze(self, transcript): return self.process_long_transcript(transcript)
    def analyze_meeting(self, transcript): return self.process_long_transcript(transcript)

    def _merge(self, results):
        base={"summary":" ".join(r.get("summary","") for r in results),"key_points":[],"decisions":[],"action_items":[],"participants":[],"deadlines":[],"priorities":[]}
        for r in results:
            for k in ["key_points","decisions","action_items","participants","deadlines","priorities"]: base[k].extend(r.get(k,[]))
        return MeetingIntelligence.model_validate(base).model_dump()

    def generate_rag_answer(self, question, context):
        return self._call(build_rag_prompt(question,context)).strip()
