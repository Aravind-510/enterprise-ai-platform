"""
backend/chat/conversation_memory.py
"""
import json, os, time, uuid

STORE="conversation_memory.json"
EXPIRY_SECONDS=3600

class ConversationMemory:
    def __init__(self):
        self.sessions={}
        self._load()
    def _load(self):
        if os.path.exists(STORE):
            with open(STORE,"r",encoding="utf-8") as f:
                self.sessions=json.load(f)
    def _save(self):
        with open(STORE,"w",encoding="utf-8") as f:
            json.dump(self.sessions,f,indent=2)
    def create_session(self):
        sid=str(uuid.uuid4())
        self.sessions[sid]={"created":time.time(),"updated":time.time(),"history":[],"preferences":{}}
        self._save()
        return sid
    def add_message(self,sid,question,answer):
        self.sessions[sid]["history"].append({"question":question,"answer":answer,"time":time.time()})
        self.sessions[sid]["updated"]=time.time()
        self._save()
    def set_preference(self,sid,key,value):
        self.sessions[sid]["preferences"][key]=value
        self._save()
    def get_history(self,sid):
        return self.sessions.get(sid,{}).get("history",[])
    def get_preferences(self,sid):
        return self.sessions.get(sid,{}).get("preferences",{})
    def cleanup(self):
        now=time.time()
        expired=[k for k,v in self.sessions.items() if now-v["updated"]>EXPIRY_SECONDS]
        for k in expired:
            del self.sessions[k]
        self._save()

if __name__=="__main__":
    mem=ConversationMemory()
    sid=mem.create_session()
    print("Session:",sid)
    mem.set_preference(sid,"department","HR")
    mem.add_message(sid,"My department is HR.","Preference stored.")
    mem.add_message(sid,"Show policies.","Showing HR policies.")
    print("Preferences:",mem.get_preferences(sid))
    print("History:")
    for h in mem.get_history(sid):
        print(h)
