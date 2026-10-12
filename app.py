"""Hifz – revamp. Requires Streamlit >= 1.39 (uses st-key-* CSS classes, no JS hacks).
Optional .streamlit/config.toml:  [theme] base="dark"  primaryColor="#d4a94f"
"""
import streamlit as st
import requests, datetime, math, uuid

st.set_page_config(page_title="Hifz", page_icon="📖", layout="centered")

try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
except KeyError:
    st.error("Konfigurera JSONBIN_BIN_ID och JSONBIN_API_KEY i Streamlit secrets.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

# ───────────────────────── DATA ─────────────────────────
raw_surah_names = [
    "Al-Fatihah", "Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Ma'idah", "Al-An'am",
    "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus", "Hud", "Yusuf", "Ar-Ra'd",
    "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha",
    "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan", "Ash-Shu'ara",
    "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum", "Luqman", "As-Sajdah",
    "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar",
    "Ghafir", "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah",
    "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf", "Adh-Dhariyat",
    "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi'ah", "Al-Hadid",
    "Al-Mujadila", "Al-Hashr", "Al-Mumtahanah", "As-Saff", "Al-Jumu'ah",
    "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam",
    "Al-Haqqah", "Al-Ma'arij", "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddathir",
    "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "'Abasa",
    "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj",
    "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad", "Ash-Shams",
    "Al-Layl", "Ad-Duha", "Ash-Sharh", "At-Tin", "Al-'Alaq", "Al-Qadr",
    "Al-Bayyinah", "Az-Zalzalah", "Al-'Adiyat", "Al-Qari'ah", "At-Takathur",
    "Al-'Asr", "Al-Humazah", "Al-Fil", "Quraysh", "Al-Ma'un", "Al-Kawthar",
    "Al-Kafirun", "An-Nasr", "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas",
]
SURAH_LISTA = [f"{i}. {n}" for i, n in enumerate(raw_surah_names, 1)]

SURAH_VERSES = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6,
]
TOTAL_VERSES = sum(SURAH_VERSES)

SURAH_WORDS = [
    29, 6144, 3503, 3745, 2842, 3055, 3346, 1244, 2506, 1839, 1947, 1795, 855, 831, 658, 1844, 1556, 1578, 972, 1353,
    1178, 1282, 1056, 1317, 897, 1322, 1163, 1439, 981, 817, 549, 374, 1303, 884, 779, 733, 866, 735, 1177, 1229,
    794, 860, 836, 346, 488, 648, 542, 560, 353, 373, 360, 312, 360, 342, 352, 379, 575, 475, 445, 349,
    221, 177, 181, 242, 284, 254, 333, 301, 261, 217, 228, 286, 200, 256, 164, 243, 181, 174, 179, 134,
    104, 81, 169, 108, 109, 61, 72, 92, 139, 82, 54, 71, 40, 27, 34, 72, 30, 94, 36, 61,
    36, 28, 14, 33, 23, 17, 25, 10, 27, 19, 23, 15, 23, 20,
]
TOTAL_WORDS = sum(SURAH_WORDS)

SURAH_TO_JUZ = [
    1, 1, 3, 4, 6, 7, 8, 9, 10, 11, 11, 12, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 18, 19, 19, 20, 20, 21, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24,
    24, 25, 25, 25, 25, 26, 26, 26, 26, 26, 26, 27, 27, 27, 27, 27, 27, 28, 28, 28,
    28, 28, 28, 28, 28, 28, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 30, 30, 30,
] + [30] * 34

SURAH_JUZ_SPLIT = {
    2: {1: 141, 2: 111, 3: 34}, 3: {3: 91, 4: 109}, 4: {4: 23, 5: 124, 6: 29},
    5: {6: 81, 7: 39}, 6: {7: 110, 8: 55}, 7: {8: 87, 9: 119}, 8: {9: 40, 10: 35},
    9: {10: 92, 11: 37}, 11: {11: 5, 12: 118}, 12: {12: 52, 13: 59}, 18: {15: 74, 16: 36},
    25: {18: 20, 19: 57}, 27: {19: 55, 20: 38}, 29: {20: 45, 21: 24}, 33: {21: 30, 22: 43},
    36: {22: 27, 23: 56}, 39: {23: 31, 24: 44}, 41: {24: 46, 25: 8}, 51: {26: 30, 27: 30},
}
JUZ_SURAH_WORDS = {j: {} for j in range(1, 31)}
for _s in range(1, 115):
    if _s in SURAH_JUZ_SPLIT:
        for _j, _v in SURAH_JUZ_SPLIT[_s].items():
            JUZ_SURAH_WORDS[_j][_s] = round(SURAH_WORDS[_s - 1] * _v / SURAH_VERSES[_s - 1])
    else:
        JUZ_SURAH_WORDS[SURAH_TO_JUZ[_s - 1]][_s] = SURAH_WORDS[_s - 1]
JUZ_TOTAL_WORDS = {j: sum(v.values()) for j, v in JUZ_SURAH_WORDS.items()}
JUZ_SURAHS = {j: list(v) for j, v in JUZ_SURAH_WORDS.items()}

# ───────────────────────── SRS (unchanged maths) ─────────────────────────
LN_TARGET = -math.log(0.90)
STEP_TO_S = {1: 1.0, 2: 2.8, 3: 7.84, 4: 21.95, 5: 61.47}
GRADE_OPTIONS = ["1 ❌", "2 ⚠️", "3 ✅", "4 👍", "5 🚀"]
S_MIN, S_MAX, MASTERED_S = 1.0, 500.0, 36.7
GRADE_MULT_TABLE = {
    5: {1.0: 1.0, 0.9: 1.8, 0.8: 2.0, 0.7: 2.2, 0.6: 2.4},
    4: {1.0: 1.0, 0.9: 1.5, 0.8: 1.7, 0.7: 1.9, 0.6: 2.1},
    3: {1.0: 1.0, 0.9: 1.2, 0.8: 1.4, 0.7: 1.6, 0.6: 1.8},
    2: {1.0: 0.7, 0.9: 0.8, 0.8: 0.9, 0.7: 1.0, 0.6: 1.1},
    1: {1.0: 0.4, 0.9: 0.5, 0.8: 0.6, 0.7: 0.7, 0.6: 0.8},
}
COLOR_STOPS = [(0.0, (192, 57, 43)), (2.5, (211, 84, 0)), (3.6, (183, 149, 11)),
               (5.2, (26, 111, 168)), (6.21, (26, 122, 74))]


def s_to_rgb(s):
    ls = min(math.log(max(1.0, s)), COLOR_STOPS[-1][0])
    for (lo, c1), (hi, c2) in zip(COLOR_STOPS, COLOR_STOPS[1:]):
        if ls <= hi:
            t = (ls - lo) / (hi - lo)
            return tuple(int(c1[j] + t * (c2[j] - c1[j])) for j in range(3))
    return COLOR_STOPS[-1][1]


def get_mult(grade, r):
    r = max(0.6, min(1.0, r))
    row, bps = GRADE_MULT_TABLE[grade], [1.0, 0.9, 0.8, 0.7, 0.6]
    for hi, lo in zip(bps, bps[1:]):
        if lo <= r <= hi:
            return row[hi] + (hi - r) / (hi - lo) * (row[lo] - row[hi])
    return row[0.6]


def s_to_steg(s):
    return 1 if s < 1.67 else 2 if s < 4.69 else 3 if s < 13.1 else 4 if s < 36.7 else 5


def get_stability(d):
    return float(d.get("stability", STEP_TO_S.get(int(d.get("steg", 1)), 1.0)))


def compute_retention(d, today):
    s = get_stability(d)
    raw = d.get("last_reviewed") or d.get("nasta_repetition") or str(today)
    try:
        last = datetime.date.fromisoformat(raw)
    except ValueError:
        last = today
    return math.exp(-max(0, (today - last).days) / s) if s > 0 else 0.0


# ───────────────────────── DB ─────────────────────────
@st.cache_data(ttl=3600)
def fetch_from_db():
    try:
        r = requests.get(URL, headers=HEADERS)
        if r.status_code == 200:
            return r.json().get("record", [])
    except Exception as e:
        st.error(f"Kunde inte ladda data: {e}")
    return []


def save_to_db(data):
    try:
        if requests.put(URL, json=data, headers=HEADERS).status_code != 200:
            st.error("Fel vid sparning.")
        fetch_from_db.clear()
    except Exception as e:
        st.error(f"Fel: {e}")


if "db_data" not in st.session_state:
    st.session_state.db_data = fetch_from_db()

TODAY = datetime.date.today()


def set_entry(d, s_new):
    s_new = max(S_MIN, min(S_MAX, s_new))
    d["stability"] = round(s_new, 4)
    d["steg"] = s_to_steg(s_new)
    d["last_reviewed"] = str(TODAY)
    d["nasta_repetition"] = str(TODAY + datetime.timedelta(days=max(1, round(LN_TARGET * s_new))))


def find_entry(num):
    return next((d for d in st.session_state.db_data
                 if d["namn"].split(".")[0].strip() == str(num)), None)


def apply_s(num, s_new):
    d = find_entry(num)
    if d is None:
        d = {"id": str(uuid.uuid4()), "namn": f"{num}. {raw_surah_names[num - 1]}"}
        st.session_state.db_data.append(d)
    set_entry(d, s_new)
    save_to_db(st.session_state.db_data)


def grade_cb(item_id, grade):
    for d in st.session_state.db_data:
        if str(d["id"]) == str(item_id):
            s_new = get_stability(d) * get_mult(grade, compute_retention(d, TODAY))
            set_entry(d, s_new)
            st.toast(f"{d['namn']} · S {s_new:.1f}", icon="✅")
            break
    save_to_db(st.session_state.db_data)


# ───────────────────────── STATS ─────────────────────────
data = st.session_state.db_data
S, R, ITEM = {}, {}, {}
for d in data:
    try:
        n = int(d["namn"].split(".")[0])
        S[n], R[n], ITEM[n] = get_stability(d), compute_retention(d, TODAY), d
    except Exception:
        pass

mast = [n for n, s in S.items() if s >= MASTERED_S]
m_verses = sum(SURAH_VERSES[n - 1] for n in mast)
m_words = sum(SURAH_WORDS[n - 1] for n in mast)
s_words = sum(SURAH_WORDS[n - 1] for n in S)
s_verses = sum(SURAH_VERSES[n - 1] for n in S)
juz_done = sum(1 for j in range(1, 31) if all(S.get(s, 0) >= MASTERED_S for s in JUZ_SURAHS[j]))
equiv_juz = round(sum(sum(w for s, w in JUZ_SURAH_WORDS[j].items() if S.get(s, 0) >= MASTERED_S)
                      / JUZ_TOTAL_WORDS[j] for j in range(1, 31)), 1)
due = sorted([d for d in data if d.get("nasta_repetition", "9999") <= str(TODAY)],
             key=lambda d: compute_retention(d, TODAY))

# ───────────────────────── STYLE ─────────────────────────
def H(s):  # collapse indentation so markdown never turns HTML into a code block
    return "".join(l.strip() for l in s.splitlines())


tile_css = ""
for n in range(1, 115):
    if n in S:
        r, g, b = s_to_rgb(S[n])
        p = int(R[n] * 100)
        bg = f"linear-gradient(to right,rgba({r},{g},{b},.55) {p}%,rgba({r},{g},{b},.12) {p}%)"
        edge, fg, ret = f"rgb({r},{g},{b})", "#fff", f"{p}%"
    else:
        bg, edge, fg, ret = "rgba(239,230,210,.04)", "rgba(239,230,210,.15)", "rgba(239,230,210,.6)", ""
    tile_css += (f".st-key-sb_{n} button{{background:{bg}!important;color:{fg}!important;"
                 f"border:1px solid rgba(239,230,210,.1)!important;border-left:4px solid {edge}!important;}}"
                 f".st-key-sb_{n} button::after{{content:'{ret}';margin-left:auto;font-weight:600;padding-left:8px}}")

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Amiri&family=Instrument+Sans:wght@400;600&display=swap');
:root{{--ink:#0d1726;--panel:#14233a;--line:#26385a;--parch:#efe6d2;--gold:#d4a94f;--mute:#8d9bb5;}}
#MainMenu,header,footer{{visibility:hidden}}
.stApp{{background:radial-gradient(1200px 500px at 50% -10%,#1b3358 0%,var(--ink) 60%);color:var(--parch);
 font-family:'Instrument Sans',sans-serif}}
.main .block-container{{max-width:520px;padding:.8rem .9rem 3rem}}
.stApp p,.stApp label,.stApp span{{color:inherit}}
.serif{{font-family:'Newsreader',serif}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}}
.muted{{color:var(--mute);font-size:.78rem}}
.h2{{font-family:'Newsreader',serif;font-size:1.15rem;margin:0 0 8px}}
[data-testid="stHorizontalBlock"]{{flex-wrap:nowrap!important;gap:.3rem!important}}
[data-testid="stColumn"]{{min-width:0!important;flex:1 1 0!important;width:auto!important}}
[data-testid="stVerticalBlock"]{{gap:.3rem}}
button[kind="secondary"],button[kind="primary"]{{border-radius:8px!important;min-height:2.3rem!important;
 padding:0 .2rem!important;font-size:.82rem!important;transition:transform .12s,filter .12s}}
button[kind="secondary"]{{background:var(--panel);color:var(--parch);border:1px solid var(--line)}}
button[kind="secondary"]:hover{{border-color:var(--gold);filter:brightness(1.15)}}
button[kind="secondary"]:active{{transform:scale(.94)}}
button[kind="primary"]{{background:var(--gold)!important;color:#1a1305!important;border:0!important;font-weight:600}}
[data-baseweb="tab-list"]{{gap:6px}}
button[data-baseweb="tab"]{{color:var(--mute)}}
button[data-baseweb="tab"][aria-selected="true"]{{color:var(--gold)}}
[data-baseweb="tab-highlight"]{{background:var(--gold)!important}}
div[role="dialog"]{{background:var(--panel)!important;color:var(--parch)}}
[data-baseweb="select"]>div,input{{background:var(--panel)!important;color:var(--parch)!important}}
[class*="st-key-sb_"] button{{min-height:2.5rem!important;justify-content:flex-start!important;padding:0 .75rem!important;
 text-shadow:0 1px 2px rgba(0,0,0,.4);font-size:.92rem!important}}
[class*="st-key-sb_"] button p{{margin:0;text-align:left}}
[class*="st-key-sb_"] button p strong{{display:inline-block;min-width:2.1rem;color:var(--gold)}}
[data-baseweb="popover"] *,ul[role="listbox"] *{{background:var(--panel)!important;color:var(--parch)!important}}
[data-testid="stVerticalBlockBorderWrapper"]{{background:var(--panel);border:1px solid var(--line)!important;
 border-radius:14px;margin-bottom:6px}}
[data-testid="stRadio"] label{{font-size:.85rem}}
{tile_css}
</style>""", unsafe_allow_html=True)

# ───────────────────────── DIALOG ─────────────────────────
@st.dialog("Sura")
def surah_dialog(num):
    name, started = raw_surah_names[num - 1], num in S
    s_val, r_val = S.get(num, 2.0), R.get(num, 1.0)
    meta = (f"S {s_val:.1f} · retention {int(r_val * 100)}% · {SURAH_VERSES[num - 1]} verser"
            if started else f"Inte påbörjad · {SURAH_VERSES[num - 1]} verser")
    st.markdown(H(f"""<div class='serif' style='font-size:1.5rem'>{num}. {name}</div>
        <div class='muted' style='margin-bottom:10px'>{meta}</div>"""), unsafe_allow_html=True)
    st.caption("Hur gick det? 1 glömd · 3 okej · 5 lätt")
    hit = None
    for i, col in enumerate(st.columns(5)):
        if col.button(GRADE_OPTIONS[i], key=f"dg_{num}_{i}", use_container_width=True):
            hit = i + 1
    new_s = st.number_input("Sätt S direkt", S_MIN, S_MAX, float(round(s_val, 1)), 1.0, key=f"ds_{num}")
    c1, c2 = st.columns(2)
    save = c1.button("Spara S", type="primary", use_container_width=True, key=f"sv_{num}")
    rem = c2.button("Ta bort", use_container_width=True, key=f"rm_{num}", disabled=not started)
    if hit:
        apply_s(num, s_val * get_mult(hit, r_val) if started else STEP_TO_S[hit])
        st.rerun()
    if save:
        apply_s(num, new_s)
        st.rerun()
    if rem:
        st.session_state.db_data = [d for d in st.session_state.db_data if d is not find_entry(num)]
        save_to_db(st.session_state.db_data)
        st.rerun()


if st.session_state.get("pick"):
    surah_dialog(st.session_state.pop("pick"))

# ───────────────────────── HERO ─────────────────────────
C = 2 * math.pi * 54
pm, ps = m_words / TOTAL_WORDS, s_words / TOTAL_WORDS
st.markdown(H(f"""
<div class='card' style='display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:14px 18px;background:linear-gradient(135deg,#1a2f4f,#14233a);box-shadow:inset 0 0 0 4px #14233a,inset 0 0 0 5px rgba(212,169,79,.35)'>
 <svg width='132' height='132' viewBox='0 0 132 132' style='flex:none'>
  <circle cx='66' cy='66' r='54' fill='none' stroke='#26385a' stroke-width='9'/>
  <circle cx='66' cy='66' r='54' fill='none' stroke='#d4a94f' stroke-opacity='.35' stroke-width='9' stroke-linecap='round'
    stroke-dasharray='{ps * C:.1f} {C:.1f}' transform='rotate(-90 66 66)'/>
  <circle cx='66' cy='66' r='54' fill='none' stroke='#d4a94f' stroke-width='9' stroke-linecap='round'
    stroke-dasharray='{pm * C:.1f} {C:.1f}' transform='rotate(-90 66 66)'/>
  <text x='66' y='64' text-anchor='middle' font-family='Newsreader,serif' font-size='30' fill='#efe6d2'>{pm * 100:.1f}%</text>
  <text x='66' y='84' text-anchor='middle' font-family='Amiri,serif' font-size='18' fill='#d4a94f'>حفظ</text>
 </svg>
 <div style='flex:1 1 180px'>
  <div class='serif' style='font-size:1.7rem;line-height:1.1'>{equiv_juz} juz</div>
  <div class='muted' style='margin-bottom:10px'>{m_words:,} av {TOTAL_WORDS:,} ord bemästrade</div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:.8rem'>
   <div><b>{len(mast)}</b>/114 suror</div><div><b>{juz_done}</b>/30 juz</div>
   <div><b>{m_verses:,}</b> verser</div><div><b>{len(S) - len(mast)}</b> pågår</div><div style='grid-column:1/-1;color:#d4a94f'><b>{len(due)}</b> att repetera idag</div>
  </div>
 </div>
</div>"""), unsafe_allow_html=True)

tab_today, tab_over, tab_suras = st.tabs([f"Idag ({len(due)})", "Översikt", "Suror"])

# ───────────────────────── TODAY ─────────────────────────
with tab_today:
    if not due:
        nxt = min((d["nasta_repetition"] for d in data), default=None)
        st.markdown(H(f"""<div class='card' style='text-align:center;padding:28px 14px'>
            <div class='serif' style='font-size:1.4rem'>Allt är repeterat</div>
            <div class='muted'>{'Nästa repetition: ' + nxt if nxt else 'Öppna fliken Suror och lägg till din första sura.'}</div>
            </div>"""), unsafe_allow_html=True)
    for d in due:
      with st.container(border=True):
        r = compute_retention(d, TODAY)
        r_c = "#c0392b" if r < .6 else "#d4a017" if r < .8 else "#1a6fa8" if r < .9 else "#1a7a4a"
        late = (TODAY - datetime.date.fromisoformat(d["nasta_repetition"])).days
        st.markdown(H(f"""<div style='display:flex;justify-content:space-between;align-items:baseline;margin-top:8px'>
            <span class='serif' style='font-size:1.1rem'>{d['namn']}</span>
            <span style='color:{r_c};font-weight:600'>{int(r * 100)}%</span></div>
            <div style='height:3px;border-radius:2px;background:#26385a;margin:4px 0 2px'>
            <div style='height:3px;border-radius:2px;width:{int(r * 100)}%;background:{r_c}'></div></div>
            <div class='muted'>S {get_stability(d):.1f}{f' · {late} d försenad' if late > 0 else ''}</div>"""),
                    unsafe_allow_html=True)
        for i, col in enumerate(st.columns(5)):
            col.button(GRADE_OPTIONS[i], key=f"g_{d['id']}_{i}", on_click=grade_cb,
                       args=(d["id"], i + 1), use_container_width=True)

# ───────────────────────── OVERVIEW ─────────────────────────
with tab_over:
    # next 7 days
    days = [TODAY + datetime.timedelta(days=i) for i in range(7)]
    cnt = [0] * 7
    for d in data:
        try:
            k = (datetime.date.fromisoformat(d["nasta_repetition"]) - TODAY).days
            if k < 7:
                cnt[max(0, k)] += 1
        except Exception:
            pass
    mx = max(cnt) or 1
    wd = ["mån", "tis", "ons", "tors", "fre", "lör", "sön"]
    bars = "".join(
        f"<div style='flex:1;text-align:center'><div class='muted'>{c}</div>"
        f"<div style='height:{6 + int(c / mx * 44)}px;background:{'#d4a94f' if i == 0 else '#3a5688'};"
        f"border-radius:4px;margin:2px 3px'></div><div class='muted'>{'idag' if i == 0 else wd[dd.weekday()]}</div></div>"
        for i, (c, dd) in enumerate(zip(cnt, days)))
    st.markdown(H(f"<div class='card'><div class='h2'>Kommande vecka</div>"
                  f"<div style='display:flex;align-items:flex-end'>{bars}</div></div>"), unsafe_allow_html=True)

    # retention histogram
    bk = [0] * 51
    for r in R.values():
        p = int(r * 100)
        bk[0 if p <= 50 else min(50, p - 50)] += 1
    mb = max(bk) or 1
    bars = ""
    for i, c in enumerate(bk):
        p = 50 + i if i else 50
        col = "#c0392b" if p < 60 else "#d4a017" if p < 80 else "#1a6fa8" if p < 90 else "#1a7a4a"
        lab = ("≤50" if i == 0 else str(p)) if (i == 0 or p % 10 == 0) else ""
        bars += (f"<div style='flex:1;display:flex;flex-direction:column;align-items:center'>"
                 f"<div style='width:100%;height:{int(c / mb * 52)}px;min-height:{2 if c else 0}px;background:{col};"
                 f"border-radius:2px 2px 0 0'></div><div style='font-size:.5rem;color:#8d9bb5'>{lab}</div></div>")
    st.markdown(H(f"<div class='card'><div class='h2'>Retention just nu</div>"
                  f"<div style='display:flex;align-items:flex-end;gap:2px;height:70px'>{bars}</div></div>"),
                unsafe_allow_html=True)

    # juz grid
    tiles = ""
    for j in range(1, 31):
        tot = JUZ_TOTAL_WORDS[j]
        mw = sum(w for s, w in JUZ_SURAH_WORDS[j].items() if S.get(s, 0) >= MASTERED_S)
        sw = sum(w for s, w in JUZ_SURAH_WORDS[j].items() if s in S)
        p = mw / tot
        if mw == tot:
            bg, fg = "#d4a94f", "#1a1305"
        elif sw:
            bg, fg = f"rgba(212,169,79,{0.12 + 0.5 * p:.2f})", "#efe6d2"
        else:
            bg, fg = "rgba(239,230,210,.05)", "#8d9bb5"
        tiles += (f"<div title='Juz {j}: {mw:,}/{tot:,} ord' style='aspect-ratio:1;border-radius:8px;background:{bg};"
                  f"color:{fg};display:flex;flex-direction:column;align-items:center;justify-content:center;"
                  f"border:1px solid #26385a'><b>{j}</b><span style='font-size:.55rem'>{round(p * 100)}%</span></div>")
    st.markdown(H(f"<div class='card'><div class='h2'>Juz</div>"
                  f"<div style='display:grid;grid-template-columns:repeat(6,1fr);gap:6px'>{tiles}</div>"
                  f"<div class='muted' style='margin-top:8px'>Guld = hela juz bemästrat (S ≥ {MASTERED_S:.0f}). "
                  f"Påbörjat: {s_verses:,} verser.</div></div>"), unsafe_allow_html=True)

# ───────────────────────── SURAHS ─────────────────────────
with tab_suras:
    st.selectbox("Hitta sura", SURAH_LISTA, index=None, placeholder="Sök på namn eller nummer", key="q",
                 label_visibility="collapsed",
                 on_change=lambda: st.session_state.update(pick=int(st.session_state.q.split(".")[0]))
                 if st.session_state.q else None)
    grad = ",".join(f"rgb{s_to_rgb(v)}" for v in (1, 7, 30, 120, 500))
    st.markdown(H(f"""<div class='muted' style='display:flex;align-items:center;gap:8px;margin:2px 0 8px'>
        <span>S 1</span><div style='flex:1;height:5px;border-radius:3px;background:linear-gradient(to right,{grad})'></div>
        <span>S 500</span></div>
        <div class='muted' style='margin-bottom:8px'>Färg = stabilitet · fyllnad = retention. Tryck på en rad för att betygsätta.</div>"""),
                unsafe_allow_html=True)
    flt = st.radio("Visa", ["Alla", "Pågående", "Bemästrade", "Ej påbörjade"], horizontal=True,
                   label_visibility="collapsed")
    for n in range(1, 115):
        if ((flt == "Pågående" and not (n in S and S[n] < MASTERED_S))
                or (flt == "Bemästrade" and S.get(n, 0) < MASTERED_S)
                or (flt == "Ej påbörjade" and n in S)):
            continue
        if st.button(f"**{n}** {raw_surah_names[n - 1]}", key=f"sb_{n}", use_container_width=True):
            surah_dialog(n)
