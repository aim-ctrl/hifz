import streamlit as st
import requests
import datetime
import uuid

# --- KONFIGURATION & SECRETS ---
try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
except KeyError:
    st.error("Saknar secrets! Se till att konfigurera JSONBIN_BIN_ID och JSONBIN_API_KEY i Streamlit Cloud.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

# Den fullständiga listan med alla 114 suror
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

# --- DATABASFUNKTIONER ---
def load_data():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            db_data = response.json()
            return db_data.get("record", [])
        return []
    except Exception as e:
        st.error(f"Ett fel uppstod vid hämtning: {e}")
        return []

def save_data(db_data):
    try:
        response = requests.put(URL, json=db_data, headers=HEADERS)
        if response.status_code != 200:
            st.error(f"Kunde inte spara data: {response.status_code}")
    except Exception as e:
        st.error(f"Ett fel uppstod vid sparning: {e}")

# --- LOGIK FÖR SPACED REPETITION ---
def calculate_next_date(current_step):
    today = datetime.date.today()
    intervals = {1: 0, 2: 1, 3: 3, 4: 7, 5: 30}
    days = intervals.get(current_step, 1)
    return today + datetime.timedelta(days=days)

# --- CSS ---
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        padding: 0px !important;
        min-height: 20px !important;
        height: 20px !important;
        width: 100% !important;
        font-size: 3px !important; 
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important; 
        margin-bottom: -8px !important; 
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) { width: 20% !important; min-width: 20% !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) { width: 17% !important; min-width: 17% !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(3) { width: 18% !important; min-width: 18% !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(4) { width: 15% !important; min-width: 15% !important; }
    [data-testid="column"] {
        padding-top: -2px !important;
        padding-bottom: -2px; !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    @media (max-width: 480px) {
        div[data-testid="stMarkdownContainer"] p {
            font-size: 12px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

data = load_data()

# Skapa 3 flikar (Tidigare flik 1 är borttagen)
tab1, tab2, tab3 = st.tabs(["Översikt", "Hantera Kapitel", "Lägg till nytt"])

# --- FLIK 1: VISUELL ÖVERSIKT (Tidigare Tab 2) ---
with tab1:
    table_data = []
    tillagda_dict = {item['namn']: item for item in data}
    
    for surah in SURAH_LISTA:
        if surah in tillagda_dict:
            item = tillagda_dict[surah]
            table_data.append({
                "namn": surah,
                "steg": int(item.get('steg', 1)),
                "datum": item.get('nasta_repetition', '-'),
                "id": item.get('id'),
                "tillagd": True
            })
        else:
            table_data.append({
                "namn": surah, "steg": 0, "datum": "-", "id": None, "tillagd": False
            })
            
    for item in data:
        if item['namn'] not in SURAH_LISTA:
            table_data.append({
                "namn": item['namn'],
                "steg": int(item.get('steg', 1)),
                "datum": item.get('nasta_repetition', '-'),
                "id": item.get('id'),
                "tillagd": True
            })

    sort_option = st.selectbox(
        "Sortera tabellen efter:", 
        ["Kapitel (Standardordning)", "Datum (Försenade först)", "Steg (Lägst först)", "Steg (Högst först)"]
    )
    
    today_str = str(datetime.date.today())
    
    if sort_option == "Datum (Försenade först)":
        table_data.sort(key=lambda x: x['datum'] if x['datum'] != "-" else "9999-99-99")
    elif sort_option == "Steg (Lägst först)":
        table_data.sort(key=lambda x: x['steg'])
    elif sort_option == "Steg (Högst först)":
        table_data.sort(key=lambda x: x['steg'], reverse=True)

    st.divider()
    
    kolumn_bredder = [3.5, 2, 2, 2.5]
    h1, h2, h3, h4 = st.columns(kolumn_bredder)
    header_style = "font-size: 0.5em; font-weight: bold; padding: 2px;"
    h1.markdown(f"<div style='{header_style}'>Kapitel</div>", unsafe_allow_html=True)
    h2.markdown(f"<div style='{header_style}'>Steg</div>", unsafe_allow_html=True)
    h3.markdown(f"<div style='{header_style}'>Datum</div>", unsafe_allow_html=True)
    h4.markdown(f"<div style='{header_style}'>Åtgärd</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0.1em 0; border: none; border-bottom: 2px solid #666;'>", unsafe_allow_html=True)
    
    for row in table_data:
        c1, c2, c3, c4 = st.columns(kolumn_bredder)
        is_overdue = row['tillagd'] and row['datum'] <= today_str
        bg_style = "background-color: rgba(255, 75, 75, 0.15); padding: 0px; font-size: 0.5em; border-radius: 4px;" if is_overdue else "padding: 0px; font-size: 0.5em;"
        cirklar = "🟢" * row['steg'] + "⚪" * (5 - row['steg']) if row['tillagd'] else "⚪⚪⚪⚪⚪"
        
        with c1:
            st.markdown(f"<div style='{bg_style}'>{row['namn']}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='{bg_style}'>{cirklar}</div>", unsafe_allow_html=True)
        with c3:
            datum_text = f"❗ {row['datum']}" if is_overdue else row['datum']
            st.markdown(f"<div style='{bg_style}'>{datum_text}</div>", unsafe_allow_html=True)
        with c4:
            if row['tillagd']:
                none_col, btn_col1, btn_col2 = st.columns([1,2,2])
                with btn_col1:
                    if st.button("✔", key=f"tab1_pass_{row['id']}"):
                        for d in data:
                            if d['id'] == row['id']:
                                d["steg"] = min(d["steg"] + 1, 5)
                                d["nasta_repetition"] = str(calculate_next_date(d["steg"]))
                                break
                        save_data(data)
                        st.rerun()
                with btn_col2:
                    if st.button("X", key=f"tab1_fail_{row['id']}"):
                        for d in data:
                            if d['id'] == row['id']:
                                d["steg"] = 1
                                d["nasta_repetition"] = today_str
                                break
                        save_data(data)
                        st.rerun()
            else:
                st.markdown("<div style='padding: 2px; color: #888; font-size: 0.85em;'>Ej tillagd</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 0.1em 0; border: none; border-bottom: 1px solid #ddd;'>", unsafe_allow_html=True)

# --- FLIK 2: HANTERA KAPITEL (Tidigare Tab 3) ---
with tab2:
    if not data:
        st.info("Inga kapitel tillagda ännu.")
    else:
        sorted_data = sorted(data, key=lambda x: x['namn'])
        for item in sorted_data:
            sid_info = f" (Sida: {item['sidor']})" if item.get('sidor') else ""
            with st.expander(f"{item['namn']}{sid_info} - Steg {item['steg']}"):
                nytt_steg = st.select_slider(f"Justera steg för {item['namn']}", options=[1, 2, 3, 4, 5], value=int(item['steg']), key=f"slider_{item['id']}")
                if nytt_steg != item['steg']:
                    item['steg'] = nytt_steg
                    item["nasta_repetition"] = str(calculate_next_date(nytt_steg))
                    save_data(data)
                    st.rerun()
                if st.button("🗑️ Ta bort kapitel", key=f"delete_{item['id']}"):
                    data = [d for d in data if d['id'] != item['id']]
                    save_data(data)
                    st.rerun()

# --- FLIK 3: LÄGG TILL NYTT (Tidigare Tab 4) ---
with tab3:    
    add_mode = st.radio("Metod:", ["Enskilt kapitel", "Bulk"], horizontal=True)
    if add_mode == "Enskilt kapitel":
        val_namn = st.selectbox("Välj Surah", SURAH_LISTA)
        eget_namn = st.text_input("Eller eget namn")
        slutgiltigt_namn = eget_namn if eget_namn else val_namn
        ange_sidor = st.checkbox("Ange sidor")
        sido_text = ""
        if ange_sidor:
            col_s1, col_s2 = st.columns(2)
            s_start = col_s1.number_input("Från", min_value=1, value=1)
            s_slut = col_s2.number_input("Till", min_value=1, value=s_start)
            sido_text = f"{int(s_start)}-{int(s_slut)}" if s_start != s_slut else f"{int(s_start)}"
        vald_steg = st.select_slider("Start-steg", options=[1, 2, 3, 4, 5], value=1)
        if st.button("Spara kapitel"):
            new_item = {"id": str(uuid.uuid4()), "namn": slutgiltigt_namn, "sidor": sido_text, "steg": vald_steg, "nasta_repetition": str(calculate_next_date(vald_steg)) if vald_steg > 1 else str(datetime.date.today())}
            data.append(new_item)
            save_data(data)
            st.rerun()
    else:
        c_b1, c_b2 = st.columns(2)
        start_s = c_b1.selectbox("Från", SURAH_LISTA)
        slut_s = c_b2.selectbox("Till", SURAH_LISTA)
        bulk_steg = st.select_slider("Steg för alla", options=[1, 2, 3, 4, 5], value=1)
        if st.button("Spara bulk"):
            s_idx, e_idx = SURAH_LISTA.index(start_s), SURAH_LISTA.index(slut_s)
            for i in range(s_idx, e_idx + 1):
                if not any(d['namn'] == SURAH_LISTA[i] for d in data):
                    data.append({"id": str(uuid.uuid4()), "namn": SURAH_LISTA[i], "sidor": "", "steg": bulk_steg, "nasta_repetition": str(calculate_next_date(bulk_steg))})
            save_data(data)
            st.rerun()
