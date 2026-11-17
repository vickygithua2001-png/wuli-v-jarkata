import os
os.makedirs("templates", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

open("app.py","w").write('''from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "wuli-v-jarkata-kenya"
app.config["UPLOAD_FOLDER"] = "static/uploads"
YOUR_WHATSAPP = "254700000000"
YOUR_MPESA_TILL = "123456"
SITE_NAME = "WULI V JARKATA"
def db():
    c = sqlite3.connect("music.db"); c.row_factory = sqlite3.Row; return c
def init():
    c = db()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, password TEXT, gender TEXT, county TEXT, age INTEGER, is_vip INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS songs (id INTEGER PRIMARY KEY, user_id INTEGER, artist TEXT, title TEXT, genre TEXT, county TEXT, filename TEXT)")
    c.commit(); c.close()
init()
@app.route("/")
def home():
    c = db(); songs = c.execute("SELECT songs.*, users.is_vip FROM songs JOIN users ON songs.user_id=users.id ORDER BY users.is_vip DESC, songs.id DESC").fetchall(); c.close()
    return render_template("index.html", songs=songs, site=SITE_NAME, wa=YOUR_WHATSAPP, till=YOUR_MPESA_TILL, user=session.get("user"))
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        name=request.form["name"]; phone=request.form["phone"]; gender=request.form["gender"]; county=request.form["county"]; age=int(request.form["age"]); pw=generate_password_hash(request.form["password"])
        if age<18 and not request.form.get("guardian"): return "Under 18 needs guardian consent"
        try:
            c=db(); c.execute("INSERT INTO users (name,phone,password,gender,county,age) VALUES (?,?,?,?,?,?)",(name,phone,pw,gender,county,age)); c.commit(); c.close(); return redirect("/login")
        except: return "Phone already registered. Go to Login."
    return render_template("signup.html", site=SITE_NAME)
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        c=db(); u=c.execute("SELECT * FROM users WHERE phone=?", (request.form["phone"],)).fetchone(); c.close()
        if u and check_password_hash(u["password"], request.form["password"]): session["user"]=dict(u); return redirect("/")
        return "Wrong phone or password"
    return render_template("login.html", site=SITE_NAME)
@app.route("/logout")
def logout(): session.clear(); return redirect("/")
@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session: return redirect("/signup")
    if request.method=="POST":
        f=request.files["music"]; fn=f.filename; f.save(os.path.join(app.config["UPLOAD_FOLDER"], fn))
        c=db(); c.execute("INSERT INTO songs (user_id,artist,title,genre,county,filename) VALUES (?,?,?,?,?,?)",(session["user"]["id"], session["user"]["name"], request.form["title"], request.form["genre"], request.form["county"], fn)); c.commit(); c.close(); return redirect("/")
    return render_template("upload.html", site=SITE_NAME)
@app.route("/vip")
def vip():
    if "user" not in session: return redirect("/signup")
    return render_template("vip.html", site=SITE_NAME, till=YOUR_MPESA_TILL, wa=YOUR_WHATSAPP, user=session["user"])
@app.route("/verify-vip/<phone>")
def verify_vip(phone):
    c=db(); c.execute("UPDATE users SET is_vip=1 WHERE phone=?", (phone,)); c.commit(); c.close(); return f"{phone} is now VIP! <a href='/'>Back</a>"
@app.route("/uploads/<filename>")
def upfile(filename): return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
if __name__=="__main__": app.run(host="0.0.0.0", port=5000, debug=True)
''')

open("templates/index.html","w").write('''<body style="background:#000;color:#fff;font-family:sans-serif;padding:15px"><h1 style="color:gold;text-align:center">WULI V JARKATA</h1><p style="text-align:center">Kenya Music For All - All Genders, All Ages, All Counties | Upload FREE</p><p style="text-align:center"><a href="/signup" style="color:gold">Sign Up</a> | <a href="/login" style="color:gold">Login</a> | <a href="/upload" style="color:gold">Upload Song</a> | <a href="/vip" style="color:gold">VIP 100 KSh</a></p>{% for s in songs %}<div style="background:#111;border:1px solid gold;border-radius:12px;padding:15px;margin:12px 0"><h3>{{ s.title }} - {{ s.artist }} {% if s.is_vip %}VIP{% endif %}</h3><p>{{ s.genre }} | {{ s.county }}</p><audio controls src="/uploads/{{ s.filename }}" style="width:100%"></audio><br><a href="https://wa.me/{{ wa }}?text=Hi WULI V JARKATA" style="background:#25D366;color:#fff;padding:10px;display:inline-block;text-decoration:none;border-radius:8px;margin-top:10px">WhatsApp Host</a></div>{% endfor %}</body>''')

open("templates/signup.html","w").write('''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px"><h2 style="color:gold">WULI V JARKATA - Sign Up FREE</h2><p>For ALL - All Genders, All Ages, All Counties. Karibu!</p><form method="POST"><input name="name" placeholder="Full / Stage Name" required style="width:100%;padding:12px;margin:6px 0"><input name="phone" placeholder="Phone 071..." required style="width:100%;padding:12px"><input type="password" name="password" placeholder="Password" required style="width:100%;padding:12px;margin:6px 0"><select name="gender" style="width:100%;padding:12px"><option>Male</option><option>Female</option><option>Non-Binary</option><option>Prefer not to say</option></select><select name="county" style="width:100%;padding:12px;margin:6px 0"><option>Nairobi</option><option>Kiambu</option><option>Mombasa</option><option>Kisumu</option><option>Nakuru</option><option>Nyeri</option><option>Muranga</option><option>Other</option></select><input type="number" name="age" placeholder="Age" required style="width:100%;padding:12px"><br><label><input type="checkbox" name="guardian"> Under 18 - guardian allows</label><br><br><button style="background:gold;padding:14px;width:100%;font-weight:bold">CREATE FREE ACCOUNT</button></form><p>Have account? <a href="/login" style="color:gold">Login</a></p></body>''')

open("templates/login.html","w").write('''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px"><h2 style="color:gold">Login - WULI V JARKATA</h2><form method="POST"><input name="phone" placeholder="Phone" required style="width:100%;padding:12px"><input type="password" name="password" placeholder="Password" required style="width:100%;padding:12px;margin:8px 0"><button style="background:gold;padding:14px;width:100%">LOGIN</button></form></body>''')

open("templates/upload.html","w").write('''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px"><h2 style="color:gold">Upload FREE</h2><form method="POST" enctype="multipart/form-data"><input name="title" placeholder="Song Title" required style="width:100%;padding:12px"><input name="genre" placeholder="Genre e.g Gengetone, Gospel, Arbantone" style="width:100%;padding:12px;margin:8px 0"><input name="county" placeholder="County" style="width:100%;padding:12px"><input type="file" name="music" accept="audio/*" required style="margin:12px 0"><button style="background:gold;padding:14px;width:100%">UPLOAD</button></form></body>''')

open("templates/vip.html","w").write('''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px;text-align:center"><h1 style="color:gold">VIP MODE - 100 KSh ONLY</h1><p>Unlimited uploads - Top of homepage - Verified Badge</p><h3>Pay via M-Pesa</h3><p>Till: <b style="color:gold">{{ till }}</b><br>Amount: 100 KSh</p><p>1. M-Pesa > Lipa na M-Pesa > Buy Goods<br>2. Till {{ till }} - 100 KSh<br>3. Send code on WhatsApp</p><a href="https://wa.me/{{ wa }}?text=Hi WULI V JARKATA I paid VIP 100" style="background:#25D366;color:#fff;padding:14px;display:block;text-decoration:none;border-radius:10px">SEND M-PESA CODE ON WHATSAPP</a></body>''')
print("WULI V JARKATA files created!")
