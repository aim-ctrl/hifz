import streamlit as st
import requests
import datetime
import uuid

# --- KONFIGURATION & SECRETS ---
try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
    PIN_KOD = st.secrets["PIN_KOD"]
except KeyError:
    st.error("Saknar secrets! Se till att konfigurera JSONBIN_BIN_ID, JSONBIN_API_KEY och PIN_KOD i Streamlit Cloud.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- SURAH-LISTA (Exempel på de första, fyll på vid behov) ---
SURAH_LISTA = [
    "Al-Fatihah", "Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Ma'idah", 
    "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus", "Hud", "Yusuf",
    "Ar-Ra'd", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf"
]

# --- DATABASFUNKTIONER ---
def load_data():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get("record", [])
        return []
    except Exception as e:
        st.error(f"Ett fel uppstod vid hämtning: {e}")
        return []

def save_data(data):
    try:
        response = requests.put(URL, json=data, headers=HEADERS)
        if response.status_code != 200:
            st.error(f"Kunde inte spara data: {response.status_code}")
    except Exception as e:
        st.error(f"Ett fel uppstod vid sparning: {e}")

# --- LOGIK FÖR SPACED REPETITION ---
def calculate_next_date(current_step):
    today = datetime.date.today()
    # Intervall: Steg 1 (1 dag), 2 (3 dagar), 3 (7 dagar), 4+ (30 dagar)
    intervals = {1: 1, 2: 3, 3: 7, 4: 30, 5: 30}
    days = intervals.get(current_step, 1)
    return today + datetime.timedelta(days=days)

# --- SESSION STATE FÖR INLOGGNING ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- INLOGGNINGSSKÄRM ---
if not st.session_state.logged_in:
    st.title("🔒 Hifz Tracker Inloggning")
    pin_input = st.text_input("Ange PIN-kod", type="password")
    if st.button("Logga in"):
        if pin_input == PIN_KOD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Fel PIN-kod.")
    st.stop()

# --- HUVUDAPP ---
st.title("📖 Hifz Spaced Repetition")
data = load_data()

# Skapa flikar
tab1, tab2, tab3 = st.tabs(["Dagens Repetitioner", "Alla Kapitel", "Lägg till nytt"])

# --- FLIK 1: DAGENS REPETITIONER ---
with tab1:
    st.header("Att repetera idag")
    today_str = str(datetime.date.today())
    
    # Filtrera fram kapitel som ska repeteras idag eller tidigare
    to_review = [item for item in data if item.get("nasta_repetition", today_str) <= today_str]
    
    if not to_review:
        st.success("Bra jobbat! Du har inga fler repetitioner planerade för idag. 🎉")
    else:
        for item in to_review:
            with st.container():
                sid_info = f" (Sida: {item['sidor']})" if item.get('sidor') else ""
                st.subheader(f"{item['namn']}{sid_info}")
                st.write(f"Nuvarande steg: **{item['steg']}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Klarade det!", key=f"success_{item['id']}"):
                        item["steg"] = min(item["steg"] + 1, 5)
                        item["nasta_repetition"] = str(calculate_next_date(item["steg"]))
                        save_data(data)
                        st.rerun()
                with col2:
                    if st.button("❌ Behöver öva mer", key=f"fail_{item['id']}"):
                        item["steg"] = 1
                        item["nasta_repetition"] = today_str
                        save_data(data)
                        st.rerun()
                st.divider()

# --- FLIK 2: ALLA KAPITEL (HANTERING) ---
with tab2:
    st.header("Översikt & Ändra Steg")
    if not data:
        st.info("Inga kapitel tillagda ännu.")
    else:
        # Sortera data efter namn för lättare överblick
        sorted_data = sorted(data, key=lambda x: x['namn'])
        
        for i, item in enumerate(sorted_data):
            sid_info = f" (Sida: {item['sidor']})" if item.get('sidor') else ""
            with st.expander(f"{item['namn']}{sid_info} - Steg {item['steg']}"):
                
                # Manuellt ändra steg
                nytt_steg = st.select_slider(
                    f"Justera steg manuellt för {item['namn']}",
                    options=[1, 2, 3, 4, 5],
                    value=int(item['steg']),
                    key=f"slider_{item['id']}"
                )
                
                if nytt_steg != item['steg']:
                    item['steg'] = nytt_steg
                    item["nasta_repetition"] = str(calculate_next_date(nytt_steg))
                    save_data(data)
                    st.rerun() # Uppdaterar alla flikar direkt
                
                st.write(f"**Nästa repetition:** {item['nasta_repetition']}")
                
                if st.button("🗑️ Ta bort kapitel", key=f"delete_{item['id']}"):
                    data = [d for d in data if d['id'] != item['id']]
                    save_data(data)
                    st.rerun()

# --- FLIK 3: LÄGG TILL NYTT ---
with tab3:
    st.header("Lägg till ett nytt kapitel")
    
    val_namn = st.selectbox("Välj Surah från listan", SURAH_LISTA)
    eget_namn = st.text_input("Eller skriv eget namn (t.ex. Juz 30)")
    
    slutgiltigt_namn = eget_namn if eget_namn else val_namn
    
    # Valfritt sidintervall
    ange_sidor = st.checkbox("Ange specifika sidor")
    sido_text = ""
    
    if ange_sidor:
        col_s1, col_s2 = st.columns(2)
        sida_start = col_s1.number_input("Från sida", min_value=1, value=1, step=1)
        sida_slut = col_s2.number_input("Till sida", min_value=1, value=sida_start, step=1)
        sido_text = f"{int(sida_start)}-{int(sida_slut)}" if sida_start != sida_slut else f"{int(sida_start)}"

    if st.button("Spara kapitel"):
        if slutgiltigt_namn:
            new_item = {
                "id": str(uuid.uuid4()),
                "namn": slutgiltigt_namn,
                "sidor": sido_text,
                "steg": 1,
                "nasta_repetition": str(datetime.date.today())
            }
            data.append(new_item)
            save_data(data)
            st.success(f"Lade till {slutgiltigt_namn}!")
            st.rerun()
