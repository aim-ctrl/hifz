import streamlit as st
import requests
import datetime
import uuid
import pandas as pd
import json

# --- KONFIGURATION & SECRETS ---
st.set_page_config(page_title="Quran Repetition", page_icon="📖", layout="centered")

try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
except KeyError:
    st.error("Saknar secrets! Se till att konfigurera JSONBIN_BIN_ID och JSONBIN_API_KEY i Streamlit Cloud.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

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

# --- HJÄLPFUNKTIONER ---
def calculate_next_date(current_step):
    today = datetime.date.today()
    intervals = {1: 0, 2: 1, 3: 3, 4: 7, 5: 30}
    days = intervals.get(int(current_step), 1)
    return today + datetime.timedelta(days=days)

@st.cache_data(ttl=3600)
def fetch_from_db():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("record", [])
    except Exception as e:
        st.error(f"Kunde inte ladda data: {e}")
    return []

def save_to_db(data_to_save):
    try:
        response = requests.put(URL, json=data_to_save, headers=HEADERS)
        if response.status_code != 200:
            st.error(f"Ett fel uppstod vid kontakt med databasen.")
        fetch_from_db.clear()
    except Exception as e:
        st.error(f"Fel vid sparning: {e}")

# --- INITIERA SESSION STATE ---
if "db_data" not in st.session_state:
    st.session_state.db_data = fetch_from_db()

# --- CALLBACKS FÖR KNAPPAR ---
def mark_done(item_id):
    for d in st.session_state.db_data:
        if str(d['id']) == str(item_id):
            nuvarande_steg = int(d.get("steg", 1))
            nytt_steg = min(nuvarande_steg + 1, 5)
            
            d["steg"] = nytt_steg
            d["nasta_repetition"] = str(calculate_next_date(nytt_steg))
            
            seg_key = f"seg_{item_id}"
            if seg_key in st.session_state:
                st.session_state[seg_key] = nytt_steg
                
            st.toast(f"✅ {d['namn']} -> Steg {nytt_steg}!")
            
            if nytt_steg == 5 and nuvarande_steg != 5:
                st.balloons()
            break
    save_to_db(st.session_state.db_data)

def mark_failed(item_id):
    for d in st.session_state.db_data:
        if str(d['id']) == str(item_id):
            d["steg"] = 1
            d["nasta_repetition"] = str(datetime.date.today())
            
            seg_key = f"seg_{item_id}"
            if seg_key in st.session_state:
                st.session_state[seg_key] = 1
                
            st.toast(f"🔄 {d['namn']} återställd.")
            break
    save_to_db(st.session_state.db_data)

def delete_item(item_id):
    st.session_state.db_data = [d for d in st.session_state.db_data if str(d['id']) != str(item_id)]
    save_to_db(st.session_state.db_data)
    st.toast("🗑️ Kapitel borttaget.")

# --- AGGRESSIV MOBIL-CSS ---
st.markdown('''
    <style>
    /* 1. Tvinga kolumner att stanna på samma rad på mobilen */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.3rem !important;
        align-items: center !important;
    }
    
    /* 2. Minska padding kraftigt i "korten" (containers) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0.4rem 0.5rem !important;
    }
    
    /* 3. Krymp knapparnas storlek för att passa perfekt */
    div[data-testid="stButton"] button {
        padding: 0.1rem 0.3rem !important;
        min-height: 2.2rem !important;
    }
    
    /* 4. Skala bort onödiga marginaler generellt */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        gap: 0rem;
    }
    </style>
''', unsafe_allow_html=True)

# --- TOPP: KOMPAKT STATISTIK ---
total_added = len(st.session_state.db_data)
steg_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for d in st.session_state.db_data:
    steg_counts[int(d.get('steg', 1))] += 1

progress_pct = int((total_added / 114) * 100) if total_added > 0 else 0

html_kod = f"""<div style="background-color: var(--secondary-background-color); padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 5px;">
<div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 5px;">
<div style="text-align: center;">
<div style="font-size: 0.7em; opacity: 0.7; text-transform: uppercase;">Påbörjade</div>
<div style="font-size: 1.4em; font-weight: 800; color: #4DA3FF; line-height: 1;">{total_added}<span style="font-size: 0.5em; opacity: 0.5;">/114</span></div>
</div>
<div style="width: 1px; height: 25px; background-color: var(--border-color);"></div>
<div style="text-align: center;">
<div style="font-size: 0.7em; opacity: 0.7; text-transform: uppercase;">Bemästrade</div>
<div style="font-size: 1.4em; font-weight: 800; color: #28A745; line-height: 1;">{steg_counts[5]}</div>
</div>
</div>
<div style="width: 100%; background-color: var(--background-color); border-radius: 4px; height: 5px; margin-bottom: 5px;">
<div style="width: {progress_pct}%; background-color: #4DA3FF; height: 5px; border-radius: 4px;"></div>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.7em; padding: 0 2px; font-weight: 500;">
<span>S1:<b style="color:#ff4b4b;">{steg_counts[1]}</b></span> <span>S2:<b>{steg_counts[2]}</b></span> <span>S3:<b>{steg_counts[3]}</b></span> <span>S4:<b>{steg_counts[4]}</b></span> <span>S5:<b style="color:#28A745;">{steg_counts[5]}</b></span>
</div>
</div>"""
st.markdown(html_kod, unsafe_allow_html=True)

# --- HUVUDAPP ---
today_str = str(datetime.date.today())

tab_dagens, tab_kommande, tab_hantera, tab_diagram, tab_lagg_till = st.tabs([
    "🎯 Idag", "⏳ Komm.", "📚 Översikt", "📊 Graf", "➕ Nytt"
])

# --- FLIK 1: DAGENS PASS ---
with tab_dagens:
    repetition_queue = [d for d in st.session_state.db_data if d['nasta_repetition'] <= today_str]
    repetition_queue.sort(key=lambda x: x['nasta_repetition'])

    if not repetition_queue:
        st.success("🎉 Inga fler repetitioner idag!")
    else:
        for item in repetition_queue:
            with st.container(border=True):
                # 6 delar text, 2 delar klar, 2 delar fail - tvingas på en horisontell linje nu
                col_text, col_done, col_fail = st.columns([6, 2, 2])
                with col_text:
                    st.markdown(f"<div style='line-height:1.2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'><b style='font-size:0.95em;'>{item['namn']}</b><br><span style='font-size:0.75em; opacity:0.7;'>S{item['steg']} • {item['nasta_repetition']}</span></div>", unsafe_allow_html=True)
                with col_done:
                    st.button("✅", key=f"done_dagens_{item['id']}", on_click=mark_done, args=(item['id'],), help="Klar", use_container_width=True, type="primary")
                with col_fail:
                    st.button("🔄", key=f"fail_dagens_{item['id']}", on_click=mark_failed, args=(item['id'],), help="Igen (Steg 1)", use_container_width=True)

# --- FLIK 2: KOMMANDE ---
with tab_kommande:
    kommande_queue = [d for d in st.session_state.db_data if d['nasta_repetition'] > today_str]
    kommande_queue.sort(key=lambda x: x['nasta_repetition'])

    if not kommande_queue:
        st.info("Inga framtida repetitioner inplanerade.")
    else:
        for item in kommande_queue:
            with st.container(border=True):
                col_text, col_done, col_fail = st.columns([6, 2, 2])
                with col_text:
                    st.markdown(f"<div style='line-height:1.2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'><b style='font-size:0.95em;'>{item['namn']}</b><br><span style='font-size:0.75em; opacity:0.7;'>S{item['steg']} • {item['nasta_repetition']}</span></div>", unsafe_allow_html=True)
                with col_done:
                    st.button("✅", key=f"done_kommande_{item['id']}", on_click=mark_done, args=(item['id'],), help="Kör i förväg", use_container_width=True)
                with col_fail:
                    st.button("🔄", key=f"fail_kommande_{item['id']}", on_click=mark_failed, args=(item['id'],), help="Återställ (Steg 1)", use_container_width=True)

# --- FLIK 3: ÖVERSIKT OCH HANTERING ---
with tab_hantera:
    search_term = st.text_input("🔍 Sök Surah...", "")
    filtered_data = [d for d in st.session_state.db_data if search_term.lower() in d['namn'].lower()]
    
    def get_sort_key(item):
        try: return int(item['namn'].split('.')[0])
        except ValueError: return 999 
    filtered_data.sort(key=get_sort_key)
        
    if not filtered_data:
        st.info("Inga kapitel hittades.")
        
    for item in filtered_data:
        with st.container(border=True):
            col_text, col_steg, col_knapp = st.columns([3, 4, 1])
            with col_text:
                st.markdown(f"<div style='line-height:1.2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'><b style='font-size:0.9em;'>{item['namn']}</b><br><span style='font-size:0.7em; opacity:0.7;'>{item['nasta_repetition']}</span></div>", unsafe_allow_html=True)
            with col_steg:
                nytt_steg = st.segmented_control("St", options=[1, 2, 3, 4, 5], default=int(item['steg']), key=f"seg_{item['id']}", label_visibility="collapsed")
                if nytt_steg and nytt_steg != int(item['steg']):
                    item['steg'] = nytt_steg
                    item['nasta_repetition'] = str(calculate_next_date(nytt_steg))
                    st.session_state[f"seg_{item['id']}"] = nytt_steg
                    save_to_db(st.session_state.db_data)
                    st.rerun()
            with col_knapp:
                st.button("🗑️", key=f"del_{item['id']}", on_click=delete_item, args=(item['id'],), help="Ta bort", use_container_width=True)

# --- FLIK 4: DIAGRAM ---
with tab_diagram:
    st.write("Visuell arbetsbelastning uppdelad i steg:")
    if not st.session_state.db_data:
        st.info("Lägg till kapitel för att se din planering!")
    else:
        df = pd.DataFrame(st.session_state.db_data)
        df['nasta_repetition'] = pd.to_datetime(df['nasta_repetition']).dt.date
        df['steg'] = df['steg'].astype(int) 
        idag = datetime.date.today()
        max_datum = df['nasta_repetition'].max()
        if pd.isna(max_datum) or max_datum < idag:
            max_datum = idag + datetime.timedelta(days=7)
            
        alla_dagar = pd.date_range(start=idag, end=max_datum).date
        chart_data = df.groupby(['nasta_repetition', 'steg']).size().unstack(fill_value=0)
        chart_data = chart_data.reindex(alla_dagar, fill_value=0)
        for i in range(1, 6):
            if i not in chart_data.columns: chart_data[i] = 0
                
        chart_data = chart_data[[1, 2, 3, 4, 5]]
        chart_data.columns = ["Steg 1", "Steg 2", "Steg 3", "Steg 4", "Steg 5"]
        steg_farger = ["#ff4b4b", "#ffa500", "#ffd700", "#4DA3FF", "#28A745"]
        st.bar_chart(chart_data, color=steg_farger)
        st.divider() 
        
        st.markdown("<div style='font-size: 0.8em; color: #666; text-transform: uppercase;'>📅 Kapitel framöver:</div>", unsafe_allow_html=True)
        dagar_med_krav = df.groupby('nasta_repetition')
        
        for datum, group in dagar_med_krav:
            if len(group) == 0: continue
            is_past = datum < idag
            status_icon = "⚠️" if is_past else "📍"
            with st.expander(f"{status_icon} {datum} ({len(group)} st)"):
                for _, rad in group.iterrows():
                    st.markdown(f"- **{rad['namn']}** (S{rad['steg']})")

# --- FLIK 5: LÄGG TILL ---
with tab_lagg_till:
    metod = st.segmented_control("Välj metod", ["Enskilt", "Bulk (Flera)"], default="Enskilt")
    if metod == "Enskilt":
        vald_surah = st.selectbox("Välj Surah", SURAH_LISTA)
        start_steg = st.radio("Starta på steg:", [1, 2, 3, 4, 5], horizontal=True)
        if st.button("➕ Lägg till", type="primary", use_container_width=True):
            if not any(d['namn'] == vald_surah for d in st.session_state.db_data):
                st.session_state.db_data.append({"id": str(uuid.uuid4()), "namn": vald_surah, "steg": start_steg, "nasta_repetition": str(calculate_next_date(start_steg) if start_steg > 1 else today_str)})
                save_to_db(st.session_state.db_data)
                st.success(f"Lade till {vald_surah}!")
            else:
                st.warning("Detta kapitel finns redan i din lista.")
    elif metod == "Bulk (Flera)":
        c1, c2 = st.columns(2)
        start_idx = c1.selectbox("Från", SURAH_LISTA, index=0)
        slut_idx = c2.selectbox("Till", SURAH_LISTA, index=10)
        if st.button("➕ Lägg till alla", type="primary", use_container_width=True):
            i1, i2 = SURAH_LISTA.index(start_idx), SURAH_LISTA.index(slut_idx)
            if i1 > i2: st.error("'Från' måste vara före 'Till'.")
            else:
                tillagda = 0
                for i in range(i1, i2 + 1):
                    namn = SURAH_LISTA[i]
                    if not any(d['namn'] == namn for d in st.session_state.db_data):
                        st.session_state.db_data.append({"id": str(uuid.uuid4()), "namn": namn, "steg": 1, "nasta_repetition": today_str})
                        tillagda += 1
                if tillagda > 0:
                    save_to_db(st.session_state.db_data)
                    st.success(f"Lade till {tillagda} nya kapitel!")
