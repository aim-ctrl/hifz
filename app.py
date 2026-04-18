import streamlit as st
import requests
import datetime
import uuid

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

@st.cache_data(ttl=3600) # Cachas för att inte överbelasta API:et vid omladdning
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
        fetch_from_db.clear() # Töm cachen så nästa hämtning är färsk
    except Exception as e:
        st.error(f"Fel vid sparning: {e}")

# --- INITIERA SESSION STATE ---
if "db_data" not in st.session_state:
    st.session_state.db_data = fetch_from_db()

# --- CALLBACKS FÖR KNAPPAR (Logisk UX-förbättring) ---
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

# --- SIDEBAR (Statistik & Överblick) ---
with st.sidebar:
    st.header("📊 Din Statistik")
    total_added = len(st.session_state.db_data)
    st.metric("Påbörjade kapitel", f"{total_added} / 114")
    
    st.divider()
    st.subheader("Nivåfördelning")
    steg_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for d in st.session_state.db_data:
        steg_counts[d.get('steg', 1)] += 1
        
    for steg, count in steg_counts.items():
        st.write(f"Steg {steg}: {count} st")

# --- HUVUDAPP ---
st.title("📖 Spaced Repetition")
today_str = str(datetime.date.today())

tab_dagens, tab_hantera, tab_lagg_till = st.tabs(["🎯 Dagens pass", "📚 Översikt", "➕ Nytt kapitel"])

# --- FLIK 1: DAGENS PASS ---
with tab_dagens:
    repetition_queue = [d for d in st.session_state.db_data if d['nasta_repetition'] <= today_str]
    repetition_queue.sort(key=lambda x: x['nasta_repetition'])

    if not repetition_queue:
        st.success("🎉 Du har inga fler repetitioner planerade för idag! Bra jobbat.")
        st.balloons()
    else:
        st.info(f"Du har {len(repetition_queue)} kapitel att repetera idag.")
        for item in repetition_queue:
            # Använd Streamlits inbyggda border-containers för rena, mobila "cards"
            with st.container(border=True):
                col1, col2 = st.columns([3, 2]) # 3 delar text, 2 delar knappar
                
                with col1:
                    st.markdown(f"**{item['namn']}**")
                    st.caption(f"Aktuellt steg: {item['steg']} • Planerad: {item['nasta_repetition']}")
                
                with col2:
                    # Använd callbacks istället för st.rerun() if-satser
                    st.button("✅ Klar", key=f"done_{item['id']}", on_click=mark_done, args=(item['id'],), use_container_width=True, type="primary")
                    st.button("🔄 Igen", key=f"fail_{item['id']}", on_click=mark_failed, args=(item['id'],), use_container_width=True)

# --- FLIK 2: ÖVERSIKT OCH HANTERING ---
with tab_hantera:
    st.subheader("Alla dina kapitel")
    search_term = st.text_input("🔍 Sök efter en Surah...", "")
    
    filtered_data = [d for d in st.session_state.db_data if search_term.lower() in d['namn'].lower()]
    filtered_data.sort(key=lambda x: x['namn'])
    
    if not filtered_data:
        st.caption("Inga kapitel hittades.")
        
    for item in filtered_data:
        with st.expander(f"{item['namn']} - Steg {item['steg']}"):
            nytt_steg = st.slider("Ändra steg manuellt", 1, 5, int(item['steg']), key=f"slider_{item['id']}")
            
            # Om användaren drar i reglaget och det skiljer sig från databasen
            if nytt_steg != item['steg']:
                item['steg'] = nytt_steg
                item['nasta_repetition'] = str(calculate_next_date(nytt_steg))
                save_to_db(st.session_state.db_data)
                st.rerun() # Här kan rerun vara vettigt för att uppdatera expander-titeln
                
            st.button("🗑️ Ta bort från listan", key=f"del_{item['id']}", on_click=delete_item, args=(item['id'],))

# --- FLIK 3: LÄGG TILL ---
with tab_lagg_till:
    st.subheader("Börja repetera nytt kapitel")
    metod = st.segmented_control("Välj metod", ["Enskilt", "Bulk (Flera)"], default="Enskilt")
    
    if metod == "Enskilt":
        vald_surah = st.selectbox("Välj Surah", SURAH_LISTA)
        start_steg = st.radio("Starta på steg:", [1, 2, 3, 4, 5], horizontal=True)
        
        if st.button("➕ Lägg till", type="primary", use_container_width=True):
            if not any(d['namn'] == vald_surah for d in st.session_state.db_data):
                ny_data = {
                    "id": str(uuid.uuid4()), 
                    "namn": vald_surah, 
                    "steg": start_steg, 
                    "nasta_repetition": str(calculate_next_date(start_steg) if start_steg > 1 else today_str)
                }
                st.session_state.db_data.append(ny_data)
                save_to_db(st.session_state.db_data)
                st.success(f"Lade till {vald_surah}!")
            else:
                st.warning("Detta kapitel finns redan i din lista.")
                
    elif metod == "Bulk (Flera)":
        start_idx = st.selectbox("Från Surah", SURAH_LISTA, index=0)
        slut_idx = st.selectbox("Till Surah", SURAH_LISTA, index=10)
        
        if st.button("➕ Lägg till alla", type="primary", use_container_width=True):
            i1 = SURAH_LISTA.index(start_idx)
            i2 = SURAH_LISTA.index(slut_idx)
            
            if i1 > i2:
                st.error("'Från' måste komma före 'Till'.")
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
                else:
                    st.info("Alla valda kapitel fanns redan i din lista.")
