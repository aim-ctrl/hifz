import streamlit as st
import requests
import datetime
import uuid

# --- KONFIGURATION & SECRETS ---
# Vi hämtar nu bara databasnycklarna och ignorerar PIN-koden
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

# Skapar den formaterade listan med nummer före namnet
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


# --- HUVUDAPP ---
# Appen laddas nu direkt utan någon inloggningsskärm
data = load_data()

# Skapa 4 flikar
tab1, tab2, tab3, tab4 = st.tabs(["Repetitioner", "Visuell Översikt", "Hantera Kapitel", "Lägg till nytt"])

# --- FLIK 1: DAGENS REPETITIONER ---
with tab1:
    today_str = str(datetime.date.today())
    
    # Filtrera ut de som ska repeteras idag eller tidigare
    to_review = [item for item in data if item.get("nasta_repetition", today_str) <= today_str]
    
    # Sortera listan efter datum (stigande, så äldst kommer först)
    to_review = sorted(to_review, key=lambda x: x.get("nasta_repetition", today_str))
    
    if not to_review:
        st.success("Bra jobbat! Du har inga fler repetitioner planerade för idag. 🎉")
    else:
        st.write(f"Du har **{len(to_review)}** repetition(er) att göra:")
        st.divider() # En avgränsare för att göra det snyggt innan listan börjar
        
        for item in to_review:
            sid_info = f" (S. {item['sidor']})" if item.get('sidor') else ""
            
            # Använd kolumner för en mer kompakt layout på samma rad
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Texten blir mindre och tajtare när vi använder st.markdown istället för st.subheader
                datum_text = item.get('nasta_repetition', today_str)
                st.markdown(f"**{item['namn']}**{sid_info} | Steg {item['steg']} | 📅 {datum_text}")
                
            with col2:
                if st.button("✅ Klar", key=f"success_{item['id']}", use_container_width=True):
                    item["steg"] = min(item["steg"] + 1, 5)
                    item["nasta_repetition"] = str(calculate_next_date(item["steg"]))
                    save_data(data)
                    st.rerun()
            with col3:
                if st.button("❌ Öva", key=f"fail_{item['id']}", use_container_width=True):
                    item["steg"] = 1
                    item["nasta_repetition"] = today_str
                    save_data(data)
                    st.rerun()
            
            # Tunn linje för att skilja raderna åt i den kompakta vyn
            st.markdown("<hr style='margin: 0.2em 0; border: none; border-bottom: 1px solid #ddd;'>", unsafe_allow_html=True)

# --- FLIK 2: VISUELL ÖVERSIKT ---
with tab2:
    st.write("Här har du en komplett översikt. Du kan sortera listan och snabbt markera kapitel som repeterade.")
    
    # -- NYTT: CSS FÖR ATT GÖRA RADERNA TAJTARE --
    st.markdown("""
        <style>
        /* Tvinga knappen att bli lägre och ha mindre utfyllnad */
        div[data-testid="stButton"] button {
            padding: 0px 10px !important;
            min-height: 32px !important;
            height: 32px !important;
        }
        /* Ta bort Streamlits inbyggda marginal under knappen */
        div[data-testid="stButton"] {
            margin-bottom: -15px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # --------------------------------------------
    
    # 1. Sammanställ all data för tabellen (Behåll din befintliga kod här)
    table_data = []
    # ... resten av koden är densamma ...
        
# --- FLIK 3: HANTERA KAPITEL ---
with tab3:
    if not data:
        st.info("Inga kapitel tillagda ännu.")
    else:
        sorted_data = sorted(data, key=lambda x: x['namn'])
        
        for i, item in enumerate(sorted_data):
            sid_info = f" (Sida: {item['sidor']})" if item.get('sidor') else ""
            with st.expander(f"{item['namn']}{sid_info} - Steg {item['steg']}"):
                
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
                    st.rerun()
                
                st.write(f"**Nästa repetition:** {item['nasta_repetition']}")
                
                if st.button("🗑️ Ta bort kapitel", key=f"delete_{item['id']}"):
                    data = [d for d in data if d['id'] != item['id']]
                    save_data(data)
                    st.rerun()

# --- FLIK 4: LÄGG TILL NYTT ---
with tab4:    
    add_mode = st.radio("Välj metod för att lägga till:", ["Enskilt kapitel", "Lägg till flera kapitel (Bulk)"])
    st.divider()
    
    if add_mode == "Enskilt kapitel":
        val_namn = st.selectbox("Välj Surah från listan", SURAH_LISTA)
        eget_namn = st.text_input("Eller skriv eget namn (t.ex. Juz 30)")
        slutgiltigt_namn = eget_namn if eget_namn else val_namn
        
        ange_sidor = st.checkbox("Ange specifika sidor")
        sido_text = ""
        
        if ange_sidor:
            col_s1, col_s2 = st.columns(2)
            sida_start = col_s1.number_input("Från sida", min_value=1, value=1, step=1)
            sida_slut = col_s2.number_input("Till sida", min_value=1, value=sida_start, step=1)
            sido_text = f"{int(sida_start)}-{int(sida_slut)}" if sida_start != sida_slut else f"{int(sida_start)}"

        vald_steg = st.select_slider("Välj start-steg", options=[1, 2, 3, 4, 5], value=1, key="steg_enskild")

        if st.button("Spara kapitel"):
            if slutgiltigt_namn:
                nasta_rep = str(datetime.date.today()) if vald_steg == 1 else str(calculate_next_date(vald_steg))
                
                new_item = {
                    "id": str(uuid.uuid4()),
                    "namn": slutgiltigt_namn,
                    "sidor": sido_text,
                    "steg": vald_steg,
                    "nasta_repetition": nasta_rep
                }
                data.append(new_item)
                save_data(data)
                st.success(f"Lade till {slutgiltigt_namn} på steg {vald_steg}!")
                st.rerun()

    else:
        st.write("Välj ett intervall av Suror att lägga till samtidigt.")
        col_b1, col_b2 = st.columns(2)
        start_surah = col_b1.selectbox("Från Surah", SURAH_LISTA)
        slut_surah = col_b2.selectbox("Till Surah", SURAH_LISTA)
        
        vald_steg_bulk = st.select_slider("Välj start-steg för alla valda kapitel", options=[1, 2, 3, 4, 5], value=1, key="steg_bulk")
        
        if st.button("Spara markerade kapitel"):
            start_idx = SURAH_LISTA.index(start_surah)
            slut_idx = SURAH_LISTA.index(slut_surah)
            
            if start_idx > slut_idx:
                st.error("Start-surah måste komma före eller vara samma som Till-surah!")
            else:
                added_count = 0
                nasta_rep = str(datetime.date.today()) if vald_steg_bulk == 1 else str(calculate_next_date(vald_steg_bulk))
                
                for i in range(start_idx, slut_idx + 1):
                    surah_namn = SURAH_LISTA[i]
                    # Kontrollera så vi inte lägger till dubbletter
                    if not any(d['namn'] == surah_namn for d in data):
                        new_item = {
                            "id": str(uuid.uuid4()),
                            "namn": surah_namn,
                            "sidor": "", 
                            "steg": vald_steg_bulk,
                            "nasta_repetition": nasta_rep
                        }
                        data.append(new_item)
                        added_count += 1
                
                save_data(data)
                st.success(f"Lade till {added_count} nya kapitel på steg {vald_steg_bulk}!")
                st.rerun()
