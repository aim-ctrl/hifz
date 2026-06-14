import streamlit as st
import requests
import datetime
import math
import uuid

st.set_page_config(page_title="Hifz", page_icon="📖", layout="centered")

try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
except KeyError:
    st.error("Konfigurera JSONBIN_BIN_ID och JSONBIN_API_KEY i Streamlit secrets.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

# --- SURAH DATA ---
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
    "Al-Kafirun", "An-Nasr", "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"
]
SURAH_LISTA = [f"{i}. {name}" for i, name in enumerate(raw_surah_names, 1)]

SURAH_VERSES = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6
]
TOTAL_VERSES = sum(SURAH_VERSES)

SURAH_WORDS = [
    29, 6144, 3503, 3745, 2842, 3055, 3346, 1244, 2506, 1839,
    1947, 1795, 855, 831, 658, 1844, 1556, 1578, 972, 1353,
    1178, 1282, 1056, 1317, 897, 1322, 1163, 1439, 981, 817,
    549, 374, 1303, 884, 779, 733, 866, 735, 1177, 1229,
    794, 860, 836, 346, 488, 648, 542, 560, 353, 373,
    360, 312, 360, 342, 352, 379, 575, 475, 445, 349,
    221, 177, 181, 242, 284, 254, 333, 301, 261, 217,
    228, 286, 200, 256, 164, 243, 181, 174, 179, 134,
    104, 81, 169, 108, 109, 61, 72, 92, 139, 82,
    54, 71, 40, 27, 34, 72, 30, 94, 36, 61,
    36, 28, 14, 33, 23, 17, 25, 10, 27, 19,
    23, 15, 23, 20
]
TOTAL_WORDS = sum(SURAH_WORDS)

SURAH_TO_JUZ = [
    1, 1, 3, 4, 6, 7, 8, 9, 10, 11,
    11, 12, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 18, 19, 19, 20, 20, 21,
    21, 21, 21, 22, 22, 22, 23, 23, 23, 24,
    24, 25, 25, 25, 25, 26, 26, 26, 26, 26,
    26, 27, 27, 27, 27, 27, 27, 28, 28, 28,
    28, 28, 28, 28, 28, 28, 29, 29, 29, 29,
    29, 29, 29, 29, 29, 29, 29, 30, 30, 30,
    30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
    30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
    30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
    30, 30, 30, 30
]

SURAH_JUZ_SPLIT = {
    2:  {1: 141, 2: 111, 3:  34},
    3:  {3:  91, 4: 109},
    4:  {4:  23, 5: 124, 6:  29},
    5:  {6:  81, 7:  39},
    6:  {7: 110, 8:  55},
    7:  {8:  87, 9: 119},
    8:  {9:  40, 10: 35},
    9:  {10: 92, 11: 37},
    11: {11:  5, 12: 118},
    12: {12: 52, 13:  59},
    18: {15: 74, 16:  36},
    25: {18: 20, 19:  57},
    27: {19: 55, 20:  38},
    29: {20: 45, 21:  24},
    33: {21: 30, 22:  43},
    36: {22: 27, 23:  56},
    39: {23: 31, 24:  44},
    41: {24: 46, 25:   8},
    51: {26: 30, 27:  30},
}

JUZ_SURAH_WORDS = {j: {} for j in range(1, 31)}
for _s in range(1, 115):
    if _s in SURAH_JUZ_SPLIT:
        for _j, _v in SURAH_JUZ_SPLIT[_s].items():
            JUZ_SURAH_WORDS[_j][_s] = round(SURAH_WORDS[_s - 1] * _v / SURAH_VERSES[_s - 1])
    else:
        JUZ_SURAH_WORDS[SURAH_TO_JUZ[_s - 1]][_s] = SURAH_WORDS[_s - 1]

JUZ_TOTAL_WORDS = {j: sum(v.values()) for j, v in JUZ_SURAH_WORDS.items()}
JUZ_SURAHS = {j: list(sw.keys()) for j, sw in JUZ_SURAH_WORDS.items()}

# --- CONTINUOUS SRS ALGORITHM ---
# R = e^(-t/S)  — S = stability (days), t = elapsed days, R_target = 0.90
LN_TARGET: float = -math.log(0.90)        # ≈ 0.10536
STEP_TO_S: dict[int, float] = {1: 1.0, 2: 2.8, 3: 7.84, 4: 21.95, 5: 61.47}
GRADE_OPTIONS = ["1 ❌", "2 ⚠️", "3 ✅", "4 👍", "5 🚀"]
S_MIN: float = 1.0
S_MAX: float = 500.0

# Multiplier table: grade (1–5) × R-bucket (clamped to [0.6, 1.0])
GRADE_MULT_TABLE: dict[int, dict[float, float]] = {
    5: {1.0: 1.0, 0.9: 1.8, 0.8: 2.0, 0.7: 2.2, 0.6: 2.4},
    4: {1.0: 1.0, 0.9: 1.5, 0.8: 1.7, 0.7: 1.9, 0.6: 2.1},
    3: {1.0: 1.0, 0.9: 1.2, 0.8: 1.4, 0.7: 1.6, 0.6: 1.8},
    2: {1.0: 0.7, 0.9: 0.8, 0.8: 0.9, 0.7: 1.0, 0.6: 1.1},
    1: {1.0: 0.4, 0.9: 0.5, 0.8: 0.6, 0.7: 0.7, 0.6: 0.8},
}
MASTERED_S: float = 36.7    # S ≥ this → considered mastered

# Retention histogram buckets and colours (10 bins, 10 % each)
# <60 % red, 60-80 % yellow, 80-90 % blue, 90-100 % green
def _ret_color(bin_idx: int) -> str:
    pct = bin_idx * 10
    if pct < 60:   return "#c0392b"   # red
    if pct < 80:   return "#d4a017"   # yellow
    if pct < 90:   return "#1a6fa8"   # blue
    return "#1a7a4a"                   # green

RET_COLORS = [_ret_color(i) for i in range(10)]
RET_LABELS = [f"{i*10:02d}–{i*10+10}%" for i in range(10)]


def s_to_color_rgb(s: float) -> tuple:
    """Log-scale S → RGB: red(S≈1) → orange → yellow → blue → green(S≈500+)."""
    stops = [
        (0.0, (192,  57,  43)),
        (1.6, (211,  84,   0)),
        (2.7, (183, 149,  11)),
        (3.9, ( 26, 111, 168)),
        (6.21, ( 26, 122,  74)),
    ]
    ls = min(math.log(max(1.0, s)), stops[-1][0])
    for i in range(len(stops) - 1):
        lo, c1 = stops[i]
        hi, c2 = stops[i + 1]
        if ls <= hi:
            t = (ls - lo) / (hi - lo)
            return tuple(int(c1[j] + t * (c2[j] - c1[j])) for j in range(3))
    return stops[-1][1]


def s_to_css(s: float, alpha: float = 1.0) -> str:
    r, g, b = s_to_color_rgb(s)
    return f"rgba({r},{g},{b},{alpha:.2f})"


def get_mult(grade: int, r: float) -> float:
    """S multiplier via linear interpolation between R breakpoints."""
    r_c = max(0.6, min(1.0, r))
    row = GRADE_MULT_TABLE[grade]
    bps = [1.0, 0.9, 0.8, 0.7, 0.6]
    for i in range(len(bps) - 1):
        r_hi, r_lo = bps[i], bps[i + 1]
        if r_lo <= r_c <= r_hi:
            t = (r_hi - r_c) / (r_hi - r_lo)
            return row[r_hi] + t * (row[r_lo] - row[r_hi])
    return row[0.6]


def s_to_steg(s: float) -> int:
    """Kept only for backward-compat writes to the 'steg' DB field."""
    if s < 1.67: return 1
    if s < 4.69: return 2
    if s < 13.1: return 3
    if s < 36.7: return 4
    return 5


def get_stability(item: dict) -> float:
    return float(item.get("stability", STEP_TO_S.get(int(item.get("steg", 1)), 1.0)))


def compute_retention(item: dict, today: datetime.date) -> float:
    s = get_stability(item)
    raw = item.get("last_reviewed") or item.get("nasta_repetition") or str(today)
    try:
        last_rev = datetime.date.fromisoformat(raw)
    except ValueError:
        last_rev = today
    elapsed = max(0, (today - last_rev).days)
    return math.exp(-elapsed / s) if s > 0 else 0.0


# --- CORE LOGIC ---
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
        r = requests.put(URL, json=data, headers=HEADERS)
        if r.status_code != 200:
            st.error("Fel vid sparning.")
        fetch_from_db.clear()
    except Exception as e:
        st.error(f"Fel: {e}")


if "db_data" not in st.session_state:
    st.session_state.db_data = fetch_from_db()


def update_stability(item_id, new_s_raw):
    new_s = max(S_MIN, min(S_MAX, float(new_s_raw)))
    for d in st.session_state.db_data:
        if str(d["id"]) != str(item_id):
            continue
        d["stability"] = round(new_s, 4)
        d["steg"] = s_to_steg(new_s)
        try:
            last_rev = datetime.date.fromisoformat(d.get("last_reviewed", str(datetime.date.today())))
        except ValueError:
            last_rev = datetime.date.today()
        d["nasta_repetition"] = str(last_rev + datetime.timedelta(days=max(1, round(LN_TARGET * new_s))))
        st.toast(f"{d['namn']} · S → {new_s:.1f}")
        break
    save_to_db(st.session_state.db_data)


def delete_item(item_id):
    st.session_state.db_data = [
        d for d in st.session_state.db_data if str(d["id"]) != str(item_id)
    ]
    save_to_db(st.session_state.db_data)
    st.toast("Borttaget.")


def graded_action_callback(item_id, key):
    grade_str = st.session_state.get(key)
    if not grade_str:
        return
    grade = int(grade_str[0])
    today = datetime.date.today()
    today_str = str(today)
    for d in st.session_state.db_data:
        if str(d["id"]) != str(item_id):
            continue
        s_old = get_stability(d)
        r_val = compute_retention(d, today)
        s_new = max(S_MIN, min(S_MAX, s_old * get_mult(grade, r_val)))
        d["stability"]        = round(s_new, 4)
        d["last_reviewed"]    = today_str
        d["nasta_repetition"] = str(today + datetime.timedelta(days=max(1, round(LN_TARGET * s_new))))
        d["steg"]             = s_to_steg(s_new)
        st.session_state[key] = None
        st.toast(f"{d['namn']} · S={s_new:.1f}")
        break
    save_to_db(st.session_state.db_data)


# --- CSS ---
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }

.main .block-container {
    padding-top: 0.25rem !important;
    padding-bottom: 130px !important;
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
    max-width: 520px !important;
}

[data-baseweb="tab-list"] {
    position: fixed !important;
    bottom: 50px !important; left: 0 !important; right: 0 !important;
    z-index: 99999 !important;
    background: var(--background-color) !important;
    border-top: 1px solid var(--border-color) !important;
    height: 58px !important;
    padding: 0 !important;
    gap: 0 !important;
    display: flex !important;
    justify-content: space-around !important;
    align-items: stretch !important;
    margin: 0 !important;
}
[data-baseweb="tab"] {
    flex: 1 !important;
    height: 58px !important;
    padding: 4px 1px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.56em !important;
    gap: 1px !important;
    border: none !important;
    min-width: 0 !important;
    white-space: normal !important;
    text-align: center !important;
    line-height: 1.2 !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #1a7a4a !important;
    border-top: 2px solid #1a7a4a !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 0.45rem 0.55rem !important; }
</style>
""", unsafe_allow_html=True)

# --- COMPUTED STATS ---
data     = st.session_state.db_data
today    = datetime.date.today()
today_str = str(today)

total_added = len(data)

surah_stability: dict[int, float] = {}
surah_retention: dict[int, float] = {}
for d in data:
    try:
        num = int(d["namn"].split(".")[0])
        surah_stability[num] = get_stability(d)
        surah_retention[num] = compute_retention(d, today)
    except Exception:
        pass

mastered_count  = sum(1 for s in surah_stability.values() if s >= MASTERED_S)
mastered_verses = sum(SURAH_VERSES[n - 1] for n, s in surah_stability.items() if s >= MASTERED_S)
mastered_words  = sum(SURAH_WORDS[n - 1]  for n, s in surah_stability.items() if s >= MASTERED_S)
started_verses  = sum(SURAH_VERSES[n - 1] for n in surah_stability)
started_words   = sum(SURAH_WORDS[n - 1]  for n in surah_stability)

due_today = sum(1 for d in data if d["nasta_repetition"] <= today_str)

juz_fully_mastered = sum(
    1 for j in range(1, 31)
    if JUZ_SURAHS.get(j) and all(surah_stability.get(s, 0) >= MASTERED_S for s in JUZ_SURAHS[j])
)
equiv_juz = round(sum(
    sum(JUZ_SURAH_WORDS[j].get(s, 0) for s in JUZ_SURAHS.get(j, []) if surah_stability.get(s, 0) >= MASTERED_S)
    / JUZ_TOTAL_WORDS[j]
    for j in range(1, 31) if JUZ_TOTAL_WORDS.get(j, 0) > 0
), 1)
potential_equiv_juz = round(sum(
    sum(JUZ_SURAH_WORDS[j].get(s, 0) for s in JUZ_SURAHS.get(j, []) if s in surah_stability)
    / JUZ_TOTAL_WORDS[j]
    for j in range(1, 31) if JUZ_TOTAL_WORDS.get(j, 0) > 0
), 1)
potential_juz_mastered = sum(
    1 for j in range(1, 31)
    if JUZ_SURAHS.get(j) and all(s in surah_stability for s in JUZ_SURAHS[j])
)

# Retention histogram: 10 buckets 0-10%, 10-20%, …, 90-100%
ret_buckets = [0] * 10
for r in surah_retention.values():
    ret_buckets[min(9, int(r * 10))] += 1

# --- TABS ---
tab_dash, tab_idag, tab_progress, tab_hantera, tab_lagg = st.tabs([
    "🏠 Hem", "🎯 Session", "📊 Progress", "📚 Hantera", "➕ Nytt"
])

# ===================== DASHBOARD =====================
with tab_dash:
    pct_surah = int((mastered_count / 114) * 100)
    pct_verse = int((mastered_verses / TOTAL_VERSES) * 100) if mastered_verses else 0
    pct_word  = int((mastered_words  / TOTAL_WORDS)  * 100) if mastered_words  else 0
    pct_juz   = int((juz_fully_mastered / 30) * 100)

    def stat_row(label, value, total, color, pct, unit=""):
        bar = (
            f"<div style='flex:1;height:5px;background:var(--border-color);"
            f"border-radius:3px;margin:0 8px;'>"
            f"<div style='width:{pct}%;height:5px;background:{color};border-radius:3px;'>"
            f"</div></div>"
        )
        return (
            f"<div style='display:flex;align-items:center;margin-bottom:6px;'>"
            f"<div style='width:80px;font-size:0.7em;opacity:0.6;'>{label}</div>"
            f"{bar}"
            f"<div style='text-align:right;min-width:80px;'>"
            f"<span style='font-size:0.9em;font-weight:700;color:{color};'>{value:,}</span>"
            f"<span style='font-size:0.6em;opacity:0.5;'>/{total:,}{unit}</span>"
            f"</div></div>"
        )

    def big_stat(label, value, sub, color):
        return (
            f"<div style='text-align:center;padding:6px;'>"
            f"<div style='font-size:0.6em;opacity:0.55;text-transform:uppercase;"
            f"letter-spacing:0.04em;margin-bottom:2px;'>{label}</div>"
            f"<div style='font-size:1.6em;font-weight:800;color:{color};line-height:1;'>{value}</div>"
            f"<div style='font-size:0.58em;opacity:0.45;margin-top:1px;'>{sub}</div>"
            f"</div>"
        )

    st.markdown(f"""
<div style="background:var(--secondary-background-color);border-radius:10px;border:1px solid var(--border-color);padding:12px;margin-bottom:10px;">
  <div style="display:grid;grid-template-columns:1fr 1px 1fr 1px 1fr 1px 1fr;gap:0;margin-bottom:10px;">
    {big_stat("Suror", mastered_count, f"/{114}", "#1a7a4a")}
    <div style="background:var(--border-color);"></div>
    {big_stat("Juz", juz_fully_mastered, "/30", "#b7950b")}
    <div style="background:var(--border-color);"></div>
    {big_stat("Verser", f"{mastered_verses:,}", f"/{TOTAL_VERSES:,}", "#1a6fa8")}
    <div style="background:var(--border-color);"></div>
    {big_stat("Ord", f"{mastered_words:,}", f"/{TOTAL_WORDS:,}", "#8e44ad")}
  </div>
  <div style="font-size:0.65em;opacity:0.5;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:6px;">Bemastrade (S≥{MASTERED_S:.0f})</div>
  {stat_row("Suror", mastered_count, 114, "#1a7a4a", pct_surah)}
  {stat_row("Juz", juz_fully_mastered, 30, "#b7950b", pct_juz)}
  {stat_row("Verser", mastered_verses, TOTAL_VERSES, "#1a6fa8", pct_verse)}
  {stat_row("Ord", mastered_words, TOTAL_WORDS, "#8e44ad", pct_word)}
</div>
""", unsafe_allow_html=True)

    in_prog_surah  = total_added - mastered_count
    in_prog_verses = started_verses - mastered_verses
    in_prog_words  = started_words  - mastered_words

    st.markdown(f"""
<div style="background:var(--secondary-background-color);border-radius:10px;border:1px solid var(--border-color);padding:12px;margin-bottom:10px;">
  <div style="font-size:0.65em;opacity:0.5;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:8px;">Pagaende (S&lt;{MASTERED_S:.0f})</div>
  <div style="display:flex;justify-content:space-around;text-align:center;">
    <div>
      <div style="font-size:1.2em;font-weight:700;color:#d68910;">{in_prog_surah}</div>
      <div style="font-size:0.6em;opacity:0.55;">Suror</div>
    </div>
    <div style="width:1px;background:var(--border-color);"></div>
    <div>
      <div style="font-size:1.2em;font-weight:700;color:#d68910;">{in_prog_verses:,}</div>
      <div style="font-size:0.6em;opacity:0.55;">Verser</div>
    </div>
    <div style="width:1px;background:var(--border-color);"></div>
    <div>
      <div style="font-size:1.2em;font-weight:700;color:#d68910;">{in_prog_words:,}</div>
      <div style="font-size:0.6em;opacity:0.55;">Ord</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Retention histogram
    max_ret = max(ret_buckets) if any(ret_buckets) else 1
    bars_html = "<div style='display:flex;align-items:flex-end;gap:6px;height:60px;margin-top:4px;'>"
    for i in range(10):
        h = int((ret_buckets[i] / max_ret) * 52) if max_ret else 0
        bars_html += (
            f"<div style='flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;'>"
            f"<div style='font-size:0.6em;font-weight:600;color:{RET_COLORS[i]};'>{ret_buckets[i]}</div>"
            f"<div style='width:100%;height:{h}px;background:{RET_COLORS[i]};"
            f"border-radius:3px 3px 0 0;min-height:3px;'></div>"
            f"<div style='font-size:0.5em;opacity:0.5;text-align:center;line-height:1.1;'>{RET_LABELS[i]}</div>"
            f"</div>"
        )
    bars_html += "</div>"

    st.markdown(f"""
<div style="background:var(--secondary-background-color);border-radius:10px;border:1px solid var(--border-color);padding:12px;margin-bottom:10px;">
  <div style="font-size:0.65em;opacity:0.5;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">Retention-fordelning</div>
  {bars_html}
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:var(--secondary-background-color);border-radius:10px;border:1px solid var(--border-color);padding:10px 12px;margin-bottom:10px;">
  <div style="font-size:0.65em;opacity:0.5;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:6px;">Juz-ekvivalent (ord)</div>
  <div style="display:flex;align-items:baseline;gap:6px;">
    <span style="font-size:2em;font-weight:800;color:#b7950b;line-height:1;">{equiv_juz}</span>
    <span style="font-size:0.75em;opacity:0.55;">juz totalt</span>
  </div>
  <div style="font-size:0.65em;opacity:0.5;margin-top:3px;">varav <b>{juz_fully_mastered}</b> kompletta · {mastered_words:,} av {TOTAL_WORDS:,} ord</div>
  <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border-color);display:flex;align-items:baseline;gap:5px;">
    <span style="font-size:0.6em;opacity:0.45;">Om pagang. → bemasträd:</span>
    <span style="font-size:1.1em;font-weight:700;color:#b7950b;opacity:0.7;">{potential_equiv_juz}</span>
    <span style="font-size:0.6em;opacity:0.4;">juz · varav <b>{potential_juz_mastered}</b> kompletta</span>
  </div>
</div>
""", unsafe_allow_html=True)

    queue_today = [d for d in data if d["nasta_repetition"] <= today_str]
    if queue_today:
        st.markdown(f"""
<div style="background:rgba(192,57,43,0.08);border-radius:10px;border:1px solid rgba(192,57,43,0.25);padding:10px 12px;">
  <div style="font-size:0.7em;font-weight:600;color:#c0392b;">🎯 {len(queue_today)} kapitel att repetera idag</div>
  <div style="font-size:0.62em;opacity:0.6;margin-top:2px;">Ga till Session-fliken</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:rgba(26,122,74,0.08);border-radius:10px;border:1px solid rgba(26,122,74,0.25);padding:10px 12px;">
  <div style="font-size:0.7em;font-weight:600;color:#1a7a4a;">Inga repetitioner kvar idag</div>
</div>
""", unsafe_allow_html=True)


# ===================== SESSION =====================
with tab_idag:
    queue    = sorted([d for d in data if d["nasta_repetition"] <= today_str], key=lambda x: compute_retention(x, today))
    kommande = sorted([d for d in data if d["nasta_repetition"] > today_str],  key=lambda x: compute_retention(x, today))

    st.markdown("""
<style>
[data-testid="stSegmentedControl"] button {
    font-size: 0.15em !important;
    padding: 2px 6px !important;
    min-height: 0 !important;
}
[data-testid="stSegmentedControl"] {
    gap: 3px !important;
    flex-wrap: nowrap !important;
}
[data-testid="stSegmentedControl"] button {
    white-space: nowrap !important;
    flex-shrink: 1 !important;
}
</style>
""", unsafe_allow_html=True)

    def _session_card(item, key_prefix):
        s_val    = get_stability(item)
        r_val    = compute_retention(item, today)
        r_pct    = int(r_val * 100)
        chip_bg  = s_to_css(s_val)
        chip_lbl = f"{round(s_val)}d"
        with st.container(border=True):
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                f"<b style='font-size:0.9em;'>{item['namn']}</b>"
                f"<span style='display:flex;gap:5px;align-items:center;'>"
                f"<span style='font-size:0.68em;opacity:0.6;'>{r_pct}%</span>"
                f"<span style='font-size:0.68em;background:{chip_bg};color:white;"
                f"padding:1px 6px;border-radius:10px;font-weight:600;'>{chip_lbl}</span>"
                f"</span></div>",
                unsafe_allow_html=True,
            )
            key = f"{key_prefix}{item['id']}"
            st.segmented_control(
                "", GRADE_OPTIONS, key=key,
                label_visibility="collapsed",
                on_change=graded_action_callback, args=(item["id"], key),
            )

    if queue:
        for item in queue:
            _session_card(item, "act_dag_")
    else:
        st.success("Inga repetitioner kvar idag!")

    if kommande:
        for item in kommande:
            _session_card(item, "act_kom_")


# ===================== PROGRESS =====================
with tab_progress:
    st.markdown(
        "<div style='font-size:0.68em;opacity:0.5;text-transform:uppercase;"
        "letter-spacing:0.04em;margin-bottom:7px;'>Juz (1–30)</div>",
        unsafe_allow_html=True,
    )
    juz_html = "<div style='display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-bottom:8px;'>"
    for juz_num in range(1, 31):
        surahs  = JUZ_SURAHS.get(juz_num, [])
        total_w = JUZ_TOTAL_WORDS.get(juz_num, 0)
        mast_w  = sum(JUZ_SURAH_WORDS[juz_num].get(s, 0) for s in surahs if surah_stability.get(s, 0) >= MASTERED_S)
        start_w = sum(JUZ_SURAH_WORDS[juz_num].get(s, 0) for s in surahs if s in surah_stability)
        pct     = mast_w / total_w if total_w else 0
        pct_lbl = f"{round(pct * 100)}%"

        if mast_w == total_w and total_w > 0:
            bg, border, text_c, sub_c = "#1a7a4a", "#1a7a4a", "white", "rgba(255,255,255,0.75)"
        elif start_w > 0:
            alpha = round(0.15 + 0.6 * pct, 2)
            bg, border = f"rgba(26,122,74,{alpha})", "rgba(26,122,74,0.5)"
            text_c = sub_c = "var(--text-color)"
        else:
            bg, border = "rgba(128,128,128,0.1)", "var(--border-color)"
            text_c = sub_c = "var(--text-color)"

        tooltip = f"Juz {juz_num}: {mast_w:,}/{total_w:,} ord bemastrade ({pct_lbl})"
        juz_html += (
            f"<div title='{tooltip}' style='aspect-ratio:1;border-radius:6px;background:{bg};"
            f"border:1px solid {border};display:flex;flex-direction:column;"
            f"align-items:center;justify-content:center;cursor:default;'>"
            f"<div style='font-size:0.75em;font-weight:800;color:{text_c};line-height:1;'>{juz_num}</div>"
            f"<div style='font-size:0.47em;color:{sub_c};opacity:0.85;margin-top:1px;'>{pct_lbl}</div>"
            f"</div>"
        )
    juz_html += "</div>"
    juz_html += (
        "<div style='display:flex;gap:10px;font-size:0.61em;margin-bottom:12px;opacity:0.6;flex-wrap:wrap;'>"
        "<span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;"
        "background:rgba(128,128,128,0.12);border:1px solid var(--border-color);"
        "vertical-align:middle;margin-right:3px;'></span>Ej paaborjad</span>"
        "<span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;"
        "background:rgba(26,122,74,0.4);vertical-align:middle;margin-right:3px;'></span>Pagaende</span>"
        "<span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;"
        "background:#1a7a4a;vertical-align:middle;margin-right:3px;'></span>Klar</span>"
        "</div>"
    )
    st.markdown(juz_html, unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:0.68em;opacity:0.5;text-transform:uppercase;"
        "letter-spacing:0.04em;margin-bottom:7px;'>Suror per Juz</div>",
        unsafe_allow_html=True,
    )

    juz_surah_ordered: dict = {}
    for idx, juz in enumerate(SURAH_TO_JUZ):
        juz_surah_ordered.setdefault(juz, []).append((idx + 1, raw_surah_names[idx]))

    grid_html = ""
    for juz_num in range(1, 31):
        surahs_here = juz_surah_ordered.get(juz_num, [])
        if not surahs_here:
            continue

        total_w_bar = JUZ_TOTAL_WORDS.get(juz_num, 0)
        mast_w_bar  = sum(
            JUZ_SURAH_WORDS[juz_num].get(s, 0)
            for s in JUZ_SURAH_WORDS.get(juz_num, {})
            if surah_stability.get(s, 0) >= MASTERED_S
        )
        prog_w_bar  = sum(
            JUZ_SURAH_WORDS[juz_num].get(s, 0)
            for s in JUZ_SURAH_WORDS.get(juz_num, {})
            if s in surah_stability and surah_stability.get(s, 0) < MASTERED_S
        )
        mast_pct = round(mast_w_bar / total_w_bar * 100, 1) if total_w_bar else 0
        prog_pct = round(prog_w_bar / total_w_bar * 100, 1) if total_w_bar else 0
        segments = ""
        if mast_pct > 0:
            segments += f"<div style='width:{mast_pct}%;background:#1a7a4a;height:100%;'></div>"
        if prog_pct > 0:
            segments += f"<div style='width:{prog_pct}%;background:rgba(26,122,74,0.35);height:100%;'></div>"

        grid_html += (
            f"<div style='margin-bottom:11px;'>"
            f"<div style='display:flex;align-items:center;gap:7px;margin-bottom:4px;'>"
            f"<span style='font-size:0.65em;font-weight:700;opacity:0.45;white-space:nowrap;'>Juz {juz_num}</span>"
            f"<div style='flex:1;height:4px;background:rgba(128,128,128,0.15);border-radius:2px;"
            f"display:flex;overflow:hidden;'>{segments}</div>"
            f"<span style='font-size:0.58em;opacity:0.4;'>{mast_w_bar}/{total_w_bar}ord</span>"
            f"</div>"
            f"<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(62px,1fr));gap:5px;'>"
        )
        for (num, name) in surahs_here:
            s_val   = surah_stability.get(num, 0.0)
            r_val   = surah_retention.get(num, 0.0)
            r_pct   = int(r_val * 100)
            started = num in surah_stability

            if started:
                bg         = s_to_css(s_val, max(0.25, r_val))
                text_c     = "white"
                OP_MIN, OP_MAX = 0.35, 1.0
                op_t       = max(0.0, min(1.0, (r_val - 0.60) / 0.40))
                cell_op    = f"{OP_MIN + op_t * (OP_MAX - OP_MIN):.2f}"
                r_label    = f"{r_pct}%"
            else:
                bg         = "rgba(128,128,128,0.10)"
                text_c     = "var(--text-color)"
                cell_op    = "0.38"
                r_label    = ""

            tooltip = f"{num}. {name} — S={s_val:.1f}, retention {r_pct}%"
            grid_html += (
                f"<div title='{tooltip}' style='background:{bg};color:{text_c};opacity:{cell_op};"
                f"aspect-ratio:1;border-radius:5px;display:flex;flex-direction:column;"
                f"align-items:center;justify-content:center;padding:2px;"
                f"border:1px solid var(--border-color);overflow:hidden;cursor:help;'>"
                f"<div style='font-size:0.88em;font-weight:800;line-height:1;'>{num}</div>"
                f"<div style='font-size:0.43em;text-align:center;line-height:1.1;margin-top:2px;"
                f"display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;"
                f"overflow:hidden;width:100%;'>{name}</div>"
                f"<div style='font-size:0.45em;margin-top:2px;opacity:0.85;'>{r_label}</div>"
                f"</div>"
            )
        grid_html += "</div></div>"

    # Gradient legend replacing old S1–S5 step legend
    grid_html += (
        "<div style='display:flex;align-items:center;gap:8px;font-size:0.58em;margin-top:6px;opacity:0.55;'>"
        "<span style='white-space:nowrap;'>S=1</span>"
        "<div style='flex:1;height:6px;border-radius:3px;background:linear-gradient(to right,"
        "rgba(192,57,43,1) 0%,rgba(211,84,0,1) 25%,rgba(183,149,11,1) 50%,"
        "rgba(26,111,168,1) 75%,rgba(26,122,74,1) 100%);'></div>"
        "<span style='white-space:nowrap;'>S=500+</span>"
        "<span style='opacity:0.6;margin-left:6px;'>· opacity = retention</span>"
        "</div>"
    )
    st.markdown(grid_html, unsafe_allow_html=True)


# ===================== HANTERA =====================
with tab_hantera:
    search   = st.text_input("Sok surah...", "", placeholder="Namn...")
    filtered = [d for d in data if search.lower() in d["namn"].lower()]
    filtered.sort(key=lambda x: int(x["namn"].split(".")[0]) if x["namn"].split(".")[0].isdigit() else 999)

    if not filtered:
        st.info("Inga kapitel hittades.")

    for item in filtered:
        with st.container(border=True):
            s_val   = get_stability(item)
            r_val   = compute_retention(item, today)
            chip_bg = s_to_css(s_val)
            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            with c1:
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                    f"<b style='font-size:0.95em;'>{item['namn']}</b>"
                    f"<span style='font-size:0.66em;background:{chip_bg};color:white;"
                    f"padding:1px 8px;border-radius:10px;font-weight:600;'>"
                    f"S={s_val:.0f}d · {int(r_val*100)}%</span>"
                    f"</div>"
                    f"<div style='font-size:0.62em;opacity:0.45;margin-top:2px;'>"
                    f"Nasta: {item['nasta_repetition']}</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.button(
                    "🗑️", key=f"del_{item['id']}",
                    on_click=delete_item, args=(item["id"],),
                    use_container_width=True,
                )
            ce, csave = st.columns([3, 1])
            with ce:
                new_s = st.number_input(
                    "S", min_value=S_MIN, max_value=S_MAX,
                    value=float(max(S_MIN, min(S_MAX, round(s_val, 1)))), step=1.0,
                    key=f"ns_{item['id']}", label_visibility="collapsed",
                )
            with csave:
                if st.button("S ✏️", key=f"ss_{item['id']}", use_container_width=True):
                    update_stability(item["id"], new_s)
                    st.rerun()


# ===================== LAGG TILL =====================
with tab_lagg:
    metod = st.segmented_control("Metod", ["Enskilt", "Bulk"], default="Enskilt")

    if metod == "Enskilt":
        vald = st.selectbox("Surah", SURAH_LISTA)
        if st.button("Lagg till", type="primary", use_container_width=True):
            if not any(d["namn"] == vald for d in st.session_state.db_data):
                st.session_state.db_data.append({
                    "id": str(uuid.uuid4()),
                    "namn": vald,
                    "steg": s_to_steg(2.0),
                    "stability": 2.0,
                    "last_reviewed": today_str,
                    "nasta_repetition": today_str,
                })
                save_to_db(st.session_state.db_data)
                st.success(f"{vald} tillagd!")
            else:
                st.warning("Finns redan i din lista.")
    else:
        c1, c2 = st.columns(2)
        start = c1.selectbox("Fran", SURAH_LISTA, index=0)
        slut  = c2.selectbox("Till", SURAH_LISTA, index=10)
        if st.button("Lagg till alla", type="primary", use_container_width=True):
            i1, i2 = SURAH_LISTA.index(start), SURAH_LISTA.index(slut)
            if i1 > i2:
                st.error("'Fran' maste komma fore 'Till'.")
            else:
                added = 0
                for i in range(i1, i2 + 1):
                    namn = SURAH_LISTA[i]
                    if not any(d["namn"] == namn for d in st.session_state.db_data):
                        st.session_state.db_data.append({
                            "id": str(uuid.uuid4()),
                            "namn": namn,
                            "steg": s_to_steg(2.0),
                            "stability": 2.0,
                            "last_reviewed": today_str,
                            "nasta_repetition": today_str,
                        })
                        added += 1
                if added > 0:
                    save_to_db(st.session_state.db_data)
                    st.success(f"{added} kapitel tillagda!")
                else:
                    st.info("Alla valda kapitel finns redan.")
