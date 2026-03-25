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

# --- DATABASFUNKTIONER ---
def load_data():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get("record", [])
        else:
            st.error(f"Kunde inte hämta data: {response.status_code}")
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
    if current_step == 1:
        return today + datetime.timedelta(days=1)
    elif current_step == 2:
        return today + datetime.timedelta(days=3)
    elif current_step == 3:
        return today + datetime.timedelta(days=7)
    elif current_step >= 4:
        return today + datetime.timedelta(days=30)
    return today

def handle_success(item, data):
    item["steg"] += 1
    # Begränsa till max steg 5 (Manzil)
    if item["steg"] > 5:
        item["steg"] = 5
    
    item["nasta_repetition"] = str(calculate_next_date(item["steg"] - 1))
    save_data(data)
    st.rerun()

def handle_failure(item, data):
    item["steg"] = 1
    item["nasta_repetition"] = str(datetime.date.today())
    save_data(data)
    st.rerun()

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
    st.stop() # Stoppa appen här om man inte är inloggad

# --- HUVUDAPP ---
st.title("📖 Hifz Spaced Repetition")

# Hämta data
data = load_data()

# Skapa flikar
tab1, tab2, tab3 = st.tabs(["Dagens Repetitioner", "Alla Kapitel", "Lägg till nytt"])

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
                st.subheader(item["namn"])
                st.write(f"Nuvarande steg: **{item['steg']}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Klarade det felfritt!", key=f"success_{item['id']}"):
                        handle_success(item, data)
                with col2:
                    if st.button("❌ Tvekade/Gjorde fel", key=f"fail_{item['id']}"):
                        handle_failure(item, data)
                st.divider()

with tab2:
    st.header("Översikt över alla kapitel")
    if not data:
        st.info("Inga kapitel tillagda ännu.")
    else:
        for item in data:
            with st.expander(f"{item['namn']} (Steg {item['steg']})"):
                st.write(f"**Nästa repetition:** {item['nasta_repetition']}")
                if st.button("🗑️ Ta bort", key=f"delete_{item['id']}"):
                    data.remove(item)
                    save_data(data)
                    st.rerun()

with tab3:
    st.header("Lägg till ett nytt kapitel")
    new_name = st.text_input("Namn på Surah/Sida/Verser")
    if st.button("Lägg till"):
        if new_name:
            new_item = {
                "id": str(uuid.uuid4()),
                "namn": new_name,
                "steg": 1,
                "nasta_repetition": str(datetime.date.today())
            }
            data.append(new_item)
            save_data(data)
            st.success(f"Lade till {new_name}! Den dyker upp under Dagens Repetitioner.")
            st.rerun()
        else:
            st.warning("Du måste skriva in ett namn.")
