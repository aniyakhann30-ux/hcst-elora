"""HCST Elora - The Art of a Connected Campus (single-file Streamlit app).

Room numbers, timings and faculty details are SAMPLE data. Update LOC_SEED below, or use
Admin > Places after logging in. Google Maps is used only on the 'Reach HCST' page and the
Home page, to travel to the college from your current location.
"""
import re
import sqlite3
import difflib
import hashlib
import hmac
import html
import secrets as pysecrets
from datetime import date, datetime, timedelta
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ------------------------------------------------------------------ CONFIG
APP_NAME = "HCST Elora"
TAGLINE = "The Art of a Connected Campus"
COLLEGE = "Hindustan College of Science and Technology"
COLLEGE_QUERY = "Hindustan College of Science and Technology, Farah, Mathura, Uttar Pradesh"
DB_PATH = "hcst_elora.db"
DEMO_NOTE = "Demo data - not an actual HCST faculty or contact."

st.set_page_config(page_title="HCST Elora", page_icon="🎓", layout="wide")

st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
html, body, .stApp, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(1100px 480px at 90% -8%, rgba(27,153,139,.12), transparent 60%),
       radial-gradient(900px 420px at -10% 8%, rgba(201,162,39,.12), transparent 60%), #FAF7F2;}
.block-container{padding-top:1.4rem;max-width:1200px;animation:fadeUp .5s ease both;}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(255,255,255,.7)}70%{box-shadow:0 0 0 9px rgba(255,255,255,0)}100%{box-shadow:0 0 0 0 rgba(255,255,255,0)}}
h1,h2,h3{font-family:'Playfair Display',serif !important;color:#0B1F3A;letter-spacing:.2px;}

/* hero */
.hero{background:linear-gradient(120deg,#0B1F3A,#13335C,#1B998B,#13335C);background-size:300% 300%;animation:flow 16s ease infinite;
      padding:2rem 2.2rem;border-radius:22px;margin-bottom:1rem;position:relative;overflow:hidden;box-shadow:0 14px 34px rgba(11,31,58,.25);}
.hero:after{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;
            background:radial-gradient(circle,rgba(201,162,39,.55),transparent 70%);}
.hero h1,.hero h2{color:#fff !important;margin:.35rem 0 0 0;}
.hero h1{font-size:2.2rem;}
.hero h2{font-size:1.25rem;font-weight:600;opacity:.92;}
.hero p{margin:.5rem 0 0 0;color:#E6EEF8 !important;}
.chip{display:inline-flex;align-items:center;gap:.45rem;background:rgba(255,255,255,.14);color:#fff;padding:.25rem .7rem;border-radius:999px;font-size:.8rem;backdrop-filter:blur(4px);}
.live{width:8px;height:8px;border-radius:50%;background:#7CFFB2;animation:pulse 2s infinite;display:inline-block;}
.ticker{background:#fff;border:1px solid #eadfc4;border-left:5px solid #C9A227;padding:.65rem 1rem;border-radius:12px;margin-bottom:1rem;color:#1c2733;}
.demo{font-size:.8rem;color:#8a5a00;background:#fff4d6;padding:.2rem .55rem;border-radius:8px;display:inline-block;}

/* stat cards */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:.4rem 0 1rem 0;}
.stat{background:#fff;border:1px solid #eadfc4;border-radius:16px;padding:1rem;text-align:center;transition:transform .25s, box-shadow .25s;}
.stat:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(11,31,58,.14);}
.stat b{display:block;font-family:'Playfair Display',serif;font-size:1.9rem;color:#0B1F3A;}
.stat span{color:#5b6b7c;font-size:.85rem;}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr);} .hero h1{font-size:1.6rem;}}

/* cards (st.container border=True) */
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px !important;background:#fff;border:1px solid #eadfc4 !important;
    box-shadow:0 2px 10px rgba(11,31,58,.05);transition:transform .25s ease, box-shadow .25s ease;}
[data-testid="stVerticalBlockBorderWrapper"]:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(11,31,58,.13);}

/* buttons */
.stButton>button,.stLinkButton a,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:999px !important;border:1px solid #C9A227 !important;
    background:#fff;color:#0B1F3A !important;font-weight:600;transition:all .25s ease;}
.stButton>button:hover,.stLinkButton a:hover,.stFormSubmitButton>button:hover{background:linear-gradient(135deg,#C9A227,#E8CF7A);transform:translateY(-2px);box-shadow:0 8px 18px rgba(201,162,39,.35);}
button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stFormSubmitButton>button[kind="primaryFormSubmit"]{background:linear-gradient(135deg,#0B1F3A,#1B998B) !important;color:#fff !important;border:none !important;}
button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primaryFormSubmit"]:hover{filter:brightness(1.12);box-shadow:0 8px 20px rgba(27,153,139,.4);}

/* inputs */
.stTextInput input,.stTextArea textarea,.stDateInput input,.stNumberInput input{border-radius:12px !important;}
div[data-baseweb="select"]>div{border-radius:12px !important;}
.stTextInput input:focus,.stTextArea textarea:focus{box-shadow:0 0 0 2px rgba(27,153,139,.35) !important;}

/* tabs */
.stTabs [data-baseweb="tab"]{font-weight:600;border-radius:10px 10px 0 0;transition:background .2s;}
.stTabs [data-baseweb="tab"]:hover{background:rgba(201,162,39,.12);}
.stTabs [data-baseweb="tab-highlight"]{background:#C9A227 !important;}

/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B1F3A 0%,#13335C 100%);}
[data-testid="stSidebar"] *{color:#E8EEF7 !important;}
[data-testid="stSidebar"] .brand{font-family:'Playfair Display',serif;font-size:1.25rem;line-height:1.2;padding:.3rem .2rem 1rem .2rem;}
[data-testid="stSidebar"] .brand span{font-family:'Inter',sans-serif;font-size:.78rem;opacity:.75;}
[data-testid="stSidebar"] .userchip{background:rgba(255,255,255,.1);padding:.55rem .8rem;border-radius:12px;margin-bottom:.8rem;font-size:.9rem;}
[data-testid="stSidebar"] div[role="radiogroup"] label{padding:.45rem .7rem;border-radius:10px;margin:2px 0;transition:all .2s ease;cursor:pointer;}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(255,255,255,.12);transform:translateX(5px);}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:rgba(201,162,39,.28);border-left:3px solid #C9A227;}
[data-testid="stSidebar"] .stButton>button{background:transparent !important;border:1px solid rgba(255,255,255,.55) !important;color:#fff !important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(201,162,39,.35) !important;}
.stAlert{border-radius:14px;}
</style>""",
    unsafe_allow_html=True,
)


EXTRA_CSS = """
.roombadge{display:flex;flex-wrap:wrap;gap:8px;margin:.2rem 0 .9rem 0;}
.roombadge span{background:#FFF4D6;border:1px solid #E6D28A;color:#5A4300;padding:.32rem .85rem;border-radius:999px;font-weight:600;font-size:.92rem;}
.steps{counter-reset:s;list-style:none;padding:0;margin:.2rem 0 1rem 0;}
.steps li{counter-increment:s;position:relative;padding:.35rem 0 .35rem 2.6rem;color:#1C2733;}
.steps li:before{content:counter(s);position:absolute;left:0;top:.25rem;width:1.9rem;height:1.9rem;border-radius:50%;background:linear-gradient(135deg,#0B1F3A,#1B998B);color:#fff;font-weight:600;text-align:center;line-height:1.9rem;}
"""
st.markdown("<style>" + EXTRA_CSS + "</style>", unsafe_allow_html=True)


# ------------------------------------------------------------------ DATABASE
@st.cache_resource
def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def qdf(sql, params=()):
    return pd.read_sql_query(sql, conn(), params=params)


def run(sql, params=()):
    c = conn()
    cur = c.execute(sql, params)
    c.commit()
    return cur.lastrowid


T = "Sample: 9:00 AM - 5:00 PM (to be verified)"
MAIN, BA, BB = "Main Block", "Academic Block A", "Academic Block B"
OFF, DEP, FAC, HOS, ENT = "Offices & Administration", "Departments", "Campus Facility", "Hostel", "Entry"
# name, category, building, floor, room, description, timings, keywords   (ALL SAMPLE - edit to match the real campus)
LOC_SEED = [
    ("Main Gate", ENT, "Main Entrance", "Ground", "-", "Main entrance of the campus. Security desk is here.", "Open daily (to be verified)", "entrance gate security start"),
    ("Reception", OFF, MAIN, "Ground", "G-01", "Front desk for visitors and general enquiries.", T, "front desk enquiry help visitor"),
    ("Admission Cell", OFF, MAIN, "Ground", "G-02", "Admission enquiries, counselling and application guidance.", T, "admission admissions enquiry counselling new student apply"),
    ("Document Verification Office", OFF, MAIN, "Ground", "G-03", "Verification of admission documents.", T, "document verification certificate documents admission"),
    ("Fee Office", OFF, MAIN, "Ground", "G-04", "Fee payment and fee-related enquiries.", T, "fee fees payment accounts cash admission fee"),
    ("Examination Cell", OFF, MAIN, "Ground", "G-05", "Examinations, results and related queries.", T, "exam examination results marksheet"),
    ("Medical Room", FAC, MAIN, "Ground", "G-06", "First aid and basic medical assistance.", T, "medical doctor first aid health clinic"),
    ("Director's Office", OFF, MAIN, "First", "101", "Office of the Director.", T, "director principal head"),
    ("Dean of Academics", OFF, MAIN, "First", "102", "Dean of Academics office - academic policy and enquiries.", T, "dean academics academic enquiry"),
    ("PDP Department", OFF, MAIN, "First", "103", "Personality Development Programme - soft skills and career readiness.", T, "pdp personality development soft skills communication"),
    ("Training & Placement (T&P) Department", OFF, MAIN, "First", "104", "Placement drives, internships and recruiter coordination.", T, "tnp t&p training placement placements job recruiter internship drive"),
    ("Computer Science Department", DEP, BA, "First", "A-101", "Department of Computer Science and Engineering.", T, "computer science cse department programming it"),
    ("Data Science Department", DEP, BA, "First", "A-102", "Department of Computer Science and Engineering (Data Science).", T, "data science ds analytics department"),
    ("AI & ML Department", DEP, BA, "First", "A-103", "Department of Artificial Intelligence and Machine Learning.", T, "ai ml artificial intelligence machine learning department"),
    ("Computer Labs", DEP, BA, "Ground", "A-G01 to A-G04", "Computer laboratories used by CS, Data Science and AI & ML.", "Sample: as per lab schedule", "computer lab labs laboratory"),
    ("Seminar Hall", FAC, BA, "Second", "A-201", "Seminars, guest lectures and workshops.", "As per event schedule", "seminar hall lecture workshop"),
    ("Civil Engineering Department", DEP, BB, "Ground", "B-G01", "Department of Civil Engineering.", T, "civil engineering department"),
    ("Mechanical Engineering Department", DEP, BB, "Ground", "B-G02", "Department of Mechanical Engineering.", T, "mechanical engineering department mech"),
    ("Electrical Engineering Department", DEP, BB, "First", "B-101", "Department of Electrical Engineering.", T, "electrical engineering department ee"),
    ("Electronics & Communication Department", DEP, BB, "First", "B-102", "Department of Electronics and Communication Engineering.", T, "electronics communication ece department"),
    ("Applied Sciences & Humanities", DEP, BB, "Second", "B-201", "First-year science, mathematics and humanities faculty.", T, "applied sciences humanities physics chemistry maths first year"),
    ("Library", FAC, "Central Library Building", "Ground", "LIB-G1", "Books, journals, reading room and digital resources.", "Sample: 8:30 AM - 6:00 PM (to be verified)", "library books reading study journals"),
    ("Cafeteria", FAC, "Cafeteria Block", "Ground", "-", "Food, snacks and beverages.", "Sample: 8:00 AM - 6:00 PM (to be verified)", "cafeteria canteen food mess snacks tea coffee"),
    ("Auditorium", FAC, "Auditorium Building", "Ground", "-", "Large events, orientation programmes and cultural functions.", "As per event schedule", "auditorium hall events orientation function"),
    ("Sports Ground", FAC, "Open Ground", "Ground", "-", "Grounds and sports facilities.", "Sample: 6:00 AM - 7:00 PM (to be verified)", "sports ground playground cricket football game"),
    ("Parking", FAC, "Parking Area", "Ground", "-", "Vehicle parking for students, staff and visitors.", "Open daily (to be verified)", "parking vehicle bike car"),
    ("Transport Office", FAC, "Parking Area", "Ground", "TO-01", "College bus and transport enquiries.", T, "transport bus office route"),
    ("Drinking Water Point", FAC, MAIN, "Ground", "-", "Drinking water point near the ground-floor corridor.", "Open daily (to be verified)", "drinking water ro"),
    ("Washrooms", FAC, MAIN, "Ground", "-", "Washrooms on every floor of each block.", "Open daily (to be verified)", "washroom toilet restroom"),
    ("Hostel Office", HOS, "Hostel Area", "Ground", "H-01", "Hostel admissions, rooms and rules enquiries.", T, "hostel office warden accommodation room"),
    ("Boys' Hostel", HOS, "Hostel Area", "Ground", "-", "Residence for male students.", "-", "boys boy hostel male residence"),
    ("Girls' Hostel", HOS, "Hostel Area", "Ground", "-", "Residence for female students.", "-", "girls girl ladies women hostel female residence"),
]

FAC_SEED = [
    # name, designation, department, cabin, timings, responsibilities, location_name
    ("Dr. Aarav Sharma", "Professor & HOD", "Computer Science", "A-101", "Mon-Fri 11:00-13:00", "Department administration, curriculum, project allocation", "Computer Science Department"),
    ("Dr. Meera Kapoor", "Associate Professor & HOD", "Data Science", "A-102", "Mon-Thu 14:00-16:00", "Data science electives, research mentoring", "Data Science Department"),
    ("Prof. Rohan Verma", "Assistant Professor", "AI & ML", "A-103", "Tue-Fri 10:00-12:00", "Machine learning labs, student mentoring", "AI & ML Department"),
    ("Dr. Nisha Rao", "Professor & HOD", "Civil Engineering", "B-G01", "Mon-Fri 12:00-14:00", "Structural engineering, department administration", "Civil Engineering Department"),
    ("Prof. Vikram Sethi", "Associate Professor & HOD", "Mechanical Engineering", "B-G02", "Mon-Fri 11:00-13:00", "Thermal engineering, workshop coordination", "Mechanical Engineering Department"),
    ("Dr. Kabir Malhotra", "Dean of Academics", "Administration", "102", "Mon-Fri 10:30-12:30", "Academic policies, academic enquiries, time-tables", "Dean of Academics"),
    ("Dr. Ishita Menon", "Director", "Administration", "101", "By appointment", "Institute administration and strategy", "Director's Office"),
    ("Mr. Aditya Bose", "Admission In-charge", "Admission Cell", "G-02", "Mon-Sat 10:00-16:00", "Admission enquiries, counselling, process guidance", "Admission Cell"),
    ("Ms. Tanvi Joshi", "Placement Coordinator", "Training & Placement", "104", "Mon-Fri 10:00-16:00", "Placement drives, recruiter coordination, internships", "Training & Placement (T&P) Department"),
    ("Dr. Sameer Khanna", "Controller of Examinations", "Examination Cell", "G-05", "Mon-Fri 11:00-15:00", "Examination schedules and results", "Examination Cell"),
    ("Ms. Pooja Nair", "PDP Faculty", "PDP", "103", "Mon-Fri 11:00-15:00", "Soft skills, communication and aptitude training", "PDP Department"),
]


def init_db():
    c = conn()
    c.executescript(
        """
    CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY, name TEXT UNIQUE, category TEXT, building TEXT,
        floor TEXT, room TEXT, description TEXT, timings TEXT, keywords TEXT, verified INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS faculty(id INTEGER PRIMARY KEY, name TEXT, designation TEXT, department TEXT, cabin TEXT,
        timings TEXT, responsibilities TEXT, location_name TEXT, email TEXT, phone TEXT);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, phone TEXT, role TEXT,
        salt TEXT, pw_hash TEXT, created TEXT);
    CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT, faculty_id INTEGER,
        purpose TEXT, details TEXT, appt_date TEXT, appt_time TEXT, status TEXT DEFAULT 'Pending', created TEXT, user_id INTEGER);
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, title TEXT, category TEXT, event_date TEXT, event_time TEXT,
        location_name TEXT, description TEXT);
    CREATE TABLE IF NOT EXISTS lost_found(id INTEGER PRIMARY KEY, kind TEXT, item TEXT, description TEXT, where_text TEXT,
        reporter TEXT, contact TEXT, status TEXT DEFAULT 'Open', claimant TEXT, claim_note TEXT, created TEXT, user_id INTEGER);
    """
    )
    if c.execute("SELECT COUNT(*) FROM locations").fetchone()[0] == 0:
        for n, cat, b, fl, rm, d, t, k in LOC_SEED:
            c.execute("INSERT INTO locations(name,category,building,floor,room,description,timings,keywords,verified) VALUES(?,?,?,?,?,?,?,?,0)",
                      (n, cat, b, fl, rm, d, t, k))
    if c.execute("SELECT COUNT(*) FROM faculty").fetchone()[0] == 0:
        for n, des, dep, cab, tim, resp, loc in FAC_SEED:
            slug = re.sub(r"[^a-z]", "", n.lower())
            c.execute("INSERT INTO faculty(name,designation,department,cabin,timings,responsibilities,location_name,email,phone) VALUES(?,?,?,?,?,?,?,?,?)",
                      (n, des, dep, cab, tim, resp, loc, f"{slug}@demo.example", "+91-00000-00000 (demo)"))
    if c.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
        t0 = date.today()
        ev = [
            ("Orientation Programme for New Students", "Orientation", t0 + timedelta(days=3), "10:00", "Auditorium", "Welcome session for newly admitted students and parents."),
            ("Campus Placement Drive (Demo Company)", "Placement", t0 + timedelta(days=7), "09:30", "Training & Placement (T&P) Department", "Sample placement drive; registration at T&P."),
            ("Guest Lecture: Careers in AI", "Seminar", t0 + timedelta(days=10), "14:00", "Seminar Hall", "Sample seminar on emerging technologies."),
            ("Inter-Department Sports Meet", "Sports", t0 + timedelta(days=15), "08:00", "Sports Ground", "Cricket, football and athletics."),
            ("Annual Cultural Evening", "Cultural", t0 + timedelta(days=25), "17:00", "Auditorium", "Music, dance and drama performances."),
            ("Notice: Fee Payment Window", "Notice", t0 + timedelta(days=5), "-", "Fee Office", "Sample notice - verify actual dates with the Fee Office."),
        ]
        for e in ev:
            c.execute("INSERT INTO events(title,category,event_date,event_time,location_name,description) VALUES(?,?,?,?,?,?)",
                      (e[0], e[1], e[2].isoformat(), e[3], e[4], e[5]))
    c.commit()


init_db()


# ------------------------------------------------------------------ AUTH
REQUIRE_LOGIN_FOR_ACTIONS = True  # set False to let anyone book / report without an account
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_pw(pw, salt=None):
    salt = salt or pysecrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), 150_000).hex()
    return salt, h


def current_user():
    return st.session_state.get("user")


def login_required(msg):
    if current_user() or not REQUIRE_LOGIN_FOR_ACTIONS:
        return True
    st.warning(msg)
    st.button("🔑 Login / Sign up", on_click=lambda: st.session_state.update(page="Account"), type="primary", key="need_login_" + str(abs(hash(msg))))
    return False



# ------------------------------------------------------------------ HELPERS
FLOOR_ORDER = {"Ground": 0, "First": 1, "Second": 2, "Third": 3}


def locations():
    return qdf("SELECT * FROM locations ORDER BY name")


def loc_by_name(name):
    r = qdf("SELECT * FROM locations WHERE name=?", (name,))
    return r.iloc[0] if len(r) else None


def has_room(r):
    return str(r["room"]).strip() not in ("", "-", "—")


def room_text(r):
    return f"Room {r['room']}" if has_room(r) else "No room number"


def place_line(r):
    return f"{r['building']} · {r['floor']} floor" + (f" · Room {r['room']}" if has_room(r) else "")


def goto(page):
    st.session_state["page"] = page


def book_with(fid):
    st.session_state["prefill_fid"] = int(fid)
    st.session_state["page"] = "Book Appointment"


STOP = set("where is the a an to how can i do does what who which of for in on at me my find reach get go tell about please are there it be and or "
           "location locate office handles handle handled need want should room floor".split())


def tokens(text):
    return {t for t in re.findall(r"[a-z0-9&]+", text.lower()) if t not in STOP}


def score_location(q, r):
    qt = tokens(q)
    kt = tokens(r["name"] + " " + r["keywords"] + " " + r["category"])
    s = len(qt & kt)
    for t in qt - kt:
        if len(t) > 3 and difflib.get_close_matches(t, list(kt), n=1, cutoff=0.82):
            s += 0.6
    if q.strip() and q.lower().strip() in r["name"].lower():
        s += 2
    return s


def search_hits(q, locs, limit=6):
    hits = [(score_location(q, r), r["name"]) for _, r in locs.iterrows()]
    hits = [h for h in hits if h[0] > 0]
    hits.sort(key=lambda x: -x[0])
    return [h[1] for h in hits[:limit]]


# ------------------------------------------------------------------ PLACE PANEL
def place_panel(loc):
    st.subheader(loc["name"])
    chips = f"<span>🏢 {html.escape(loc['building'])}</span><span>🪜 {html.escape(loc['floor'])} floor</span>"
    if has_room(loc):
        chips += f"<span>🚪 Room {html.escape(str(loc['room']))}</span>"
    st.markdown(f'<div class="roombadge">{chips}</div>', unsafe_allow_html=True)
    st.write(loc["description"])
    if loc["timings"] not in ("-", ""):
        st.markdown(f"**Timings:** {loc['timings']}")
    if not loc["verified"]:
        st.caption("📍 Room details are sample data pending verification by the college.")

    if loc["name"] != "Main Gate":
        steps = [f"Enter through the <b>Main Gate</b> (ask at Reception if you need help).",
                 f"Head to the <b>{html.escape(loc['building'])}</b>."]
        if loc["floor"] != "Ground" or has_room(loc):
            steps.append(f"Go to the <b>{html.escape(loc['floor'])} floor</b>.")
        if has_room(loc):
            steps.append(f"Look for <b>Room {html.escape(str(loc['room']))}</b> - that is the <b>{html.escape(loc['name'])}</b>.")
        st.markdown("**How to find it**")
        st.markdown('<ol class="steps">' + "".join(f"<li>{s}</li>" for s in steps) + "</ol>", unsafe_allow_html=True)

    fac = qdf("SELECT * FROM faculty WHERE location_name=?", (loc["name"],))
    if len(fac):
        st.markdown("**People here** " + '<span class="demo">demo data</span>', unsafe_allow_html=True)
        for _, f in fac.iterrows():
            st.write(f"• {f['name']} - {f['designation']} (Cabin {f['cabin']})")
    same = locations()
    same = same[(same["building"] == loc["building"]) & (same["floor"] == loc["floor"]) & (same["name"] != loc["name"])]
    if len(same):
        st.markdown(f"**Also on the {loc['floor']} floor of {loc['building']}**")
        for _, r in same.iterrows():
            st.write(f"• {r['name']}" + (f" - Room {r['room']}" if has_room(r) else ""))


# ------------------------------------------------------------------ HOME
def page_home():
    u = current_user()
    hr = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    greet = "Good morning" if hr < 12 else "Good afternoon" if hr < 17 else "Good evening"
    who = f", {html.escape(u['name'].split()[0])}" if u else ""
    st.markdown(
        f"""<div class="hero"><span class="chip"><span class="live"></span> {APP_NAME} · Farah, Mathura</span>
        <h1>{greet}{who} 👋</h1><h2>Welcome to HCST</h2>
        <p>{TAGLINE}. Find any office, department or facility by building, floor and room number.</p></div>""",
        unsafe_allow_html=True)
    nx = qdf("SELECT * FROM events WHERE event_date>=? ORDER BY event_date LIMIT 1", (date.today().isoformat(),))
    if len(nx):
        e = nx.iloc[0]
        st.markdown(f'<div class="ticker">📣 <b>Next up:</b> {html.escape(e["title"])} · {e["event_date"]} · 📍 {html.escape(e["location_name"])}</div>',
                    unsafe_allow_html=True)
    locs = locations()
    q = st.text_input("🔍 Search offices, departments, hostels, facilities", placeholder="e.g. admission, library, girls hostel, civil, AI")
    if q:
        hits = search_hits(q, locs)
        if hits:
            choice = st.radio("Matches", hits, horizontal=True)
            st.session_state["dest"] = int(locs[locs["name"] == choice]["id"].iloc[0])
        else:
            st.warning("No match found. Try another keyword.")
    st.markdown("**Popular destinations**")
    pop = ["Admission Cell", "Training & Placement (T&P) Department", "PDP Department", "Dean of Academics", "Director's Office",
           "Computer Science Department", "Civil Engineering Department", "Mechanical Engineering Department", "Library", "Cafeteria",
           "Boys' Hostel", "Girls' Hostel"]
    cols = st.columns(4)
    for i, n in enumerate(pop):
        r = locs[locs["name"] == n]
        if len(r) and cols[i % 4].button(n.replace(" (T&P)", ""), key=f"pop_{i}", use_container_width=True):
            st.session_state["dest"] = int(r["id"].iloc[0])
    st.divider()
    did = st.session_state.get("dest")
    r = locs[locs["id"] == did] if did else locs.iloc[0:0]
    if len(r):
        place_panel(r.iloc[0])
        return
    nloc = len(locs)
    ndep = int((locs["category"] == DEP).sum())
    nfac = int(qdf("SELECT COUNT(*) AS n FROM faculty").iloc[0]["n"])
    nev = int(qdf("SELECT COUNT(*) AS n FROM events WHERE event_date>=?", (date.today().isoformat(),)).iloc[0]["n"])
    st.markdown(
        f"""<div class="stats"><div class="stat"><b>{nloc}</b><span>Campus places</span></div>
        <div class="stat"><b>{ndep}</b><span>Departments & labs</span></div>
        <div class="stat"><b>{nfac}</b><span>Faculty & staff (demo)</span></div>
        <div class="stat"><b>{nev}</b><span>Upcoming events</span></div></div>""",
        unsafe_allow_html=True)
    qa = st.columns(4)
    for col, (label, pg) in zip(qa, [("🏢 Building guide", "Campus Directory"), ("📅 Book a meeting", "Book Appointment"),
                                      ("💬 Ask HCST", "Ask HCST"), ("🚗 Reach HCST", "Reach HCST")]):
        col.button(label, key="qa_" + pg, on_click=goto, args=(pg,), use_container_width=True)
    st.subheader("📍 HCST on Google Maps")
    components.html(
        f'<iframe src="https://www.google.com/maps?q={quote_plus(COLLEGE_QUERY)}&output=embed" width="100%" height="380" '
        f'style="border:0;border-radius:14px" loading="lazy"></iframe>', height=390)


# ------------------------------------------------------------------ CAMPUS DIRECTORY
def page_directory():
    st.header("🏢 Campus Directory")
    st.caption("Find any place by building, floor and room number. Room details are sample data until verified by the college.")
    locs = locations()
    t1, t2 = st.tabs(["Find a place", "Floor-wise building guide"])
    with t1:
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["All"] + sorted(locs["category"].unique()))
        sub = locs if cat == "All" else locs[locs["category"] == cat]
        name = c2.selectbox("Place", sub["name"])
        place_panel(sub[sub["name"] == name].iloc[0])
    with t2:
        b = st.selectbox("Building", sorted(locs["building"].unique()))
        sub = locs[locs["building"] == b].copy()
        sub["o"] = sub["floor"].map(lambda x: FLOOR_ORDER.get(x, 9))
        sub = sub.sort_values(["o", "room"])
        for fl in sub["floor"].unique():
            g = sub[sub["floor"] == fl]
            with st.container(border=True):
                st.markdown(f"#### {fl} floor")
                show = g[["room", "name", "timings"]].rename(columns={"room": "Room", "name": "Place", "timings": "Timings"})
                st.dataframe(show, hide_index=True, use_container_width=True)
    with st.expander("All places (table)"):
        st.dataframe(locs[["name", "category", "building", "floor", "room", "timings", "verified"]], use_container_width=True, hide_index=True)


# ------------------------------------------------------------------ REACH HCST (Google Maps)
START_POINTS = ["Mathura Junction Railway Station", "Agra Cantt Railway Station", "Vrindavan, Uttar Pradesh", "New Delhi Railway Station"]
TRAVEL = {"Driving": "driving", "Two-wheeler": "two-wheeler", "Public transport": "transit", "Walking": "walking"}


def page_reach():
    st.header("🚗 Reach HCST")
    st.write("Travelling to the college? Use Google Maps from your current location (or any place you choose). "
             "Once you are inside the campus, use the **Campus Directory** to find the building, floor and room.")
    left, right = st.columns([1, 1.3])
    with left:
        mode = st.radio("Starting point", ["📍 My current location", "⌨️ A place I type"])
        origin = ""
        if mode.startswith("⌨️"):
            common = st.selectbox("Quick picks", ["(none)"] + START_POINTS)
            typed = st.text_input("Starting place", placeholder="e.g. my home address, a landmark, a city")
            origin = typed.strip() or ("" if common == "(none)" else common)
        travel = st.selectbox("Travel mode", list(TRAVEL))
        url = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(COLLEGE_QUERY)}&travelmode={TRAVEL[travel]}"
        if origin:
            url += "&origin=" + quote_plus(origin)
        if mode.startswith("⌨️") and not origin:
            st.warning("Type a starting place or pick one above.")
        else:
            st.link_button("🧭 Open directions to HCST in Google Maps", url, type="primary", use_container_width=True)
        if mode.startswith("📍"):
            st.info("Google Maps will use your phone or browser location as the starting point. Please allow location access when it asks.")
        st.link_button("View HCST on Google Maps", "https://www.google.com/maps/search/?api=1&query=" + quote_plus(COLLEGE_QUERY), use_container_width=True)
        st.caption(f"Destination: {COLLEGE_QUERY}")
    with right:
        components.html(
            f'<iframe src="https://www.google.com/maps?q={quote_plus(COLLEGE_QUERY)}&output=embed" width="100%" height="470" '
            f'style="border:0;border-radius:14px" loading="lazy"></iframe>', height=480)


# ------------------------------------------------------------------ VISITOR HELP
JOURNEYS = {
    "New admission": ("Admission Cell → Document Verification → Fee Office", ["Reception", "Admission Cell", "Document Verification Office", "Fee Office", "Hostel Office"]),
    "Placement enquiry": ("T&P Department → Placement Coordinator", ["Reception", "Training & Placement (T&P) Department"]),
    "Academic enquiry": ("Relevant Department → Dean's Office", ["Reception", "Computer Science Department", "Dean of Academics"]),
    "Parent visit": ("Reception → Concerned Department", ["Reception", "Computer Science Department"]),
    "Hostel enquiry": ("Hostel Office → Hostel Building", ["Hostel Office", "Boys' Hostel", "Girls' Hostel"]),
}


def page_visitor():
    st.header("🧭 Visitor Help Centre")
    st.write("Not sure where to begin? Choose your purpose to see which offices to visit, in order, with building, floor and room number.")
    st.table(pd.DataFrame([(k, v[0]) for k, v in JOURNEYS.items()], columns=["Visitor purpose", "Suggested journey"]))
    p = st.selectbox("I am here for…", list(JOURNEYS))
    for i, n in enumerate(JOURNEYS[p][1], 1):
        r = loc_by_name(n)
        if r is None:
            continue
        with st.container(border=True):
            st.markdown(f"**{i}. {r['name']}**  \n🏢 {place_line(r)}  \n{r['description']}")
    st.caption("Coming from outside the campus? Use the **Reach HCST** page to get Google Maps directions to the college.")
    with st.expander("Common questions"):
        st.markdown("- **Where to begin admission?** Admission Cell.\n- **Document verification?** Document Verification Office.\n"
                    "- **Pay admission fees?** Fee Office.\n- **Hostel facilities?** Hostel Office.\n- **Submit forms?** Admission Cell / Reception.")


# ------------------------------------------------------------------ CHAT
def answer(q):
    ql = q.lower()
    if re.search(r"(reach|get to|come to|travel to) (the )?(hcst|college|campus)|my current location|from (my )?(home|city|station)", ql):
        return "To travel to the college, open the **Reach HCST** page. Google Maps will start from your current location (or any place you type) and take you to HCST."
    if re.search(r"appointment|meeting|meet |book", ql):
        return "You can request a meeting from the **Book Appointment** page (login required): choose the person, purpose, date and time. You will get a reference ID to track or cancel the request."
    if re.search(r"^(hello|hi|hey|namaste)\b", ql):
        return "Hello! Ask me where any office, department, hostel or facility is, and I will tell you the building, floor and room."
    if re.search(r"faculty|professor|dr\.|who handles|who is|incharge|in-charge|coordinator|hod", ql):
        qt = tokens(q)
        best, bs = None, 0
        for _, f in qdf("SELECT * FROM faculty").iterrows():
            s = len(qt & tokens(" ".join([f["name"], f["designation"], f["department"], f["responsibilities"]])))
            if s > bs:
                best, bs = f, s
        if best is not None and bs >= 1:
            loc = loc_by_name(best["location_name"])
            where = f" ({place_line(loc)})" if loc is not None else ""
            return (f"**{best['name']}** ({best['designation']}, {best['department']}) - Cabin {best['cabin']}{where}, timings {best['timings']}. "
                    f"Handles: {best['responsibilities']}. _{DEMO_NOTE}_")
    hits = search_hits(q, locations(), limit=1)
    if hits:
        r = loc_by_name(hits[0])
        extra = f" Timings: {r['timings']}." if r["timings"] not in ("-", "") else ""
        return f"**{r['name']}** is in **{r['building']}**, {r['floor']} floor" + (f", **Room {r['room']}**" if has_room(r) else "") + f". {r['description']}{extra}"
    return "Sorry, I couldn't match that to a campus place. Try names like *Admission Cell*, *Library*, *Girls' hostel*, *Civil* or *AI & ML*."


def page_chat():
    st.header("💬 Ask HCST - Campus Chat Assistant")
    st.caption("Answers come from the campus database (keyword matching, no external AI). Try: *Where is the Admission Cell?*")
    if "chat" not in st.session_state:
        st.session_state["chat"] = [("assistant", "Hi! I'm the HCST campus assistant. Ask me where something is, or who handles what.")]
    for role, txt in st.session_state["chat"]:
        with st.chat_message(role):
            st.markdown(txt)
    q = st.chat_input("Ask a question about the campus…")
    if q:
        st.session_state["chat"] += [("user", q), ("assistant", answer(q))]
        st.rerun()
    st.markdown("**Sample questions**")
    for s in ["Where is the Admission Cell?", "Where is the Civil Engineering department?", "Where is the girls' hostel?",
              "Who handles placement-related queries?", "How can I reach the college from my current location?"]:
        if st.button(s, key="sq_" + s):
            st.session_state["chat"] += [("user", s), ("assistant", answer(s))]
            st.rerun()


# ------------------------------------------------------------------ FACULTY
def page_faculty():
    st.header("👩‍🏫 Faculty & Department Connect")
    st.markdown('<span class="demo">All faculty names, photographs, contact details and availability are fictional demonstration data.</span>',
                unsafe_allow_html=True)
    fdf = qdf("SELECT * FROM faculty ORDER BY department, name")
    dept = st.selectbox("Department / Office", ["All"] + sorted(fdf["department"].unique()))
    if dept != "All":
        fdf = fdf[fdf["department"] == dept]
    cols = st.columns(2)
    for i, (_, f) in enumerate(fdf.iterrows()):
        with cols[i % 2].container(border=True):
            st.markdown(f"### 👤 {f['name']}")
            st.caption(f"Sample Faculty · {f['department']}")
            loc = loc_by_name(f["location_name"])
            where = f"  \n**Location:** {place_line(loc)}" if loc is not None else ""
            st.write(f"**Designation:** {f['designation']}  \n**Cabin / room:** {f['cabin']}{where}  \n**Office timings (sample):** {f['timings']}  \n"
                     f"**Responsibilities:** {f['responsibilities']}")
            st.write(f"📧 {f['email']}  \n📞 {f['phone']}")
            st.button("Request appointment", key=f"ap_{f['id']}", on_click=book_with, args=(f["id"],), use_container_width=True)


# ------------------------------------------------------------------ FACILITIES & EVENTS
def page_facilities():
    st.header("🏫 Campus Facilities")
    locs = locations()
    f = locs[locs["category"].isin([FAC, HOS])]
    for _, r in f.iterrows():
        with st.container(border=True):
            st.markdown(f"**{r['name']}**  \n🏢 {place_line(r)}  \n{r['description']}  \n⏰ {r['timings']}")


def page_events():
    st.header("📢 Events & Notices")
    st.caption("Sample events for demonstration.")
    ev = qdf("SELECT * FROM events ORDER BY event_date")
    cat = st.multiselect("Filter", sorted(ev["category"].unique()))
    if cat:
        ev = ev[ev["category"].isin(cat)]
    for _, e in ev.iterrows():
        loc = loc_by_name(e["location_name"])
        where = f"📍 {e['location_name']}" + (f" - {place_line(loc)}" if loc is not None else "")
        with st.container(border=True):
            st.markdown(f"**{e['title']}** · _{e['category']}_  \n📅 {e['event_date']} {e['event_time']}  \n{where}  \n{e['description']}")


def slots_for(fid, d):
    base = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
    taken = qdf("SELECT appt_time FROM appointments WHERE faculty_id=? AND appt_date=? AND status IN ('Pending','Approved')", (int(fid), d.isoformat()))
    return [s for s in base if s not in set(taken["appt_time"])]


def my_appointments_ui(u, prefix):
    mine = qdf("SELECT a.*, f.name AS fname FROM appointments a JOIN faculty f ON f.id=a.faculty_id WHERE a.user_id=? ORDER BY a.id DESC",
               (int(u["id"]),))
    if not len(mine):
        st.info("You have no meeting requests yet.")
        return
    for _, a in mine.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            badge = {"Pending": "🟡", "Approved": "🟢", "Rejected": "🔴", "Cancelled": "⚪"}.get(a["status"], "⚪")
            c1.markdown(f"**APT-{int(a['id']):05d}** · {a['fname']}  \n📅 {a['appt_date']} {a['appt_time']} · {a['purpose']}  \n{badge} **{a['status']}**")
            if a["status"] in ("Pending", "Approved") and c2.button("Cancel", key=f"{prefix}_c_{int(a['id'])}"):
                run("UPDATE appointments SET status='Cancelled' WHERE id=?", (int(a["id"]),))
                st.toast("Request cancelled", icon="✅")
                st.rerun()


def page_appointment():
    st.header("📅 Meeting & Appointment Booking")
    st.caption("Sample booking interface. " + DEMO_NOTE)
    if not login_required("Please log in or sign up to request a meeting. Browsing the rest of the site needs no account."):
        return
    u = current_user()
    fdf = qdf("SELECT * FROM faculty ORDER BY name")
    labels = {int(r["id"]): f"{r['name']} - {r['designation']}" for _, r in fdf.iterrows()}
    ids = list(labels)
    pre = st.session_state.get("prefill_fid")
    idx = ids.index(pre) if pre in ids else 0
    tab1, tab2 = st.tabs(["Request a meeting", "My requests / track by ID"])
    with tab1:
        fid = st.selectbox("Who would you like to meet?", ids, index=idx, format_func=lambda i: labels[i])
        c1, c2 = st.columns(2)
        purpose = c1.selectbox("Purpose of meeting", ["Admission enquiry", "Academic enquiry", "Placement enquiry", "Hostel enquiry", "Fee enquiry", "Other"])
        d = c2.date_input("Preferred date", min_value=date.today() + timedelta(days=1), value=date.today() + timedelta(days=1))
        if d.weekday() == 6:
            st.warning("Sundays are not available (sample rule). Choose another date.")
            slots = []
        else:
            slots = slots_for(fid, d)
        t = st.selectbox("Preferred time (available sample slots)", slots if slots else ["No slots available"])
        with st.form("appt_form", clear_on_submit=True):
            name = st.text_input("Your name *", value=u["name"])
            phone = st.text_input("Phone *", value=u.get("phone") or "")
            email = st.text_input("Email", value=u["email"])
            details = st.text_area("Additional details")
            ok = st.form_submit_button("Submit meeting request", type="primary")
        if ok:
            if not name.strip() or not phone.strip():
                st.error("Name and phone are required.")
            elif not slots:
                st.error("Please pick a date with an available slot.")
            elif not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
                st.error("Enter a valid phone number.")
            else:
                aid = run("INSERT INTO appointments(name,phone,email,faculty_id,purpose,details,appt_date,appt_time,created,user_id) VALUES(?,?,?,?,?,?,?,?,?,?)",
                          (name.strip(), phone.strip(), email.strip(), int(fid), purpose, details.strip(), d.isoformat(), t,
                           datetime.now().isoformat(timespec="seconds"), int(u["id"])))
                st.success(f"Request submitted! Your reference ID is **APT-{aid:05d}**. Status: Pending approval.")
                st.toast("Meeting request sent", icon="📅")
    with tab2:
        st.markdown("#### Your requests")
        my_appointments_ui(u, "appt")
        with st.expander("Track a request by reference ID"):
            ref = st.text_input("Reference ID (e.g. APT-00001)")
            ph = st.text_input("Phone used while booking")
            if st.button("Check status"):
                m = re.search(r"(\d+)", ref)
                if m:
                    r = qdf("SELECT a.*, f.name AS fname FROM appointments a JOIN faculty f ON f.id=a.faculty_id WHERE a.id=? AND a.phone=?", (int(m.group(1)), ph.strip()))
                    if len(r):
                        a = r.iloc[0]
                        st.info(f"**APT-{int(a['id']):05d}** · {a['fname']} · {a['appt_date']} {a['appt_time']} · {a['purpose']}  \nStatus: **{a['status']}**")
                    else:
                        st.error("No matching request found.")


def page_account():
    st.header("👤 My Account")
    u = current_user()
    if u:
        with st.container(border=True):
            st.markdown(f"### {html.escape(u['name'])}")
            st.write(f"📧 {u['email']}  \n📞 {u.get('phone') or '-'}  \n🏷️ {u['role']}")
            if st.button("Logout", key="logout_main"):
                st.session_state["user"] = None
                st.toast("Logged out", icon="👋")
                st.rerun()
        t1, t2, t3 = st.tabs(["My meeting requests", "My lost & found reports", "Change password"])
        with t1:
            my_appointments_ui(u, "acct")
        with t2:
            df = qdf("SELECT id,kind,item,description,status,created FROM lost_found WHERE user_id=? ORDER BY id DESC", (int(u["id"]),))
            if len(df):
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("You have not submitted any reports.")
        with t3:
            with st.form("chpw", clear_on_submit=True):
                old = st.text_input("Current password", type="password")
                new = st.text_input("New password (min 8 characters)", type="password")
                ok = st.form_submit_button("Update password", type="primary")
            if ok:
                row = qdf("SELECT * FROM users WHERE id=?", (int(u["id"]),)).iloc[0]
                if not hmac.compare_digest(hash_pw(old, row["salt"])[1], row["pw_hash"]):
                    st.error("Current password is incorrect.")
                elif len(new) < 8:
                    st.error("New password must be at least 8 characters.")
                else:
                    salt, h = hash_pw(new)
                    run("UPDATE users SET salt=?, pw_hash=? WHERE id=?", (salt, h, int(u["id"])))
                    st.success("Password updated.")
        return

    st.write("Create an account to book meetings and report lost & found items. Browsing the campus guide needs no account.")
    tl, ts = st.tabs(["Login", "Sign up"])
    with tl:
        with st.form("login_form"):
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            ok = st.form_submit_button("Login", type="primary")
        if ok:
            if st.session_state.get("fails", 0) >= 5:
                st.error("Too many failed attempts. Please refresh the page and try again later.")
            else:
                r = qdf("SELECT * FROM users WHERE email=?", (email.strip().lower(),))
                if len(r) and hmac.compare_digest(hash_pw(pw, r.iloc[0]["salt"])[1], r.iloc[0]["pw_hash"]):
                    x = r.iloc[0]
                    st.session_state["user"] = {"id": int(x["id"]), "name": x["name"], "email": x["email"], "phone": x["phone"], "role": x["role"]}
                    st.session_state["fails"] = 0
                    st.toast(f"Welcome back, {x['name'].split()[0]}!", icon="👋")
                    st.rerun()
                else:
                    st.session_state["fails"] = st.session_state.get("fails", 0) + 1
                    st.error("Incorrect email or password.")
    with ts:
        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Full name *")
            c1, c2 = st.columns(2)
            email = c1.text_input("Email *", key="su_email")
            phone = c2.text_input("Phone")
            role = st.selectbox("I am a…", ["New student / candidate", "Current student", "Parent", "Visitor", "Alumni"])
            p1 = st.text_input("Password * (min 8 characters)", type="password", key="su_p1")
            p2 = st.text_input("Confirm password *", type="password", key="su_p2")
            ok = st.form_submit_button("Create account", type="primary")
        if ok:
            em = email.strip().lower()
            if not name.strip() or not em:
                st.error("Name and email are required.")
            elif not EMAIL_RE.match(em):
                st.error("Enter a valid email address.")
            elif phone.strip() and not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
                st.error("Enter a valid phone number.")
            elif len(p1) < 8:
                st.error("Password must be at least 8 characters.")
            elif p1 != p2:
                st.error("Passwords do not match.")
            else:
                salt, h = hash_pw(p1)
                try:
                    uid = run("INSERT INTO users(name,email,phone,role,salt,pw_hash,created) VALUES(?,?,?,?,?,?,?)",
                              (name.strip(), em, phone.strip(), role, salt, h, datetime.now().isoformat(timespec="seconds")))
                    st.session_state["user"] = {"id": int(uid), "name": name.strip(), "email": em, "phone": phone.strip(), "role": role}
                    st.toast("Account created. Welcome to HCST!", icon="🎉")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("An account with this email already exists. Please log in.")


def page_lost():
    st.header("🎒 Lost & Found")
    u = current_user()
    tab1, tab2, tab3 = st.tabs(["Report", "Browse items", "Claim an item"])
    with tab1:
        if login_required("Please log in or sign up to submit a lost / found report."):
            with st.form("lf", clear_on_submit=True):
                kind = st.radio("I want to report a…", ["Lost item", "Found item"], horizontal=True)
                item = st.selectbox("Item type", ["ID card", "Book", "Water bottle", "Bag", "Other"])
                desc = st.text_area("Description *")
                where = st.text_input("Where (lost / found)?")
                who = st.text_input("Your name *", value=u["name"] if u else "")
                contact = st.text_input("Contact (phone/email) *", value=(u.get("phone") or u["email"]) if u else "")
                ok = st.form_submit_button("Submit report", type="primary")
            if ok:
                if not (desc.strip() and who.strip() and contact.strip()):
                    st.error("Please fill all required fields.")
                else:
                    run("INSERT INTO lost_found(kind,item,description,where_text,reporter,contact,created,user_id) VALUES(?,?,?,?,?,?,?,?)",
                        (kind, item, desc.strip(), where.strip(), who.strip(), contact.strip(), datetime.now().isoformat(timespec="seconds"),
                         int(u["id"]) if u else None))
                    st.success("Report submitted. The admin will coordinate.")
                    st.toast("Report submitted", icon="🎒")
    with tab2:
        df = qdf("SELECT id,kind,item,description,where_text,status,created FROM lost_found ORDER BY id DESC")
        if len(df):
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No reports yet.")
    with tab3:
        if login_required("Please log in or sign up to claim an item."):
            open_df = qdf("SELECT id,item,description FROM lost_found WHERE status='Open' AND kind='Found item'")
            if not len(open_df):
                st.info("No found items available to claim.")
            else:
                sel = st.selectbox("Found item", open_df["id"], format_func=lambda i: f"#{i} · {open_df[open_df['id']==i]['item'].iloc[0]} - {open_df[open_df['id']==i]['description'].iloc[0][:50]}")
                cl = st.text_input("Your name", value=u["name"] if u else "", key="cl_n")
                note = st.text_area("Proof / details to verify ownership", key="cl_d")
                if st.button("Submit claim", type="primary"):
                    if cl.strip() and note.strip():
                        run("UPDATE lost_found SET status='Claim pending', claimant=?, claim_note=? WHERE id=?", (cl.strip(), note.strip(), int(sel)))
                        st.success("Claim submitted. Admin will verify and coordinate return.")
                    else:
                        st.error("Name and details are required.")


# ------------------------------------------------------------------ ADMIN
def admin_password():
    try:
        return st.secrets.get("ADMIN_PASSWORD", "admin123")
    except Exception:
        return "admin123"


def page_admin():
    st.header("🔐 Admin")
    if not st.session_state.get("admin"):
        pw = st.text_input("Admin password", type="password")
        if st.button("Login", key="admin_login"):
            if pw == admin_password():
                st.session_state["admin"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return
    if st.button("Logout", key="admin_logout"):
        st.session_state["admin"] = False
        st.rerun()
    t1, t2, t3, t4, t5 = st.tabs(["Appointments", "Lost & Found", "Places", "Events", "Users"])
    with t1:
        df = qdf("SELECT a.id,a.name,a.phone,f.name AS meet,a.purpose,a.appt_date,a.appt_time,a.status FROM appointments a JOIN faculty f ON f.id=a.faculty_id ORDER BY a.id DESC")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if len(df):
            c1, c2, c3 = st.columns(3)
            aid = c1.selectbox("Request ID", df["id"], key="adm_aid")
            ns = c2.selectbox("Set status", ["Approved", "Rejected", "Pending", "Cancelled"])
            if c3.button("Update status"):
                run("UPDATE appointments SET status=? WHERE id=?", (ns, int(aid)))
                st.rerun()
    with t2:
        df = qdf("SELECT * FROM lost_found ORDER BY id DESC")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if len(df):
            c1, c2, c3 = st.columns(3)
            lid = c1.selectbox("Item ID", df["id"], key="adm_lid")
            ns = c2.selectbox("Set status", ["Open", "Claim pending", "Returned", "Closed"], key="adm_ls")
            if c3.button("Update item"):
                run("UPDATE lost_found SET status=? WHERE id=?", (ns, int(lid)))
                st.rerun()
    with t3:
        st.caption("Edit building, floor and room number for every place. Tick 'verified' once checked on the campus. "
                   "Note: edits live in the app database, which resets when Streamlit Cloud restarts the app - also update LOC_SEED in app.py to keep them permanently.")
        df = qdf("SELECT id,name,category,building,floor,room,timings,verified FROM locations ORDER BY name")
        df["verified"] = df["verified"].astype(bool)
        ed = st.data_editor(df, use_container_width=True, hide_index=True, disabled=["id"], key="loc_ed")
        if st.button("Save place changes"):
            for _, r in ed.iterrows():
                run("UPDATE locations SET name=?,category=?,building=?,floor=?,room=?,timings=?,verified=? WHERE id=?",
                    (r["name"], r["category"], r["building"], r["floor"], str(r["room"]), r["timings"], int(bool(r["verified"])), int(r["id"])))
            st.success("Saved.")
        with st.form("newloc", clear_on_submit=True):
            st.markdown("**Add a new place**")
            n = st.text_input("Name")
            cat = st.selectbox("Category", [OFF, DEP, FAC, HOS, ENT])
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Building")
            fl = c2.selectbox("Floor", ["Ground", "First", "Second", "Third"])
            rm = c3.text_input("Room number", placeholder="e.g. A-104 (or - if none)")
            ds = st.text_area("Description")
            kw = st.text_input("Search keywords")
            if st.form_submit_button("Add place", type="primary") and n.strip():
                try:
                    run("INSERT INTO locations(name,category,building,floor,room,description,timings,keywords,verified) VALUES(?,?,?,?,?,?,?,?,0)",
                        (n.strip(), cat, b, fl, rm.strip() or "-", ds, "To be verified", kw))
                    st.success("Added.")
                except sqlite3.IntegrityError:
                    st.error("A place with this name already exists.")
        d = qdf("SELECT id,name FROM locations ORDER BY name")
        did = st.selectbox("Delete a place", d["id"], format_func=lambda i: d[d["id"] == i]["name"].iloc[0], key="adm_del_loc")
        if st.button("Delete selected place"):
            run("DELETE FROM locations WHERE id=?", (int(did),))
            st.rerun()
    with t4:
        with st.form("newev", clear_on_submit=True):
            title = st.text_input("Title")
            cat = st.selectbox("Category", ["Placement", "Seminar", "Cultural", "Sports", "Notice", "Orientation"])
            d = st.date_input("Date")
            tm = st.text_input("Time", "10:00")
            ln = st.selectbox("Location", list(locations()["name"]))
            ds = st.text_area("Description")
            if st.form_submit_button("Add event", type="primary") and title.strip():
                run("INSERT INTO events(title,category,event_date,event_time,location_name,description) VALUES(?,?,?,?,?,?)",
                    (title.strip(), cat, d.isoformat(), tm, ln, ds))
                st.success("Event added.")
        ev = qdf("SELECT * FROM events ORDER BY event_date")
        st.dataframe(ev, use_container_width=True, hide_index=True)
        if len(ev):
            eid = st.selectbox("Delete event ID", ev["id"])
            if st.button("Delete event"):
                run("DELETE FROM events WHERE id=?", (int(eid),))
                st.rerun()
    with t5:
        us = qdf("SELECT id,name,email,phone,role,created FROM users ORDER BY id DESC")
        st.dataframe(us, use_container_width=True, hide_index=True)
        if len(us):
            c1, c2 = st.columns(2)
            uid = c1.selectbox("User ID", us["id"], key="adm_uid")
            tmp = c2.text_input("Temporary new password (min 8 chars)", key="adm_tmp")
            b1, b2 = st.columns(2)
            if b1.button("Reset password"):
                if len(tmp) >= 8:
                    salt, h = hash_pw(tmp)
                    run("UPDATE users SET salt=?, pw_hash=? WHERE id=?", (salt, h, int(uid)))
                    st.success("Password reset. Share the temporary password with the user.")
                else:
                    st.error("Use at least 8 characters.")
            if b2.button("Delete user"):
                run("DELETE FROM users WHERE id=?", (int(uid),))
                st.rerun()


# ------------------------------------------------------------------ ROUTER
PAGES = {
    "Home": page_home,
    "Campus Directory": page_directory,
    "Reach HCST": page_reach,
    "Visitor Help Centre": page_visitor,
    "Ask HCST": page_chat,
    "Account": page_account,
    "Faculty Directory": page_faculty,
    "Book Appointment": page_appointment,
    "Facilities": page_facilities,
    "Events & Notices": page_events,
    "Lost & Found": page_lost,
    "Admin": page_admin,
}
ICONS = {"Home": "🏠", "Campus Directory": "🏢", "Reach HCST": "🚗", "Visitor Help Centre": "🧭", "Ask HCST": "💬", "Account": "👤",
         "Faculty Directory": "👩‍🏫", "Book Appointment": "📅", "Facilities": "🏫", "Events & Notices": "📢", "Lost & Found": "🎒", "Admin": "🔐"}
st.sidebar.markdown(f'<div class="brand">🎓 {APP_NAME}<br><span>{TAGLINE}</span></div>', unsafe_allow_html=True)
_u = current_user()
if _u:
    st.sidebar.markdown(f'<div class="userchip">👋 Hi, <b>{html.escape(_u["name"].split()[0])}</b><br><span style="opacity:.7">{html.escape(_u["role"])}</span></div>',
                        unsafe_allow_html=True)
    if st.sidebar.button("Logout", key="logout_side"):
        st.session_state["user"] = None
        st.rerun()
else:
    st.sidebar.button("🔑 Login / Sign up", key="login_side", on_click=goto, args=("Account",), use_container_width=True)
if "page" not in st.session_state:
    st.session_state["page"] = "Home"
st.sidebar.radio("Go to", list(PAGES), key="page", format_func=lambda k: f"{ICONS.get(k, '•')}  {k}")
st.sidebar.caption("Room numbers and faculty details are sample data pending verification by the college.")
PAGES[st.session_state["page"]]()
