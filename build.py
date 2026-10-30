# SOARiA メンバーサイト：Apps Script の画面ファイルを取ってきて、GitHub Pages 用に変換する
# 使い方：Actions タブ →「サイトを更新」→ Run workflow
import json, re, io, base64, urllib.request, os
API_URL = "https://script.google.com/macros/s/AKfycbxZUDMYigCAWncQTNfTqfvVM66sTJEo9tGyu9RjrNA_ZoGFYj84Ik8C3PyguG7nOw5biw/exec"
req = urllib.request.Request(API_URL, data=json.dumps({"fn": "siteSource", "args": []}).encode(), headers={"Content-Type": "text/plain"})
s = json.load(urllib.request.urlopen(req, timeout=60))["ok"]["html"]
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
rep('<meta charset="utf-8">\n', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>SOARiA</title>\n<meta name="robots" content="noindex, nofollow">\n<meta name="theme-color" content="#f5f5f7">\n<link rel="icon" href="icon.png">\n<link rel="apple-touch-icon" href="icon.png">\n<meta name="apple-mobile-web-app-title" content="SOARiA">\n')
s, n = re.subn(r'<input type="hidden" id="boot[TK]" value="[^"]*">\n', '', s)
assert n == 2, n
rep('return new Promise((res,rej)=>google.script.run.withSuccessHandler(res).withFailureHandler(rej)[fn](...args));',
    'return fetch(API_URL,{method:"POST",body:JSON.stringify({fn,args}),credentials:"omit",redirect:"follow",cache:"no-store"}).then(r=>{if(!r.ok)throw new Error("HTTP "+r.status);return r.json();}).then(j=>{if(j&&Object.prototype.hasOwnProperty.call(j,"err"))throw new Error(j.err);return j?j.ok:null;});')
rep('function api(fn,...args){', 'const API_URL="' + API_URL + '";\nconst QS=new URLSearchParams(location.search);\nfunction api(fn,...args){')
rep('const KEY=(($("bootK")||{}).value||"").trim();', 'const KEY=(QS.get("k")||"").trim();')
rep('async function boot(){\nconst t=($("bootT")||{}).value||"";',
    'async function showReply(r){\ntry{history.replaceState(null,"",location.pathname);}catch(e){}\nlet msg="";\ntry{const x=await api("replyDone",r);msg=x&&x.name?x.name+"さんに、やりとりを始めたことを伝えました。":"このリンクはすでに使われているか、見つかりませんでした。";}\ncatch(e){msg="うまくいきませんでした。時間をおいて、もう一度開いてください。";}\ndocument.body.innerHTML=\'<div style="font-family:system-ui,sans-serif;max-width:420px;margin:48px auto;padding:0 16px;text-align:center;color:#1f2933"><h2 style="color:#1d4a9c">SOARiA</h2><p>\'+esc(msg)+\'</p><p style="color:#66737e;font-size:13px">この画面は閉じて大丈夫です。</p></div>\';\n}\nasync function boot(){\nconst rr=QS.get("r");if(rr){showReply(rr);return;}\nconst t=QS.get("t")||"";')
rep('try{google.script.history.replace(null,KEY?{k:KEY}:{},"");}catch(e){}', 'try{history.replaceState(null,"",location.pathname+(KEY?"?k="+encodeURIComponent(KEY):""));}catch(e){}')
rep('<option value="kana">名前順</option>', '<option value="kana">名前順</option><option value="pref">地域順</option>')
rep('if(st.sort==="kana")list.sort((a,b)=>String(a.kana).localeCompare(String(b.kana),"ja"));', 'if(st.sort==="kana")list.sort((a,b)=>String(a.kana).localeCompare(String(b.kana),"ja"));\n  if(st.sort==="pref"){const pi=p=>{const i=ALLPREFS.indexOf(p);return i<0?999:i;};list.sort((a,b)=>pi(a.pref)-pi(b.pref)||String(a.kana).localeCompare(String(b.kana),"ja"));}')
assert 'google.script' not in s and '<?' not in s
os.makedirs('docs', exist_ok=True)
open('docs/index.html', 'w', encoding='utf-8').write(s)
open('docs/.nojekyll', 'w').close()
from PIL import Image
import html as H
m = re.search(r'<img src="data:image/webp;base64,([^"]+)"', s)
im = Image.open(io.BytesIO(base64.b64decode(H.unescape(m.group(1))))).convert('RGBA')
bg = Image.new('RGBA', (180, 180), (255, 255, 255, 255)); w, h = im.size; k = 150 / max(w, h)
im = im.resize((int(w * k), int(h * k)), Image.LANCZOS)
bg.paste(im, ((180 - im.size[0]) // 2, (180 - im.size[1]) // 2), im)
bg.convert('RGB').save('docs/icon.png')
print('built', len(s))
