from flask import Flask, request, redirect, url_for, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads'
app.config['MAX_CONTENT_LENGTH']=50*1024*1024
os.makedirs('uploads', exist_ok=True)
app.secret_key = "wuli-v-jarkata-2026"
UPLOAD = "static/uploads"
os.makedirs(UPLOAD, exist_ok=True)

COUNTIES = ["Baringo","Bomet","Bungoma","Busia","Elgeyo-Marakwet","Embu","Garissa","Homa Bay","Isiolo","Kajiado","Kakamega","Kericho","Kiambu","Kilifi","Kirinyaga","Kisii","Kisumu","Kitui","Kwale","Laikipia","Lamu","Machakos","Makueni","Mandera","Marsabit","Meru","Migori","Mombasa","Murang'a","Nairobi","Nakuru","Nandi","Narok","Nyamira","Nyandarua","Nyeri","Samburu","Siaya","Taita-Taveta","Tana River","Tharaka-Nithi","Trans Nzoia","Turkana","Uasin Gishu","Vihiga","Wajir","West Pokot"]

def db():
    c = sqlite3.connect("wuli.db"); c.row_factory = sqlite3.Row; return c

def init():
    c=db()
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, phone TEXT, county TEXT, role TEXT, genre TEXT, password TEXT, fans INTEGER DEFAULT 0, points INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, title TEXT, artist TEXT, genre TEXT, county TEXT, filename TEXT, vip INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS follows(id INTEGER PRIMARY KEY, fan TEXT, artist TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS rewards(id INTEGER PRIMARY KEY, artist TEXT, action TEXT, points INTEGER)")
    c.commit(); c.close()
init()

def counties_options(sel=""):
    return "".join([f'<option {"selected" if x==sel else ""}>{x}</option>' for x in COUNTIES])

def counties_grid():
    return "".join([f'<a href="/county/{x}" style="background:#111;border:1px solid gold;color:#fff;padding:8px;border-radius:20px;text-decoration:none;font-size:12px">{x}</a>' for x in COUNTIES])

def header():
    return '''
<div style="background:#000;padding:15px;text-align:center;border-bottom:2px solid gold">
<h1 style="color:gold;margin:0;font-size:30px">WULI V JARKATA 🇰🇪</h1>
<p style="margin:5px;color:#fff">🎤 NEW ARTISTS RECRUITING SITE - Kenya's Home For New Stars</p>
<p style="background:gold;color:#000;display:inline-block;padding:8px 14px;border-radius:20px;font-weight:bold;font-size:13px">🔥 100% FREE - JOIN AS ARTIST OR FAN</p>
</div>
<div style="text-align:center;padding:10px;background:#111">
<a href="/" style="color:gold;margin:5px">Home</a> | <a href="/signup" style="color:gold;margin:5px">Sign Up</a> | <a href="/rewards" style="color:gold;margin:5px">🏆 Rewards</a> | <a href="/vip" style="color:gold;margin:5px">⭐ VIP 100 KSh</a> | <a href="/login" style="color:gold;margin:5px">Login</a>
</div>
'''

def footer_link():
    return '''
<div style="background:#fff;color:#000;text-align:center;padding:15px;margin:15px;border-radius:15px;border:3px solid gold">
<h2 style="margin:0">📱 SCAN TO JOIN - SHARE THIS LINK!</h2>
<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=http://192.168.100.3:5000" style="width:170px;height:170px;margin:10px">
<p style="font-weight:bold">👉 Clickable Link:</p>
<a href="http://192.168.100.3:5000" style="background:#000;color:gold;padding:10px 15px;display:inline-block;border-radius:10px;text-decoration:none;font-weight:bold;word-break:break-all">http://192.168.100.3:5000</a>
<p style="font-size:12px">Copy this link & paste on WhatsApp / TikTok / Status!<br>Anyone on same WiFi can open it. For public link, use localhost.run</p>
<p>Or on this phone: <a href="/">localhost:5000</a></p>
</div>
'''

@app.route("/")
def home():
    c=db(); songs=c.execute("SELECT * FROM songs ORDER BY vip DESC, id DESC").fetchall()
    artists=c.execute("SELECT * FROM users WHERE role='artist' ORDER BY fans DESC LIMIT 12").fetchall()
    c.close()
    song_html=""
    for s in songs:
        song_html+=f'<div style="background:#111;border:1px solid gold;border-radius:12px;padding:12px;margin:10px"><h3>{s["title"]} - {s["artist"]} {"✅ VIP" if s["vip"] else ""}</h3><p>{s["genre"]} | {s["county"]}</p><audio controls src="/static/uploads/{s["filename"]}" style="width:100%"></audio><br><a href="/follow/{s["artist"]}" style="background:gold;color:#000;padding:8px 15px;display:inline-block;border-radius:20px;text-decoration:none;font-weight:bold;margin-top:8px">❤️ FOLLOW {s["artist"]}</a></div>'
    artist_html=""
    for a in artists:
        artist_html+=f'<div style="background:#111;border-radius:10px;padding:10px;text-align:center"><b>{a["name"]}</b><br><span style="color:gold;font-size:12px">{a["genre"]} | {a["county"]}</span><br>👥 {a["fans"]} Fans | ⭐ {a["points"]} Pts<br><a href="/follow/{a["name"]}" style="background:gold;color:#000;padding:6px 12px;display:inline-block;border-radius:15px;text-decoration:none;font-weight:bold;margin-top:5px">+ FOLLOW</a></div>'
    if not artist_html: artist_html='<p style="text-align:center">No artists yet - Be the FIRST!</p>'
    if not song_html: song_html='<p style="text-align:center;color:#ccc">No songs yet - Be the FIRST to upload!</p>'
    return f'''
<body style="background:#000;color:#fff;font-family:sans-serif;margin:0">
{header()}
{footer_link()}
<div style="text-align:center;padding:5px"><a href="/signup" style="background:gold;color:#000;padding:16px 30px;display:inline-block;border-radius:30px;text-decoration:none;font-weight:bold;font-size:18px">🎤 JOIN NOW - ARTIST OR FAN - FREE</a></div>

<h2 style="color:gold;text-align:center">🔥 Trending In Kenya - Inspiration</h2>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;padding:6px">
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://kelxfy.com/wp-content/uploads/2025/11/Toxic-Lyrikali-Glitter-Freestyle-Lyrics.jpg" style="width:100%;height:140px;object-fit:cover"><p><b>Toxic Lyrikali</b><br><span style="color:gold;font-size:12px">Hip Hop</span></p></div>
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://cdn.radioafrica.digital/image/2025/01/3c74ccbb-9f71-46fe-a644-02d167401eae.jpeg" style="width:100%;height:140px;object-fit:cover"><p><b>Kapitani</b><br><span style="color:gold;font-size:12px">Arbantone</span></p></div>
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://biggestkaka.co.ke/wp-content/uploads/2018/08/Khaligraph-Jones-showing-off-his-tats-rockng-a-mavin.jpg" style="width:100%;height:140px;object-fit:cover"><p><b>Khaligraph</b><br><span style="color:gold;font-size:12px">Rap King</span></p></div>
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://image.okayafrica.com/229936.webp?imageId=229936&width=960&height=642&format=jpg" style="width:100%;height:140px;object-fit:cover"><p><b>Bien</b><br><span style="color:gold;font-size:12px">Afrobeats</span></p></div>
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://businesstoday.co.ke/wp-content/uploads/2021/02/nadia-mukami-34-1024x715.jpg" style="width:100%;height:140px;object-fit:cover"><p><b>Nadia Mukami</b><br><span style="color:gold;font-size:12px">Pop Queen</span></p></div>
<div style="background:#111;border-radius:10px;overflow:hidden;text-align:center"><img src="https://k24.digital/wp-content/uploads/2025/04/FotoJet-63-600x380.jpg" style="width:100%;height:140px;object-fit:cover"><p><b>Mejja</b><br><span style="color:gold;font-size:12px">Gengetone</span></p></div>
</div>

<h2 style="color:gold;text-align:center">🏆 Rewards For Artists - Earn Points!</h2>
<div style="background:#111;margin:10px;padding:15px;border-radius:12px;border:1px solid gold">
<p>✅ Sign Up = <b>+10 Pts</b> &nbsp; ✅ Upload Song = <b>+50 Pts</b> &nbsp; ✅ Get 1 Fan = <b>+20 Pts</b><br>✅ 100 Pts = <b>Top of Homepage</b> &nbsp; ✅ 300 Pts = <b>Verified Badge ✅</b> &nbsp; ✅ 500 Pts = <b>FREE VIP 1 Week</b><br>✅ Top Artist of Month = <b>Shoutout on WhatsApp + TikTok</b></p>
<div style="text-align:center"><a href="/rewards" style="background:gold;color:#000;padding:10px 20px;border-radius:20px;text-decoration:none;font-weight:bold">See Full Rewards →</a></div>
</div>

<h2 style="color:gold;text-align:center">🎤 New Artists On WULI V JARKATA</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:8px">{artist_html}</div>

<h2 style="color:gold;text-align:center">🎧 Latest Songs</h2>{song_html}

<h2 style="color:gold;text-align:center">🗺️ All 47 Counties - Find Artists Near You</h2>
<p style="text-align:center;color:#ccc;font-size:13px">Tap your county to see artists from there</p>
<div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;padding:10px">{counties_grid()}</div>

<div style="background:#111;margin:15px;padding:15px;border-radius:12px;text-align:center"><h3 style="color:gold">Are You A Fan? ❤️</h3><p>Sign up as FAN - Follow your favourite new artists, get notified when they drop songs, vote for them!</p><a href="/signup" style="background:#fff;color:#000;padding:12px 25px;display:inline-block;border-radius:20px;text-decoration:none;font-weight:bold">JOIN AS FAN - FREE</a></div>
</body>
'''

@app.route("/signup")
def signup_choice():
    return f'''<body style="background:#000;color:#fff;font-family:sans-serif;text-align:center;padding:20px">{header()}
<h2 style="color:gold">Who Are You?</h2>
<a href="/signup/artist" style="background:gold;color:#000;display:block;padding:20px;margin:15px;border-radius:15px;text-decoration:none"><h2>🎤 I'M AN ARTIST</h2><p>Upload songs, gain fans, earn rewards, get discovered</p></a>
<a href="/signup/fan" style="background:#fff;color:#000;display:block;padding:20px;margin:15px;border-radius:15px;text-decoration:none"><h2>❤️ I'M A FAN</h2><p>Follow artists, discover new Kenyan music, vote</p></a>
</body>'''

@app.route("/signup/<role>", methods=["GET","POST"])
def signup(role):
    if request.method=="POST":
        name=request.form.get("name"); phone=request.form.get("phone"); county=request.form.get("county"); genre=request.form.get("genre","Fan"); pw=request.form.get("password")
        c=db(); c.execute("INSERT INTO users(name,phone,county,role,genre,password,points) VALUES(?,?,?,?,?,?,10)",(name,phone,county,role,genre,pw)); c.commit(); c.close()
        session["user"]=name; session["role"]=role
        return redirect("/dashboard")
    return f'''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px">{header()}
<h2 style="color:gold;text-align:center">Sign Up As {role.upper()} - FREE</h2>
<form method="post" style="background:#111;padding:20px;border-radius:12px">
<input name="name" placeholder="Your Name / Stage Name" required style="width:100%;padding:12px;margin:8px 0;border-radius:8px"><br>
<input name="phone" placeholder="Phone / WhatsApp e.g 0712345678" required style="width:100%;padding:12px;margin:8px 0;border-radius:8px"><br>
<select name="county" style="width:100%;padding:12px;margin:8px 0;border-radius:8px"><option>Select Your County</option>{counties_options()}</select><br>
{'<input name="genre" placeholder="Your Genre e.g Arbantone, Gengetone, Gospel, Drill" style="width:100%;padding:12px;margin:8px 0;border-radius:8px"><br>' if role=="artist" else ""}
<input name="password" type="password" placeholder="Create Password" required style="width:100%;padding:12px;margin:8px 0;border-radius:8px"><br>
<button style="background:gold;color:#000;padding:15px;width:100%;border:none;border-radius:25px;font-weight:bold;font-size:18px">CREATE ACCOUNT +10 PTS 🎉</button>
</form><p style="text-align:center">Already have account? <a href="/login" style="color:gold">Login</a></p></body>'''

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        c=db(); u=c.execute("SELECT * FROM users WHERE LOWER(TRIM(name))=LOWER(TRIM(?)) AND password=TRIM(?)",(request.form.get("name",""),request.form.get("password",""))).fetchone(); c.close()
        if u: session["user"]=u["name"]; session["role"]=u["role"]; return redirect("/dashboard")
        return "Wrong login! <a href='/login'>Try again</a>"
    return f'''<body style="background:#000;color:#fff;padding:20px;font-family:sans-serif">{header()}<h2 style="color:gold;text-align:center">Login</h2><form method="post" style="background:#111;padding:20px;border-radius:12px"><input name="name" placeholder="Name" style="width:100%;padding:12px;margin:8px 0"><input name="password" type="password" placeholder="Password" style="width:100%;padding:12px;margin:8px 0"><button style="background:gold;padding:15px;width:100%;border-radius:25px;font-weight:bold">LOGIN</button></form></body>'''

@app.route("/dashboard", methods=["GET","POST"])
def dash():
    if "user" not in session: return redirect("/login")
    if request.method=="POST":
        f=request.files.get("song"); title=request.form.get("title"); genre=request.form.get("genre"); county=request.form.get("county")
        if f:
            fn=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fn))
            c=db(); c.execute("INSERT INTO songs(title,artist,genre,county,filename) VALUES(?,?,?,?,?)",(title,session["user"],genre,county,fn)); c.execute("UPDATE users SET points=points+50 WHERE name=?",(session["user"],)); c.execute("INSERT INTO rewards(artist,action,points) VALUES(?,?,50)",(session["user"],"Upload Song")); c.commit(); c.close()
            return redirect("/")
    c=db(); me=c.execute("SELECT * FROM users WHERE name=?",(session["user"],)).fetchone(); fans=c.execute("SELECT COUNT(*) as n FROM follows WHERE artist=?",(session["user"],)).fetchone()["n"]; c.close()
    upload = f'''<h3 style="color:gold">🎤 Upload Song +50 Pts</h3><form method="post" enctype="multipart/form-data" style="background:#111;padding:15px;border-radius:12px"><input name="title" placeholder="Song Title" required style="width:100%;padding:12px;margin:5px 0"><input name="genre" placeholder="Genre" style="width:100%;padding:12px;margin:5px 0"><select name="county" style="width:100%;padding:12px;margin:5px 0">{counties_options()}</select><input type="file" name="song" accept=".mp3,.wav,.m4a" required style="width:100%;margin:10px 0"><button style="background:gold;padding:12px;width:100%;border-radius:20px;font-weight:bold">UPLOAD SONG</button></form>''' if session.get("role")=="artist" else f'''<p>❤️ You are a FAN! Go follow artists on homepage and discover music!</p><a href="/" style="background:gold;color:#000;padding:12px 20px;border-radius:20px;text-decoration:none;font-weight:bold">Browse Artists</a>'''
    return f'''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px">{header()}<h2 style="color:gold">Welcome {session["user"]} ({session.get("role")})</h2><p>👥 Fans: {fans} | ⭐ Points: {me["points"] if me else 0} | 📍 {me["county"] if me else ""}</p>{upload}<br><a href="/rewards" style="color:gold">See My Rewards →</a> | <a href="/vip" style="color:gold">Go VIP</a></body>'''

@app.route("/follow/<artist>")
def follow(artist):
    fan=session.get("user","Guest Fan")
    c=db()
    ex=c.execute("SELECT * FROM follows WHERE fan=? AND artist=?",(fan,artist)).fetchone()
    if not ex:
        c.execute("INSERT INTO follows(fan,artist) VALUES(?,?)",(fan,artist)); c.execute("UPDATE users SET fans=fans+1, points=points+20 WHERE name=?",(artist,)); c.execute("INSERT INTO rewards(artist,action,points) VALUES(?,?,20)",(artist,f"New Fan: {fan}"))
        c.commit()
    c.close(); return redirect("/")

@app.route("/county/<name>")
def county(name):
    c=db(); arts=c.execute("SELECT * FROM users WHERE county=? AND role='artist'",(name,)).fetchall(); songs=c.execute("SELECT * FROM songs WHERE county=?",(name,)).fetchall(); c.close()
    h="".join([f'<p><b>{a["name"]}</b> - {a["genre"]} - 👥 {a["fans"]} fans <a href="/follow/{a["name"]}" style="color:gold">+ FOLLOW</a></p>' for a in arts]) or "<p>No artists yet in this county - Be the FIRST!</p>"
    s="".join([f'<p><b>{x["title"]}</b> - {x["artist"]}<br><audio controls src="/static/uploads/{x["filename"]}" style="width:100%"></audio></p>' for x in songs])
    return f'''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px">{header()}<h2 style="color:gold">🎤 Artists in {name} County</h2>{h}<h3 style="color:gold">Songs from {name}</h3>{s}<br><a href="/signup" style="background:gold;color:#000;padding:12px 20px;border-radius:20px;text-decoration:none;font-weight:bold">Join {name} - FREE</a></body>'''

@app.route("/rewards")
def rewards():
    c=db(); top=c.execute("SELECT * FROM users WHERE role='artist' ORDER BY points DESC LIMIT 10").fetchall(); c.close()
    rows="".join([f'<p><b>{i+1}. {a["name"]}</b> - {a["county"]} - ⭐ {a["points"]} Pts - 👥 {a["fans"]} Fans</p>' for i,a in enumerate(top)])
    return f'''<body style="background:#000;color:#fff;font-family:sans-serif;padding:20px">{header()}<h2 style="color:gold;text-align:center">🏆 REWARDS - How To Earn</h2>
<div style="background:#111;padding:15px;border-radius:12px;border:1px solid gold">
<p>🎉 Sign Up = +10 Pts<br>🎤 Upload Song = +50 Pts<br>❤️ Each New Fan = +20 Pts<br>📱 Share Your Link = +15 Pts<br>🏆 100 Pts = Top of Homepage for 7 Days<br>✅ 300 Pts = Verified Badge + Shoutout<br>⭐ 500 Pts = FREE VIP for 1 Week<br>👑 TOP ARTIST OF MONTH = WhatsApp + TikTok Promo + Interview</p></div>
<h3 style="color:gold">Top Artists Leaderboard</h3>{rows or "<p>No artists yet</p>"}<br><a href="/signup" style="background:gold;color:#000;padding:12px 20px;border-radius:20px;text-decoration:none;font-weight:bold">Join & Earn Points</a></body>'''

@app.route("/vip")
def vip():
    return header() + "<h2 style='color:gold;text-align:center'>VIP - 100 KSh</h2><div style='background:#111;padding:20px;border-radius:12px;border:2px solid gold;text-align:center'><p>Top of Homepage<br>Verified Badge<br>More Fans Faster</p><p>Pay via M-Pesa Till: <b>YOUR TILL</b></p><p>WhatsApp proof to <b>YOUR NUMBER</b></p></div>"


@app.route('/artist/<artist_name>')
def artist_page(artist_name):
    name = artist_name.replace('-',' ').replace('_',' ').lower()
    all_songs = []
    for var in ['SONGS','songs','MUSIC','music','tracks']:
        if var in globals():
            all_songs = globals()[var]
            break
    result = []
    for s in all_songs:
        if isinstance(s, dict):
            a = str(s.get('artist','')).lower()
            if name in a or a in name:
                result.append(s)
    return render_template('artist.html', artist=artist_name, songs=result)
@app.route('/artist')
def artist_list():
    return redirect('/')

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
