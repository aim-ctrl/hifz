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
ARABIC = ['الفاتحة', 'البقرة', 'آل عمران', 'النساء', 'المائدة', 'الأنعام', 'الأعراف', 'الأنفال', 'التوبة', 'يونس', 'هود', 'يوسف', 'الرعد', 'إبراهيم', 'الحجر', 'النحل', 'الإسراء', 'الكهف', 'مريم', 'طه', 'الأنبياء', 'الحج', 'المؤمنون', 'النور', 'الفرقان', 'الشعراء', 'النمل', 'القصص', 'العنكبوت', 'الروم', 'لقمان', 'السجدة', 'الأحزاب', 'سبأ', 'فاطر', 'يس', 'الصافات', 'ص', 'الزمر', 'غافر', 'فصلت', 'الشورى', 'الزخرف', 'الدخان', 'الجاثية', 'الأحقاف', 'محمد', 'الفتح', 'الحجرات', 'ق', 'الذاريات', 'الطور', 'النجم', 'القمر', 'الرحمن', 'الواقعة', 'الحديد', 'المجادلة', 'الحشر', 'الممتحنة', 'الصف', 'الجمعة', 'المنافقون', 'التغابن', 'الطلاق', 'التحريم', 'الملك', 'القلم', 'الحاقة', 'المعارج', 'نوح', 'الجن', 'المزمل', 'المدثر', 'القيامة', 'الإنسان', 'المرسلات', 'النبأ', 'النازعات', 'عبس', 'التكوير', 'الانفطار', 'المطففين', 'الانشقاق', 'البروج', 'الطارق', 'الأعلى', 'الغاشية', 'الفجر', 'البلد', 'الشمس', 'الليل', 'الضحى', 'الشرح', 'التين', 'العلق', 'القدر', 'البينة', 'الزلزلة', 'العاديات', 'القارعة', 'التكاثر', 'العصر', 'الهمزة', 'الفيل', 'قريش', 'الماعون', 'الكوثر', 'الكافرون', 'النصر', 'المسد', 'الإخلاص', 'الفلق', 'الناس']

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
                 f".st-key-sb_{n} button::before{{content:'{ARABIC[n - 1]}'}}"
                 f".st-key-sb_{n} button>div::before{{content:'{SURAH_TO_JUZ[n - 1]}'}}"
                 f".st-key-sb_{n} button::after{{content:'{ret}'}}")
    if S.get(n, 0) >= S_MAX:
        tile_css += (f".st-key-sb_{n} button{{position:relative}}"
                     f".st-key-sb_{n} button>div::after{{content:'⭐';position:absolute;left:50%;top:50%;"
                     f"transform:translate(-50%,-50%);font-size:.95rem;text-shadow:none}}")

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
[class*="st-key-sb_"] button>div{{order:1}}
[class*="st-key-sb_"] button{{position:relative}}
[class*="st-key-sb_"] button>div::before{{position:absolute;left:.75rem;top:3px;width:1.3rem;text-align:center;
 font-size:.52rem;line-height:1;font-weight:600;opacity:.6;text-shadow:none}}
[class*="st-key-sb_"] button::before{{order:2;margin-left:auto;font-family:'Amiri',serif;font-size:1.15rem;opacity:.9;
 padding-right:10px;direction:rtl}}
[class*="st-key-sb_"] button::after{{order:3;min-width:2.5rem;text-align:right;font-weight:600}}
[data-testid="stExpander"] details{{background:var(--panel);border:1px solid var(--line)!important;border-radius:12px}}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{{color:var(--parch);font-family:'Newsreader',serif;font-size:1.02rem}}
[class*="st-key-sb_"] button>div{{flex:0 1 auto;text-align:left!important;justify-content:flex-start!important}}
[class*="st-key-sb_"] button p strong{{display:inline-block;width:2.2rem;text-align:left;color:var(--gold)}}
[data-baseweb="popover"] *,ul[role="listbox"] *{{background:var(--panel)!important;color:var(--parch)!important}}
[data-testid="stVerticalBlockBorderWrapper"]{{background:var(--panel);border:1px solid var(--line)!important;
 border-radius:14px;margin-bottom:6px}}
[data-testid="stRadio"] label{{font-size:.85rem}}
{tile_css}
</style>""", unsafe_allow_html=True)

# ───────────────────────── DIALOG ─────────────────────────
def curve_svg(s_, el):
    T = max(s_ * 1.5, el * 1.15 + 1)
    W, HH, L, B = 300, 100, 26, 18
    X = lambda t: L + t / T * (W - L - 6)
    Y = lambda r: 8 + (1 - r) * (HH - 8 - B)
    pts = " ".join(f"{X(T * i / 40):.1f},{Y(math.exp(-T * i / 40 / s_)):.1f}" for i in range(41))
    t90, y90, nowr = LN_TARGET * s_, Y(0.9), math.exp(-el / s_)
    return (f"<svg viewBox='0 0 {W} {HH + 4}' style='width:100%;margin-top:6px'>"
            f"<line x1='{L}' x2='{W - 6}' y1='{y90:.1f}' y2='{y90:.1f}' stroke='#d4a94f' stroke-opacity='.5' stroke-dasharray='3 3'/>"
            f"<line x1='{X(t90):.1f}' x2='{X(t90):.1f}' y1='{y90:.1f}' y2='{Y(0):.1f}' stroke='#d4a94f' stroke-opacity='.5' stroke-dasharray='3 3'/>"
            f"<text x='2' y='{y90 + 3:.1f}' font-size='8' fill='#d4a94f'>90%</text>"
            f"<polyline points='{pts}' fill='none' stroke='#efe6d2' stroke-width='2'/>"
            f"<circle cx='{X(el):.1f}' cy='{Y(nowr):.1f}' r='4.5' fill='#d4a94f'/>"
            f"<text x='{L}' y='{HH + 2}' font-size='8' fill='#8d9bb5'>0 d</text>"
            f"<text x='{W - 6}' y='{HH + 2}' font-size='8' fill='#8d9bb5' text-anchor='end'>{T:.0f} d</text></svg>"
            f"<div class='muted' style='margin-bottom:8px'>Minneskurva · gul punkt = nu (dag {el}) · "
            f"90% nås efter {t90:.1f} dagar</div>")


@st.dialog("Sura")
def surah_dialog(num):
    name, started = raw_surah_names[num - 1], num in S
    s_val, r_val = S.get(num, 2.0), R.get(num, 1.0)
    meta = (f"S {s_val:.1f} · retention {int(r_val * 100)}% · {SURAH_VERSES[num - 1]} verser"
            if started else f"Inte påbörjad · {SURAH_VERSES[num - 1]} verser")
    st.markdown(H(f"""<div class='serif' style='font-size:1.5rem'>{num}. {name}</div>
        <div style="font-family:Amiri,serif;font-size:1.7rem;color:#d4a94f;line-height:1.4">{ARABIC[num - 1]}</div>
        <div class='muted' style='margin-bottom:10px'>{meta}</div>"""), unsafe_allow_html=True)
    if started:
        st.markdown(curve_svg(s_val, round(-s_val * math.log(max(r_val, 1e-9)))), unsafe_allow_html=True)
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
   <div><b>{m_verses:,}</b> verser</div><div><b>{len(S) - len(mast)}</b> pågår</div>
  </div>
 </div>
</div>"""), unsafe_allow_html=True)

tab_over, tab_stat, tab_suras = st.tabs(["Översikt", "Statistik", "Suror"])

# ───────────────────────── OVERVIEW ─────────────────────────
with tab_over:
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

# ───────────────────────── STATISTICS ─────────────────────────
with tab_stat:
    revs = []
    for d in data:
        try:
            revs.append((TODAY - datetime.date.fromisoformat(d["last_reviewed"])).days)
        except Exception:
            pass
    avg_r = sum(R.values()) / len(R) if R else 0
    avg_s = sum(S.values()) / len(S) if S else 0
    srt = sorted(S.values())
    med_s = srt[len(srt) // 2] if srt else 0
    juz_started = sum(1 for j in range(1, 31) if any(s in S for s in JUZ_SURAHS[j]))

    def pbar(lab, m, s_, t):
        return (f"<div style='margin:9px 0'><div style='display:flex;justify-content:space-between;font-size:.82rem'>"
                f"<span>{lab}</span><span class='muted'><b style='color:#d4a94f'>{m / t:.0%}</b> bemästrat · {s_ / t:.0%} påbörjat</span></div>"
                f"<div style='height:8px;border-radius:4px;background:#26385a;margin-top:4px;position:relative'>"
                f"<div style='position:absolute;height:8px;border-radius:4px;width:{s_ / t * 100:.1f}%;background:rgba(212,169,79,.35)'></div>"
                f"<div style='position:absolute;height:8px;border-radius:4px;width:{m / t * 100:.1f}%;background:#d4a94f'></div></div></div>")

    st.markdown(H("<div class='card'><div class='h2'>Framsteg</div>"
                  + pbar("Suror", len(mast), len(S), 114) + pbar("Juz", juz_done, juz_started, 30)
                  + pbar("Verser", m_verses, s_verses, TOTAL_VERSES) + pbar("Ord", m_words, s_words, TOTAL_WORDS)
                  + "</div>"), unsafe_allow_html=True)

    def tile(l, v, sub=""):
        return (f"<div style='background:rgba(239,230,210,.05);border:1px solid #26385a;border-radius:10px;padding:10px'>"
                f"<div class='muted'>{l}</div><div class='serif' style='font-size:1.45rem;line-height:1.25'>{v}</div>"
                f"<div class='muted'>{sub}</div></div>")

    with st.container(border=True):
        st.markdown("<div class='h2'>Mål och prognos</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        goal = c1.number_input("Mål (juz)", 1, 30, 30, key="goal")
        pace = c2.number_input("Tempo (ord/vecka)", 10, 5000, 250, 10, key="pace")
        dl = st.date_input("Klar senast", TODAY + datetime.timedelta(days=365),
                           min_value=TODAY + datetime.timedelta(days=1), key="dl")
        rem = max(0.0, goal * TOTAL_WORDS / 30 - m_words)
        weeks = rem / pace
        need = rem / max(1, (dl - TODAY).days) * 7
        vpd = need / 7 * TOTAL_VERSES / TOTAL_WORDS
        eta = "Klart 🎉" if rem == 0 else (TODAY + datetime.timedelta(weeks=weeks)).isoformat()
        good = pace >= need
        st.markdown(H("<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>"
                      + tile("Beräknat klart", eta, f"≈ {weeks:.0f} veckor kvar")
                      + tile("Krävs för deadline", f"{need:.0f} ord/v", f"≈ {vpd:.1f} verser/dag")
                      + "</div>"
                      + f"<div class='muted' style='margin-top:8px;color:{'#4caf7d' if good else '#d4a017'}'>"
                      + ("I fas med ditt tempo" if good else "Du behöver öka tempot för att nå deadline") + "</div>"),
                    unsafe_allow_html=True)

    tiles = "".join([
        tile("Påbörjade suror", len(S), f"av 114 · {len(S) / 114:.0%}"),
        tile("Bemästrade suror", len(mast), f"S ≥ {MASTERED_S:.0f}"),
        tile("Snitt-retention", f"{avg_r:.0%}", "alla påbörjade"),
        tile("Snitt-stabilitet", f"{avg_s:.1f} d", f"median {med_s:.1f} d"),
        tile("Verser påbörjade", f"{s_verses:,}", f"{s_verses / TOTAL_VERSES:.1%} av Koranen"),
        tile("Ord påbörjade", f"{s_words:,}", f"{s_words / TOTAL_WORDS:.1%} av Koranen"),
        tile("Granskade 7 dagar", sum(1 for x in revs if x < 7), f"{sum(1 for x in revs if x == 0)} idag"),
        tile("Granskade 30 dagar", sum(1 for x in revs if x < 30), "suror"),
    ])
    st.markdown(H(f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px'>{tiles}</div>"),
                unsafe_allow_html=True)

    bins = [(0, 2, "under 2 d", 1.5), (2, 7, "2–7 d", 4), (7, 21, "7–21 d", 12),
            (21, 37, "21–37 d", 28), (37, 100, "37–100 d", 60), (100, 1e9, "100 d +", 200)]
    cts = [sum(1 for s in S.values() if lo <= s < hi) for lo, hi, _, _ in bins]
    mx = max(cts) or 1
    rows = ""
    for (lo, hi, lab, rep), c in zip(bins, cts):
        r_, g_, b_ = s_to_rgb(rep)
        rows += (f"<div style='display:flex;align-items:center;gap:8px;margin:6px 0'>"
                 f"<div class='muted' style='width:62px'>{lab}</div>"
                 f"<div style='flex:1;height:10px;border-radius:5px;background:#26385a'>"
                 f"<div style='height:10px;border-radius:5px;width:{c / mx * 100:.0f}%;background:rgb({r_},{g_},{b_})'></div></div>"
                 f"<div style='width:24px;text-align:right'>{c}</div></div>")
    st.markdown(H(f"<div class='card'><div class='h2'>Stabilitet</div>{rows}</div>"), unsafe_allow_html=True)

    empty = "<div class='muted'>Inga data än</div>"

    def toplist(title, items, fmt):
        rows = "".join(f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #26385a'>"
                       f"<span>{n}. {raw_surah_names[n - 1]}</span><b>{fmt(n)}</b></div>" for n in items)
        st.markdown(H(f"<div class='card'><div class='h2'>{title}</div>{rows or empty}</div>"), unsafe_allow_html=True)

    toplist("Starkast", sorted(S, key=lambda n: -S[n])[:5], lambda n: f"S {S[n]:.0f}")
    toplist("Lägst retention", sorted(R, key=lambda n: R[n])[:5], lambda n: f"{int(R[n] * 100)}%")

# ───────────────────────── SURAHS ─────────────────────────
with tab_suras:
    grad = ",".join(f"rgb{s_to_rgb(v)}" for v in (1, 7, 30, 120, 500))
    st.markdown(H(f"""<div class='muted' style='display:flex;align-items:center;gap:8px;margin:2px 0 8px'>
        <span>S 1</span><div style='flex:1;height:5px;border-radius:3px;background:linear-gradient(to right,{grad})'></div>
        <span>S 500</span></div>"""),
                unsafe_allow_html=True)
    FILTERS = ["Alla", "Påbörjade", "Pågående", "Bemästrade", "Ej påbörjade", "Retention under 90 %",
               "Retention under 70 %", "Svaga (S under 7 d)", "Nästan bemästrade (S 20–37)",
               "Långa (100+ verser)", "Korta (under 20 verser)"]
    SORTS = ["Sura", "Lägst retention", "Högst retention", "Högst stabilitet", "Lägst stabilitet",
             "Senast granskad", "Längst sedan granskad", "Flest verser", "Färst verser", "Namn A–Z"]
    fc, mc = st.columns(2)
    flt = fc.selectbox("Visa", FILTERS, key="flt", label_visibility="collapsed")
    mode = mc.selectbox("Sortera", SORTS, key="mode", label_visibility="collapsed")

    def ok(n):
        s_, r_, v = S.get(n), R.get(n), SURAH_VERSES[n - 1]
        return {"Alla": True, "Påbörjade": s_ is not None, "Pågående": s_ is not None and s_ < MASTERED_S,
                "Bemästrade": s_ is not None and s_ >= MASTERED_S, "Ej påbörjade": s_ is None,
                "Retention under 90 %": r_ is not None and r_ < .9, "Retention under 70 %": r_ is not None and r_ < .7,
                "Svaga (S under 7 d)": s_ is not None and s_ < 7,
                "Nästan bemästrade (S 20–37)": s_ is not None and 20 <= s_ < MASTERED_S,
                "Långa (100+ verser)": v >= 100, "Korta (under 20 verser)": v < 20}[flt]

    def days_ago(n):
        try:
            return (TODAY - datetime.date.fromisoformat(ITEM[n]["last_reviewed"])).days
        except Exception:
            return 9999

    def row(n):
        if st.button(f"**{n}** {raw_surah_names[n - 1]}", key=f"sb_{n}", use_container_width=True):
            surah_dialog(n)

    if mode == "Sura":
        for n in range(1, 115):
            if ok(n):
                row(n)
    else:
        KEYS = {
            "Lägst retention": lambda n: (n not in S, R.get(n, 0), n),
            "Högst retention": lambda n: (n not in S, -R.get(n, 0), n),
            "Högst stabilitet": lambda n: (n not in S, -S.get(n, 0), n),
            "Lägst stabilitet": lambda n: (n not in S, S.get(n, 0), n),
            "Senast granskad": lambda n: (n not in S, days_ago(n), n),
            "Längst sedan granskad": lambda n: (n not in S, -days_ago(n), n),
            "Flest verser": lambda n: (-SURAH_VERSES[n - 1], n),
            "Färst verser": lambda n: (SURAH_VERSES[n - 1], n),
            "Namn A–Z": lambda n: (raw_surah_names[n - 1].lstrip("'").lower(), n),
        }
        for n in sorted((n for n in range(1, 115) if ok(n)), key=KEYS[mode]):
            row(n)

# Keep the on-screen keyboard closed for dropdowns: make the select's search input readonly + inputmode none
st.components.v1.html("""<script>
(function(){
  var doc = window.parent.document;
  function fix(){
    doc.querySelectorAll('[data-baseweb="select"] input').forEach(function(i){
      if (i.getAttribute('inputmode') !== 'none') i.setAttribute('inputmode', 'none');
      if (!i.readOnly) i.readOnly = true;
    });
  }
  fix();
  setInterval(fix, 300);
  new MutationObserver(fix).observe(doc.body, {childList: true, subtree: true});
  ['pointerdown', 'touchstart', 'mousedown'].forEach(function(ev){
    doc.addEventListener(ev, fix, true);
  });
})();
</script>""", height=1)
