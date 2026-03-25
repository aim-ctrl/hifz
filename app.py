import streamlit as st
import requests
import datetime
import uuid

# --- KONFIGURATION & SECRETS (Samma som tidigare) ---
try:
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    API_KEY = st.secrets["JSONBIN_API_KEY"]
    PIN_KOD = st.secrets["PIN_KOD"]
except KeyError:
    st.error("Saknar secrets! Se till att konfigurera JSONBIN_BIN_ID, JSONBIN_API_KEY och PIN_KOD.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

# Lista med Surah-namn (Exempel - du kan fylla på hela listan)
SURAH_LISTA = [
    "Al-Fatihah", "Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Ma'idah", 
    "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus"
    # ... fyll på med fler vid behov
]

# --- DATABASFUNKTIONER ---
def load_data():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("record", [])
        return []
    except:
        return []

def save_data(data):
    requests.put(URL, json=data, headers=HEADERS)

def calculate_next_date(current_step):
    today = datetime.date.today()
    intervals = {1: 1, 2: 3, 3: 7, 4: 30, 5: 30}
    days = intervals.get(current_step, 1)
    return today + datetime.timedelta(days=days)

# --- SESSION STATE & INLOGGNING ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Hifz Tracker")
    if st.text_input("Ange PIN-kod", type="password") == PIN_KOD:
        if st.button("Logga in"):
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- HUVUDAPP ---
st.title("📖 Hifz Spaced Repetition")
data = load_data()

tab1, tab2, tab3 = st.tabs(["Dagens Repetitioner", "Alla Kapitel", "Lägg till nytt"])

with tab1:
    st.header("Att repetera idag")
    today_str = str(datetime.date.today())
    to_review = [item for item in data if item.get("nasta_repetition", today_str) <= today_str]
    
    if not to_review:
        st.success("Bra jobbat! 🎉")
    else:
        for item in to_review:
            with st.expander(f"📖 {item['namn']} (Sid: {item.get('sidor', 'N/A')})"):
                st.write(f"Nuvarande steg: **{item['steg']}**")
                c1, c2 = st.columns(2)
                if c1.button("✅ Felfritt", key=f"ok_{item['id']}"):
                    item["steg"] = min(item["steg"] + 1, 5)
                    item["nasta_repetition"] = str(calculate_next_date(item["steg"]))
                    save_data(data)
                    st.rerun()
                if c2.button("❌ Repetera", key=f"fail_{item['id']}"):
                    item["steg"] = 1
                    item["nasta_repetition"] = today_str
                    save_data(data)
                    st.rerun()

with tab2:
    st.header("Hantera kapitel")
    for i, item in enumerate(data):
        with st.expander(f"{item['namn']} - Steg {item['steg']}"):
            # Manuellt ändra steg
            nytt_steg = st.slider("Ändra steg manuellt", 1, 5, int(item['steg']), key=f"slider_{item['id']}")
            if nytt_steg != item['steg']:
                item['steg'] = nytt_steg
                item["nasta_repetition"] = str(calculate_next_date(nytt_steg))
                save_data(data)
                st.toast(f"Uppdaterade {item['namn']} till steg {nytt_steg}")
            
            st.write(f"Nästa datum: {item['nasta_repetition']}")
            if st.button("🗑️ Ta bort", key=f"del_{item['id']}"):
                data.pop(i)
                save_data(data)
                st.rerun()

with tab3:
    st.header("Lägg till nytt")
    # Dropdown för namn
    val d_namn = st.selectbox("Välj Surah", SURAH_LISTA)
    
    # Sida/Sidintervall
    col_s1, col_s2 = st.columns(2)
    sida_start = col_s1.number_input("Från sida", min_value=1, value=1)
    sida_slut = col_s2.number_input("Till sida (valfritt)", min_value=1, value=sida_start)
    
    sido_text = f"{sida_start}-{sida_slut}" if sida_start != sida_slut else f"{sida_start}"

    if st.button("Lägg till i listan"):
        new_item = {
            "id": str(uuid.uuid4()),
            "namn": val_namn,
            "sidor": sido_text,
            "steg": 1,
            "nasta_repetition": str(datetime.date.today())
        }
        data.append(new_item)
        save_data(data)
        st.success(f"Lade till {val_namn} (Sida {sido_text})")
        st.rerun()
