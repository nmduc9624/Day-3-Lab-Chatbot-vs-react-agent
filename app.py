import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from dotenv import load_dotenv
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.ecommerce_tools import PRODUCTS, COUPONS, SHIPPING_RATE, get_tools_v1, get_tools_v2

load_dotenv()

LLM = OpenAIProvider(model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"), api_key=os.getenv("OPENAI_API_KEY"))
RESPONDERS = {
    "chatbot": {
        "label": "Chatbot baseline",
        "description": "Direct LLM answer with no tools or observations.",
        "run": lambda question: LLM.generate(question)["content"],
    },
    "agentv1": {
        "label": "Agent v1",
        "description": "ReAct loop with v1 tool descriptions.",
        "run": ReActAgent(llm=LLM, tools=get_tools_v1(), max_steps=6).run,
    },
    "agentv2": {
        "label": "Agent v2",
        "description": "Improved ReAct loop with clearer tool specs and get_weight.",
        "run": ReActAgent(llm=LLM, tools=get_tools_v2(), max_steps=10).run,
    },
}

HTML = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Procurement Lab</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#f5f7fb;color:#1d2433}.wrap{max-width:1080px;margin:auto;display:grid;grid-template-columns:320px 1fr;gap:16px;padding:20px}.panel{background:white;border:1px solid #dce3ef;border-radius:8px;padding:16px}.chat{height:65vh;overflow:auto;display:flex;flex-direction:column;gap:10px}.msg{padding:12px;border-radius:8px;white-space:pre-wrap;line-height:1.45}.user{align-self:flex-end;background:#244c98;color:white;max-width:80%}.ai{align-self:flex-start;background:#eef3fb;border:1px solid #d9e4f5;max-width:85%}.meta{display:block;font-size:12px;font-weight:700;color:#526070;margin-bottom:6px}form{display:flex;gap:8px;margin-top:12px}input,select{padding:11px;border:1px solid #cbd5e1;border-radius:6px;font-size:15px}input{flex:1}button{border:0;border-radius:6px;background:#1f7a5c;color:white;font-weight:700;padding:0 16px;cursor:pointer}button:disabled{opacity:.55}.chip{display:block;width:100%;text-align:left;margin:8px 0;padding:9px;border:1px solid #cbd5e1;border-radius:6px;background:white;color:#1d2433}table{width:100%;border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid #edf1f7;padding:6px;text-align:left}@media(max-width:800px){.wrap{grid-template-columns:1fr}}
</style></head><body><div class="wrap"><aside class="panel"><h2>Procurement Lab</h2><p>Choose who answers: Chatbot, Agent v1, or Agent v2.</p><h3>Products</h3><table id="products"></table><h3>Coupons</h3><table id="coupons"></table><h3>Shipping</h3><table id="shipping"></table><h3>Try</h3><button class="chip">I want to buy 2 standing desks using coupon OFFICE10 and ship to Danang. What is the total price?</button><button class="chip">Compare the total cost of buying 1 ergonomic chair shipped to HCMC versus Can Tho.</button><button class="chip">Can I buy 2 portable projectors using coupon BULK15 and ship to Hanoi?</button></aside><main class="panel"><label>Responder <select id="mode"><option value="chatbot">Chatbot baseline</option><option value="agentv1">Agent v1</option><option value="agentv2" selected>Agent v2</option></select></label><p id="help"></p><div class="chat" id="chat"><div class="msg ai"><span class="meta">Agent v2</span>Hello. Choose a responder, then ask a question.</div></div><form id="form"><input id="q" placeholder="Ask your question..."><button id="send">Send</button></form></main></div>
<script>
const data=__DATA__,responders=data.responders;function rows(id,obj,fn){const el=document.querySelector(id);Object.entries(obj).forEach(([k,v])=>el.insertAdjacentHTML('beforeend',fn(k,v)))}rows('#products',data.products,(k,v)=>`<tr><td>${k}</td><td>$${v.price}</td><td>${v.stock}</td><td>${v.weight}kg</td></tr>`);rows('#coupons',data.coupons,(k,v)=>`<tr><td>${k}</td><td>${v}%</td></tr>`);rows('#shipping',data.shipping,(k,v)=>`<tr><td>${k}</td><td>$${v}/kg</td></tr>`);
const chat=document.querySelector('#chat'),form=document.querySelector('#form'),q=document.querySelector('#q'),send=document.querySelector('#send'),mode=document.querySelector('#mode'),help=document.querySelector('#help');function setHelp(){help.textContent=responders[mode.value].description}setHelp();mode.onchange=setHelp;function msg(text,cls,label){const d=document.createElement('div');d.className='msg '+cls;if(label){const m=document.createElement('span');m.className='meta';m.textContent=label;d.appendChild(m)}d.appendChild(document.createTextNode(text));chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d}
async function ask(text){const m=mode.value,label=responders[m].label;msg(text,'user',label);q.value='';send.disabled=true;mode.disabled=true;const pending=msg('Thinking...','ai',label);try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text,mode:m})});const p=await r.json();pending.lastChild.textContent=p.answer||p.error||'No response.'}catch(e){pending.lastChild.textContent='Request failed: '+e.message}finally{send.disabled=false;mode.disabled=false;q.focus()}}
form.onsubmit=e=>{e.preventDefault();const text=q.value.trim();if(text)ask(text)};document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>ask(b.textContent.trim()));
</script></body></html>
"""


def build_page() -> bytes:
    data = {
        "products": PRODUCTS,
        "coupons": COUPONS,
        "shipping": SHIPPING_RATE,
        "responders": {k: {"label": v["label"], "description": v["description"]} for k, v in RESPONDERS.items()},
    }
    return HTML.replace("__DATA__", json.dumps(data)).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path in {"/", "/index.html"}:
            self.send_body(200, build_page(), "text/html; charset=utf-8")
        else:
            self.send_body(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            self.send_body(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = payload.get("question", "").strip()
            mode = payload.get("mode", "agentv2").strip().lower()
            if not question:
                raise ValueError("Question is required.")
            if mode not in RESPONDERS:
                raise ValueError("Unknown responder mode.")
            answer = RESPONDERS[mode]["run"](question)
            self.send_body(200, json.dumps({"answer": answer, "mode": mode}).encode("utf-8"), "application/json; charset=utf-8")
        except Exception as exc:
            self.send_body(400, json.dumps({"error": str(exc)}).encode("utf-8"), "application/json; charset=utf-8")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    host = "127.0.0.1"
    port = int(os.getenv("PORT", "8000"))
    print(f"Open http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
