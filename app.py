import streamlit as st
import requests
import datetime
import uuid
import pandas as pd
from collections import Counter
import plotly.graph_objects as go # Ny import för speedometers

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
    days = intervals.get(current_step, 1)
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
        requests.put(URL, json=data_to_save, headers=HEADERS)
        fetch_from_db.clear()
    except Exception as e:
        st.error(f"Fel vid sparning: {e}")

# --- INITIERA SESSION STATE ---
if "db_data" not in st.session_state:
    st.session_state.db_data = fetch_from_db()

# --- CALLBACKS FÖR KNAPPAR ---
def mark_done(item_id):
    for d in st.session_state.db_data:
        if d['id'] == item_id:
            d["steg"] = min(d["steg"] + 1, 5)
            d["nasta_repetition"] = str(calculate_next_date(d["steg"]))
            st.toast(f"✅ {d['namn']} uppflyttad till steg {d['steg']}!")
            break
    save_to_db(st.session_state.db_data)

def mark_failed(item_id):
    for d in st.session_state.db_data:
        if d['id'] == item_id:
            d["steg"] = 1
            d["nasta_repetition"] = str(datetime.date.today())
            st.toast(f"🔄 {d['namn']} återställd till steg 1.")
            break
    save_to_db(st.session_state.db_data)

def delete_item(item_id):
    st.session_state.db_data = [d for d in st.session_state.db_data if d['id'] != item_id]
    save_to_db(st.session_state.db_data)
    st.toast("🗑️ Kapitel borttaget.")

# --- PLOTLY SPEEDOMETER FUNKTION ---
def create_gauge(value, max_val, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14, 'color': 'gray'}},
        number={'font': {'size': 26, 'color': '#333'}},
        gauge={
            'axis': {'range': [0, max_val], 'visible': False},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#f2f2f2",
            'borderwidth': 0,
        }
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=140,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Arial, sans-serif"}
    )
    return fig

# --- TOPP: STATISTIK (Ersätter gamla titeln & sidebaren) ---
total_added = len(st.session_state.db_data)
steg_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for d in st.session_state.db_data:
    steg_counts[d.get('steg', 1)] += 1

# Designval UX: Att rita 6 stora speedometers blir rörigt på en liten mobilskärm. 
# Vi ritar 2 huvudsakliga speedometers, och en ren siffer-rad för stegen nedanför.
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(create_gauge(total_added, 114, "Påbörjade", "#007BFF"), use_container_width=True, config={'displayModeBar': False})
with col_g2:
    st.plotly_chart(create_gauge(steg_counts[5], 114, "Bemästrade (Steg 5)", "#28A745"), use_container_width=True, config={'displayModeBar': False})

# Små mätare/värden för stegen (perfekt för att se fördelning snabbt)
st.caption("📈 Kapitel per steg:")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Steg 1", steg_counts[1])
c2.metric("Steg 2", steg_counts[2])
c3.metric("Steg 3", steg_counts[3])
c4.metric("Steg 4", steg_counts[4])
c5.metric("Steg 5", steg_counts[5])

st.divider() # Skapar en snygg avskiljare innan flikarna

# --- HUVUDAPP ---
today_str = str(datetime.date.today())

tab_dagens, tab_kommande, tab_hantera, tab_diagram, tab_lagg_till = st.tabs([
    "🎯 Dagens", "⏳ Kommande", "📚 Översikt", "📊 Kalender", "➕ Nytt"
])

# --- FLIK 1: DAGENS PASS ---
with tab_dagens:
    repetition_queue = [d for d in st.session_state.db_data if d['nasta_repetition'] <= today_str]
    repetition_queue.sort(key=lambda x: x['nasta_repetition'])

    if not repetition_queue:
        st.success("🎉 Inga fler repetitioner planerade för idag!")
    else:
        for item in repetition_queue:
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{item['namn']}**")
                    st.caption(f"Steg: {item['steg']} • Planerad: {item['nasta_repetition']}")
                with col2:
                    st.button("✅ Klar", key=f"done_dagens_{item['id']}", on_click=mark_done, args=(item['id'],), use_container_width=True, type="primary")
                    st.button("🔄 Igen", key=f"fail_dagens_{item['id']}", on_click=mark_failed, args=(item['id'],), use_container_width=True)

# --- FLIK 2: KOMMANDE ---
with tab_kommande:
    kommande_queue = [d for d in st.session_state.db_data if d['nasta_repetition'] > today_str]
    kommande_queue.sort(key=lambda x: x['nasta_repetition'])

    if not kommande_queue:
        st.info("Inga framtida repetitioner är inplanerade just nu.")
    else:
        for item in kommande_queue:
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{item['namn']}**")
                    st.caption(f"Steg: {item['steg']} • Inplanerad: {item['nasta_repetition']}")
                with col2:
                    st.button("✅ Kör nu", key=f"done_kommande_{item['id']}", on_click=mark_done, args=(item['id'],), use_container_width=True)
                    st.button("🔄 Igen", key=f"fail_kommande_{item['id']}", on_click=mark_failed, args=(item['id'],), use_container_width=True)

# --- FLIK 3: ÖVERSIKT OCH HANTERING ---
with tab_hantera:
    search_term = st.text_input("🔍 Sök Surah...", "")
    filtered_data = [d for d in st.session_state.db_data if search_term.lower() in d['namn'].lower()]
    filtered_data.sort(key=lambda x: x['namn'])
        
    for item in filtered_data:
        with st.expander(f"{item['namn']} - Steg {item['steg']} (Nästa: {item['nasta_repetition']})"):
            nytt_steg = st.slider("Ändra steg manuellt", 1, 5, int(item['steg']), key=f"slider_{item['id']}")
            if nytt_steg != item['steg']:
                item['steg'] = nytt_steg
                item['nasta_repetition'] = str(calculate_next_date(nytt_steg))
                save_to_db(st.session_state.db_data)
                st.rerun()
            st.button("🗑️ Ta bort", key=f"del_{item['id']}", on_click=delete_item, args=(item['id'],))

# --- FLIK 4: DIAGRAM ---
with tab_diagram:
    st.write("Antal kapitel inplanerade per datum framöver:")
    if st.session_state.db_data:
        alla_datum = [d['nasta_repetition'] for d in st.session_state.db_data]
        datum_raknare = Counter(alla_datum)
        df_diagram = pd.DataFrame(list(datum_raknare.items()), columns=['Datum', 'Antal kapitel'])
        df_diagram = df_diagram.sort_values('Datum')
        st.bar_chart(df_diagram.set_index('Datum'))
    else:
        st.info("Lägg till kapitel för att se statistik!")

# --- FLIK 5: LÄGG TILL ---
with tab_lagg_till:
    metod = st.segmented_control("Välj metod", ["Enskilt", "Bulk (Flera)"], default="Enskilt")
    
    if metod == "Enskilt":
        vald_surah = st.selectbox("Välj Surah", SURAH_LISTA)
        start_steg = st.radio("Starta på steg:", [1, 2, 3, 4, 5], horizontal=True)
        if st.button("➕ Lägg till", type="primary", use_container_width=True):
            if not any(d['namn'] == vald_surah for d in st.session_state.db_data):
                st.session_state.db_data.append({
                    "id": str(uuid.uuid4()), "namn": vald_surah, "steg": start_steg, 
                    "nasta_repetition": str(calculate_next_date(start_steg) if start_steg > 1 else today_str)
                })
                save_to_db(st.session_state.db_data)
                st.success(f"Lade till {vald_surah}!")
            else:
                st.warning("Detta kapitel finns redan.")
                
    elif metod == "Bulk (Flera)":
        c1, c2 = st.columns(2)
        start_idx = c1.selectbox("Från", SURAH_LISTA, index=0)
        slut_idx = c2.selectbox("Till", SURAH_LISTA, index=10)
        
        if st.button("➕ Lägg till alla", type="primary", use_container_width=True):
            i1, i2 = SURAH_LISTA.index(start_idx), SURAH_LISTA.index(slut_idx)
            if i1 > i2:
                st.error("'Från' måste vara före 'Till'.")
            else:
                tillagda = 0
                for i in range(i1, i2 + 1):
                    namn = SURAH_LISTA[i]
                    if not any(d['namn'] == namn for d in st.session_state.db_data):
                        st.session_state.db_data.append({
                            "id": str(uuid.uuid4()), "namn": namn, "steg": 1, "nasta_repetition": today_str
                        })
                        tillagda += 1
                if tillagda > 0:
                    save_to_db(st.session_state.db_data)
                    st.success(f"Lade till {tillagda} nya kapitel!")
