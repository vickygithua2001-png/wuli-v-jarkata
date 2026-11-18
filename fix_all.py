import pathlib, os
WHATSAPP = "https://chat.whatsapp.com/BfhIWHs2cYYGBHearOhFA5"
p = pathlib.Path("app.py")
code = p.read_text()
# 1. Worldwide access
if "0.0.0.0" not in code:
    code = code.replace("app.run(debug=True)", "import os\napp.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))")
    code = code.replace("app.run()", "import os\napp.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))")
# 2. Fix upload folder + crash
if "UPLOAD_FOLDER" not in code:
    code = code.replace("app = Flask(__name__)", "app = Flask(__name__)\napp.config['UPLOAD_FOLDER']='uploads'\napp.config['MAX_CONTENT_LENGTH']=50*1024*1024\nos.makedirs('uploads', exist_ok=True)")
# 3. Fix artist page
if "/artist/<artist_name>" not in code:
    fix = '''
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
'''
    if "if __name__" in code:
        code = code.replace("if __name__", fix + "\nif __name__")
    else:
        code += fix
p.write_text(code)
print("app.py FIXED")

# 4. Create artist.html
os.makedirs("templates", exist_ok=True)
pathlib.Path("templates/artist.html").write_text('<h1 style="color:white">{{ artist }}</h1><a href="/" style="color:yellow">← Back</a>{% for s in songs %}<p style="color:white">{{ s.title }} - {{ s.artist }}</p>{% else %}<p style="color:white">No songs yet for {{ artist }}</p>{% endfor %}')
print("artist.html CREATED")

# 5. WhatsApp + 47 Counties + fix upload form
counties = ["Mombasa","Kwale","Kilifi","Tana River","Lamu","Taita-Taveta","Garissa","Wajir","Mandera","Marsabit","Isiolo","Meru","Tharaka-Nithi","Embu","Kitui","Machakos","Makueni","Nyandarua","Nyeri","Kirinyaga","Murang'a","Kiambu","Turkana","West Pokot","Samburu","Trans Nzoia","Uasin Gishu","Elgeyo-Marakwet","Nandi","Baringo","Laikipia","Nakuru","Narok","Kajiado","Kericho","Bomet","Kakamega","Vihiga","Bungoma","Busia","Siaya","Kisumu","Homa Bay","Migori","Kisii","Nyamira","Nairobi"]
options = ''.join([f'<option value="{c}">{c}</option>' for c in counties])
banner = f'<div style="background:#25D366; padding:14px; text-align:center; border-radius:12px; margin:10px;"><b style="color:white; font-size:17px;">🇰🇪 WULI V JARKATA - ALL 47 COUNTIES</b><br><a href="{WHATSAPP}" target="_blank" style="display:inline-block; background:white; color:#075E54; padding:11px 20px; border-radius:25px; font-weight:bold; text-decoration:none; margin-top:10px;">💬 Join Wuli v WhatsApp Group</a><p style="color:white; font-size:13px;">Artists from Mombasa to Nairobi - Connect, Collab, Drop Music!</p><form action="/" method="get"><select name="county" onchange="this.form.submit()" style="padding:9px; border-radius:20px; width:92%;"><option value="">🌍 All 47 Counties</option>{options}</select></form></div>'
for html in pathlib.Path("templates").glob("*.html"):
    t = html.read_text()
    if "WULI V JARKATA - ALL 47 COUNTIES" not in t:
        t = t.replace("<body>", "<body>\n"+banner, 1) if "<body>" in t else banner+t
        html.write_text(t)
    if "<form" in t and "enctype" not in t:
        t2 = html.read_text().replace("<form", '<form enctype="multipart/form-data"', 1)
        html.write_text(t2)
print("DONE! ALL FIXED")
