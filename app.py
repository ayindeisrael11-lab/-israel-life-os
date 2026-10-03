from flask import Flask, request, redirect, render_template_string, session, jsonify
import json, os
from datetime import datetime

app=Flask(__name__)
app.secret_key="israel_ultimate_2026"
PASSWORD="israel123"
FILE="tasks.json"

def load_tasks():
    if not os.path.exists(FILE): return []
    try:
        with open(FILE,"r") as f: return json.load(f)
    except: return []

def save_tasks(t):
    with open(FILE,"w") as f: json.dump(t,f)

HTML='''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Israel OS - Ultimate</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--card:#ffffff;--text:#0f172a;--muted:#64748b;--bg1:#667eea;--bg2:#764ba2;--input:#f8fafc}
*{font-family:Inter,sans-serif;box-sizing:border-box;transition:.2s}
body{margin:0;background:linear-gradient(135deg,var(--bg1),var(--bg2));min-height:100vh;padding:12px;color:var(--text)}
.container{max-width:900px;margin:0 auto}
.nav{display:flex;justify-content:space-between;align-items:center;color:white;padding:8px 4px}
.nav b{font-size:18px}
.nav a{color:white;text-decoration:none;background:rgba(255,255,255,.2);padding:8px 14px;border-radius:20px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:14px 0}
.card{background:var(--card);border-radius:18px;padding:18px;box-shadow:0 10px 25px rgba(0,0,0,.15)}
.stat b{font-size:24px}
.main{display:grid;grid-template-columns:2fr 1fr;gap:12px}
@media(max-width:700px){.main{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,1fr)}}
.add{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.add input,.add select{padding:12px 14px;border:2px solid #e2e8f0;border-radius:12px;flex:1;min-width:120px}
.btn{padding:12px 20px;background:#0f172a;color:white;border:none;border-radius:12px;font-weight:700;cursor:pointer}
.btn-ghost{background:var(--input);color:var(--text)}
.task{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:var(--input);border-radius:14px;margin-bottom:8px;border-left:5px solid #6366f1}
.task.done{opacity:.6;text-decoration:line-through;border-left-color:#10b981}
.badge{font-size:9px;padding:4px 8px;border-radius:20px;color:white;font-weight:800}
.badge-school{background:#f59e0b}.badge-business{background:#10b981}.badge-personal{background:#8b5cf6}.badge-urgent{background:#ef4444}
.meta{font-size:11px;color:var(--muted)}
.actions a{margin-left:6px;text-decoration:none;font-weight:600;background:white;padding:6px 9px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,.1)}
</style>
</head>
<body>
<div class="container">
<div class="nav"><b>⚡ ISRAEL OS • Ultimate</b><div><a href="/export">📤 Export</a> <a href="/logout" style="background:#ef4444">🔒 Lock</a></div></div>

<div class="grid">
<div class="card stat"><b>{{total}}</b><div class="meta">Total Tasks</div></div>
<div class="card stat"><b style="color:#10b981">{{done}}</b><div class="meta">Completed</div></div>
<div class="card stat"><b style="color:#f59e0b">{{pending}}</b><div class="meta">Pending</div></div>
<div class="card stat"><b style="color:#6366f1">{{percent}}%</b><div class="meta">Productivity</div></div>
</div>

<div class="main">
<div class="card">
<h3 style="margin:0 0 12px">🎯 Today's Focus</h3>
<form class="add" action="/add" method="post">
<input type="text" name="task" placeholder="What will you dominate today?" required>
<select name="cat"><option value="school">School</option><option value="business">Business</option><option value="personal">Personal</option><option value="urgent">Urgent 🔥</option></select>
<select name="priority"><option value="normal">Normal</option><option value="high">High</option><option value="low">Low</option></select>
<input type="date" name="due">
<button class="btn">Add +</button>
</form>

<div style="display:flex;gap:6px;margin-bottom:12px">
<a href="/?filter=" class="btn btn-ghost">All</a>
<a href="/?filter=school" class="btn btn-ghost">School</a>
<a href="/?filter=business" class="btn btn-ghost">Business</a>
<a href="/?filter=urgent" class="btn btn-ghost">Urgent</a>
<form method="get" style="flex:1;display:flex;gap:6px"><input type="text" name="q" placeholder="Search..." value="{{q}}" style="flex:1;padding:10px;border-radius:12px;border:2px solid #e2e8f0"><button class="btn">Go</button></form>
</div>

{% for i,t in display %}
<div class="task {{'done' if t.done else ''}}">
<div><span class="badge badge-{{t.cat}}">{{t.cat}}</span> {% if t.priority=='high'%}<span style="color:red">⚡</span>{% endif %} {{t.text}}<div class="meta">{{t.priority}} • {% if t.due %}📅 {{t.due}}{% else %}No deadline{% endif %}</div></div>
<div class="actions"><a href="/toggle/{{i}}">✓</a><a href="/edit/{{i}}">✏️</a><a href="/delete/{{i}}">🗑️</a></div>
</div>
{% endfor %}
</div>

<div>
<div class="card">
<h4 style="margin:0 0 10px">📊 Analytics</h4>
<canvas id="myChart" height="200"></canvas>
<p class="meta">{{date}} • Israel's Workspace</p>
</div>
<div class="card" style="margin-top:12px">
<h4 style="margin:0 0 8px">💡 Tip</h4>
<p class="meta">You complete {{done}} tasks. Focus on <b>Urgent</b> tasks first. Export your data daily for backup.</p>
<a href="/clear_done" class="btn btn-ghost" style="width:100%;text-align:center;display:block;margin-top:10px;text-decoration:none">Clear Completed</a>
</div>
</div>
</div>
</div>
<script>
new Chart(document.getElementById('myChart'),{type:'doughnut',data:{labels:['Done','Pending'],datasets:[{data:[{{done}},{{pending}}],backgroundColor:['#10b981','#f59e0b']}]},options:{plugins:{legend:{display:false}}}})
</script>
</body>
</html>
'''

EDIT='''
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);font-family:sans-serif">
<div style="background:white;padding:30px;border-radius:20px;width:380px">
<h3>Edit</h3>
<form method="post">
<input name="task" value="{{t.text}}" style="width:100%;padding:12px;border-radius:12px;border:2px solid #ddd;margin-bottom:8px">
<select name="cat" style="width:100%;padding:12px;border-radius:12px;margin-bottom:8px"><option value="school" {{'selected' if t.cat=='school'}}>School</option><option value="business" {{'selected' if t.cat=='business'}}>Business</option><option value="personal" {{'selected' if t.cat=='personal'}}>Personal</option><option value="urgent" {{'selected' if t.cat=='urgent'}}>Urgent</option></select>
<input type="date" name="due" value="{{t.due}}" style="width:100%;padding:12px;border-radius:12px;margin-bottom:12px">
<button style="width:100%;padding:12px;background:#0f172a;color:white;border:none;border-radius:12px">Save Changes</button>
</form><br><a href="/">← Back</a>
</div></div>
'''

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("password")==PASSWORD:
            session["logged"]=True;session.permanent=False;return redirect("/")
        return "Wrong! <a href='/login'>Retry</a>"
    session.clear()
    return '''<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);font-family:sans-serif"><div style="background:white;padding:40px;border-radius:24px;text-align:center;width:360px;box-shadow:0 20px 40px rgba(0,0,0,.3)"><h1>⚡ ISRAEL OS</h1><p>Ultimate Level 3</p><form method="post"><input type="password" name="password" placeholder="Password: israel123" style="width:100%;padding:14px;border-radius:12px;border:2px solid #ddd;margin-bottom:12px"><button style="width:100%;padding:14px;background:#0f172a;color:white;border:none;border-radius:12px;font-weight:800">ENTER OS →</button></form></div></div>'''

@app.route("/logout")
def logout(): session.clear(); return redirect("/login")
@app.route("/export")
def export():
    if not session.get("logged"): return redirect("/login")
    return jsonify(load_tasks())
@app.route("/clear_done")
def clear_done():
    tasks=[t for t in load_tasks() if not t.get("done")]
    save_tasks(tasks); return redirect("/")

@app.route("/")
def index():
    if not session.get("logged"): return redirect("/login")
    tasks=load_tasks()
    q=request.args.get("q","").lower(); f=request.args.get("filter","")
    filtered=[(i,t) for i,t in enumerate(tasks) if (not q or q in t["text"].lower()) and (not f or t.get("cat")==f)]
    total=len(tasks); done=len([t for t in tasks if t.get("done")]); percent=int(done/total*100) if total else 0
    return render_template_string(HTML, display=filtered, total=total, done=done, pending=total-done, percent=percent, date=datetime.now().strftime("%a %d %b"), q=request.args.get("q",""))

@app.route("/add",methods=["POST"])
def add():
    tasks=load_tasks()
    tasks.append({"text":request.form.get("task"),"cat":request.form.get("cat","school"),"priority":request.form.get("priority","normal"),"done":False,"due":request.form.get("due","")})
    save_tasks(tasks); return redirect("/")

@app.route("/toggle/<int:id>")
def toggle(id):
    t=load_tasks()
    if 0<=id<len(t): t[id]["done"]=not t[id]["done"]; save_tasks(t)
    return redirect(request.referrer or "/")

@app.route("/delete/<int:id>")
def delete(id):
    t=load_tasks()
    if 0<=id<len(t): t.pop(id); save_tasks(t)
    return redirect("/")

@app.route("/edit/<int:id>",methods=["GET","POST"])
def edit(id):
    t=load_tasks()
    if not (0<=id<len(t)): return redirect("/")
    if request.method=="POST":
        t[id].update({"text":request.form.get("task"),"cat":request.form.get("cat"),"due":request.form.get("due")})
        save_tasks(t); return redirect("/")
    return render_template_string(EDIT, t=t[id])

if __name__=="__main__":
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",5000)))