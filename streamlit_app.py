import streamlit as st
import requests
import base64
import re
from urllib.parse import urlparse, parse_qs
import hashlib

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="KG Explorer Pro", 
    page_icon="🕸️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DI AUTENTICAZIONE ---
def check_credentials():
    """Verifica username e password usando i secrets di Streamlit"""
    
    def credentials_entered():
        """Callback quando vengono inserite le credenziali"""
        # Verifica username
        entered_username = st.session_state["username"]
        entered_password = st.session_state["password"]
        
        # Hash della password inserita
        hashed_password = hashlib.sha256(entered_password.encode()).hexdigest()
        
        # Confronta con le credenziali nei secrets
        if (entered_username == st.secrets["app_username"] and 
            hashed_password == st.secrets["app_password_hash"]):
            st.session_state["authenticated"] = True
            # Rimuove le credenziali dalla sessione per sicurezza
            del st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    # Se non è ancora stato verificato lo stato di login
    if "authenticated" not in st.session_state:
        # Mostra form di login
        st.markdown("### 🔐 Accesso Richiesto")
        st.text_input(
            "Nome Utente",
            key="username",
            placeholder="Inserisci il nome utente"
        )
        st.text_input(
            "Password",
            type="password",
            key="password",
            placeholder="Inserisci la password"
        )
        st.button("Login", on_click=credentials_entered, type="primary")
        st.markdown("<small>Inserisci le credenziali per accedere all'applicazione</small>", unsafe_allow_html=True)
        return False
    
    # Se le credenziali sono errate
    elif not st.session_state["authenticated"]:
        st.markdown("### 🔐 Accesso Richiesto")
        st.text_input(
            "Nome Utente",
            key="username",
            placeholder="Inserisci il nome utente"
        )
        st.text_input(
            "Password",
            type="password",
            key="password",
            placeholder="Inserisci la password"
        )
        st.button("Login", on_click=credentials_entered, type="primary")
        st.error("😕 Credenziali errate, riprova")
        return False
    
    # Credenziali corrette
    else:
        return True

# Verifica autenticazione
if not check_credentials():
    st.stop()

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    code { color: #e83e8c !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONI LOGICHE ---
def encode_to_profile_id(mid):
    """Converte un MID in un Profile ID"""
    try:
        raw = b'\x0a' + bytes([len(mid)]) + mid.encode('utf-8')
        return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')
    except: 
        return ""

def validate_mid(mid):
    """Valida il formato del MID (deve iniziare con /m/ o /g/)"""
    pattern = r'^/(m|g)/[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, mid))

def extract_mid_from_share_url(share_url):
    """
    Estrae il MID da un URL di condivisione Google (share.google o search.app)
    seguendo i redirect e analizzando l'URL finale
    """
    try:
        response = requests.get(share_url, allow_redirects=True, timeout=10)
        final_url = response.url
        
        parsed = urlparse(final_url)
        params = parse_qs(parsed.query)
        
        # Cerca il parametro kgmid
        if 'kgmid' in params:
            return params['kgmid'][0], final_url, None
        
        # Cerca il pattern /m/ o /g/ nell'URL
        match = re.search(r'/(m|g)/[a-zA-Z0-9_]+', final_url)
        if match:
            return match.group(0), final_url, None
        
        return None, final_url, "MID non trovato nell'URL finale"
        
    except requests.exceptions.RequestException as e:
        return None, None, f"Errore nella richiesta: {str(e)}"
    except Exception as e:
        return None, None, f"Errore: {str(e)}"

def generate_data(mid):
    """Genera tutte le informazioni necessarie dato un MID"""
    mid_clean = mid.replace("kg:", "")
    cpid = encode_to_profile_id(mid_clean)
    
    urls = {
        'search': f"https://www.google.com/search?kgmid={mid_clean}",
        'profile': f"https://profile.google.com/cp/{cpid}"
    }
    
    return mid_clean, cpid, urls

def display_results(mid_clean, cpid, urls):
    """Mostra i risultati dell'analisi"""
    st.divider()
    st.subheader("📊 Risultati Analisi")
    
    # Informazioni estratte
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Machine ID (MID)**")
        st.code(mid_clean, language="text")
    with col2:
        st.info("**Profile ID (CPID)**")
        st.code(cpid, language="text")

    st.markdown("### 🔗 Collegamenti Rapidi")
    c1, c2 = st.columns(2)
    c1.link_button("🌐 Google Search", urls['search'], use_container_width=True)
    c2.link_button("👤 Google Profile", urls['profile'], use_container_width=True)

    # Sezione per copiare i link
    with st.expander("📋 Copia Rapida Link"):
        st.text_input("URL Search", urls['search'], disabled=True)
        st.text_input("URL Profile", urls['profile'], disabled=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Impostazioni")
    
    input_method = st.radio(
        "Scegli metodo di input:",
        ["🔗 URL Condivisione", "📝 MID Manuale"],
        label_visibility="visible"
    )
    
    st.divider()
    
    st.markdown("### 📖 Guida")
    st.markdown("""
    **Legenda formati MID:**
    - `/m/`: Topic generico
    - `/g/`: Topic specifico Google
    
    **Come trovare un MID:**
    1. Cerca un'entità su Google
    2. Ispeziona il Knowledge Panel
    3. Cerca l'attributo `data-kgmid`
    
    **URL supportati:**
    - `https://share.google/xxxxx`
    - `https://search.app/xxxxx`
    """)
    
    st.divider()
    
    # Pulsante logout
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# --- MAIN CONTENT ---
st.title("🔍 Knowledge Graph Explorer")
st.caption("Estrai ID e genera link ai profili Google in un clic.")

st.markdown("<br>", unsafe_allow_html=True)

# ========== METODO 1: URL DI CONDIVISIONE ==========
if input_method == "🔗 URL Condivisione":
    st.markdown("### Estrazione da URL di Condivisione")
    
    url_input = st.text_input(
        "URL di Condivisione Google",
        placeholder="https://share.google/... o https://search.app/...",
        help="Incolla l'URL breve di condivisione Google",
        label_visibility="visible"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔍 Estrai e Analizza", type="primary"):
        if not url_input:
            st.warning("⚠️ Inserisci un URL di condivisione prima di procedere")
        elif not ("share.google" in url_input or "search.app" in url_input):
            st.error("❌ Inserisci un URL valido (share.google o search.app)")
        else:
            with st.spinner("🔄 Interrogando i server Google..."):
                mid, final_url, error = extract_mid_from_share_url(url_input)
                
                if error:
                    st.error(f"❌ {error}")
                elif mid:
                    st.success(f"✅ MID trovato con successo: {mid}")
                    mid_clean, cpid, urls = generate_data(mid)
                    display_results(mid_clean, cpid, urls)
                else:
                    st.error("❌ Impossibile estrarre il MID dall'URL fornito")

# ========== METODO 2: MID MANUALE ==========
else:
    st.markdown("### Inserimento Manuale MID")
    
    mid_input = st.text_input(
        "Knowledge Graph ID",
        placeholder="/m/0jcx (es. Leonardo da Vinci)",
        help="Inserisci un MID valido nel formato /m/xxxxx o /g/xxxxx",
        label_visibility="visible"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Genera Analisi", type="primary"):
        if not mid_input:
            st.warning("⚠️ Inserisci un MID prima di procedere")
        elif not validate_mid(mid_input):
            st.error("❌ Formato MID non valido. Deve essere /m/xxxxx o /g/xxxxx")
        else:
            mid_clean, cpid, urls = generate_data(mid_input)
            display_results(mid_clean, cpid, urls)

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown(
    "<center><small>🕸️ KG Explorer Pro | Strumento avanzato per l'analisi del Knowledge Graph</small></center>", 
    unsafe_allow_html=True
)
