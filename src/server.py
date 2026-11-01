"""Local live LLM app. Single-thread HTTP keeps MLX GPU stream on its owning thread."""
from http.server import HTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,json,threading,time
from copilot import Planner,answer
ROOT=Path(__file__).resolve().parents[1]
def main(model,port):
 planner=Planner(model);lock=threading.Lock()
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'site'),**kw)
  def do_POST(self):
   if self.path!='/api/ask':self.send_error(404);return
   try:
    length=int(self.headers.get('Content-Length',0))
    if length>16000:raise ValueError('Request too large')
    data=json.loads(self.rfile.read(length));question=data['question']
    if not isinstance(question,str) or not 1<=len(question)<=1500:raise ValueError('Question must be 1–1500 characters')
    with lock:plan,trace=planner.plan(question,data.get('previous'))
    payload=json.dumps({**answer(plan),'trace':trace,'mode':'live local Qwen'},ensure_ascii=False,allow_nan=False).encode()
    self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers();self.wfile.write(payload)
   except (ValueError,KeyError,json.JSONDecodeError) as e:
    self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({'error':str(e)}).encode())
 print(f'Live local Qwen Copilot: http://127.0.0.1:{port}',flush=True)
 HTTPServer(('127.0.0.1',port),Handler).serve_forever()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',default='mlx-community/Qwen3-4B-Instruct-2507-4bit');p.add_argument('--port',type=int,default=8767);a=p.parse_args();main(a.model,a.port)
