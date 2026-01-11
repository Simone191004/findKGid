import streamlit as st
import requests
import base64
import re
from urllib.parse import urlparse, parse_qs

import streamlit as st
import requests
import base64
import re
from urllib.parse import urlparse, parse_qs

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="KG Explorer Pro", 
    page_icon="🕸️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    try:
        raw = b'\x0a' + bytes([len(mid)]) + mid.encode('utf-8')
        return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')
    except: return ""

def validate_mid(mid):
    pattern = r'^/(m|g)/[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, mid))

def extract_mid_from_share_url(share_url):
    try:
        response = requests.get(share_url, allow_redirects=True, timeout=10)
        final_url = response.url
        parsed = urlparse(final_url)
        params = parse_qs(parsed.query)
        
        if 'kgmid' in params:
            return params['kgmid'][0], final_url, None
        
        match = re.search(r'/(m|g)/[a-zA-Z0-9_]+', final_url)
        if match:
            return match.group(0), final_url, None
        
        return None, final_url, "MID non trovato nell'URL finale."
    except Exception as e:
        return None, None, f"Errore: {str(e)}"

def generate_data(mid):
    mid_clean = mid.replace("kg:", "")
    cpid = encode_to_profile_id(mid_clean)
    urls = {
        'search': f"https://www.google.com/search?kgmid={mid_clean}",
        'profile': f"https://profile.google.com/cp/{cpid}",
        'knowledge_graph': f"https://developers.google.com/knowledge-graph/reference/rest/v1/entities/search?ids={mid_clean}"
    }
    return mid_clean, cpid, urls

# --- UI HELPER ---
def display_results(mid_clean, cpid, urls):
    st.divider()
    st.subheader("📊 Risultati Analisi")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Machine ID (MID)**")
        st.code(mid_clean, language="text")
    with col2:
        st.info("**Profile ID (CPID)**")
        st.code(cpid, language="text")

    st.markdown("### 🔗 Collegamenti Rapidi")
    c1, c2, c3 = st.columns(3)
    c1.link_button("🌐 Google Search", urls['search'], use_container_width=True)
    c2.link_button("👤 Google Profile", urls['profile'], use_container_width=True)
    c3.link_button("🛠️ API Explorer", urls['knowledge_graph'], use_container_width=True)

    with st.expander("📋 Copia Rapida Link"):
        st.text_input("URL Search", urls['search'])
        st.text_input("URL Profile", urls['profile'])

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings ⚙️")
    input_method = st.radio(
        "Scegli metodo di input:",
        ["📝 MID Manuale", "🔗 URL Condivisione"]
    )
    st.divider()
    st.markdown("""
    **Legenda:**
    - `/m/`: Topic generico
    - `/g/`: Topic specifico Google
    """)

# --- MAIN CONTENT ---
st.title("🔍 Knowledge Graph Explorer")
st.caption("Estrai ID e genera link ai profili Google in un clic.")

if input_method == "📝 MID Manuale":
    st.markdown("### Inserimento Manuale")
    mid_input = st.text_input("Inserisci il MID", placeholder="/m/0jcx", help="Es. Leonardo da Vinci: /m/0jcx")
    
    if st.button("🚀 Genera Analisi", type="primary"):
        if validate_mid(mid_input):
            mid_clean, cpid, urls = generate_data(mid_input)
            display_results(mid_clean, cpid, urls)
        else:
            st.error("Formato MID non valido. Assicurati che inizi con /m/ o /g/")

else:
    st.markdown("### Estrazione da URL")
    url_input = st.text_input("Incolla URL di condivisione", placeholder="https://share.google/...")
    
    if st.button("🔍 Estrai e Analizza", type="primary"):
        if "share.google" in url_input or "search.app" in url_input:
            with st.spinner("Interrogando i server Google..."):
                mid, final_url, error = extract_mid_from_share_url(url_input)
                if mid:
                    mid_clean, cpid, urls = generate_data(mid)
                    st.success(f"MID trovato con successo!")
                    display_results(mid_clean, cpid, urls)
                else:
                    st.error(error)
        else:
            st.warning("Inserisci un URL valido (share.google o search.app)")

# --- FOOTER ---
st.divider()
st.markdown(
    "<center><small>KG Explorer Pro | Strumento avanzato per l'analisi del Knowledge Graph</small></center>", 
    unsafe_allow_html=True
)
def encode_to_profile_id(mid):
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
        
        if 'kgmid' in params:
            mid = params['kgmid'][0]
            return mid, final_url, None
        
        match = re.search(r'/(m|g)/[a-zA-Z0-9_]+', final_url)
        if match:
            return match.group(0), final_url, None
        
        return None, final_url, "MID non trovato nell'URL finale"
        
    except requests.exceptions.RequestException as e:
        return None, None, f"Errore nella richiesta: {str(e)}"
    except Exception as e:
        return None, None, f"Errore: {str(e)}"

def generate_urls_from_mid(mid):
    """Genera le URL necessarie dato un MID"""
    mid_clean = mid.replace("kg:", "")
    cpid = encode_to_profile_id(mid_clean)
    
    urls = {
        'google_search': f"https://www.google.com/search?kgmid={mid_clean}",
        'profile': f"https://profile.google.com/cp/{cpid}"
    }
    
    return mid_clean, cpid, urls

# Header
st.title("Knowledge Graph Explorer")

st.markdown("<br>", unsafe_allow_html=True)

# Selezione metodo
input_method = st.radio(
    "Seleziona il metodo di input:",
    options=["MID Manuale", "URL di Condivisione"],
    horizontal=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ========== METODO 1: MID MANUALE ==========
if input_method == "MID Manuale":
    
    col_input, col_help = st.columns([3, 1])
    
    with col_input:
        mid_input = st.text_input(
            "Knowledge Graph ID",
            placeholder="/m/0jcx",
            help="Formato: /m/xxxxx o /g/xxxxx",
            label_visibility="visible"
        )
    
    with col_help:
        with st.expander("Info"):
            st.markdown("""
            **Come trovare un MID:**
            
            1. Cerca un'entità su Google
            2. Nel Knowledge Panel, ispeziona l'elemento
            3. Cerca l'attributo `data-kgmid`
            
            **Formati validi:**
            - `/m/0jcx` (Machine ID)
            - `/g/11b7t1brqf` (Google ID)
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Genera URL", type="primary", use_container_width=False):
        if not mid_input:
            st.warning("Inserisci un MID prima di procedere")
        elif not validate_mid(mid_input):
            st.error("Formato MID non valido. Deve essere /m/xxxxx o /g/xxxxx")
        else:
            mid_clean, cpid, urls = generate_urls_from_mid(mid_input)
            
            st.success(f"URL generate per: {mid_clean}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Informazioni calcolate
            with st.container(border=True):
                st.markdown("### Informazioni Calcolate")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**MID**")
                    st.code(mid_clean, language="text")
                
                with col2:
                    st.markdown("**Profile ID**")
                    st.code(cpid, language="text")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Link generati
            st.markdown("### Link Generati")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.link_button(
                    "Google Search",
                    urls['google_search'],
                    use_container_width=True
                )
            
            with col_b:
                st.link_button(
                    "Google Profile",
                    urls['profile'],
                    use_container_width=True
                )
            
            # Copia URL
            with st.expander("Copia le URL"):
                st.text_input("Google Search", urls['google_search'], disabled=True, label_visibility="visible")
                st.text_input("Google Profile", urls['profile'], disabled=True, label_visibility="visible")

# ========== METODO 2: URL DI CONDIVISIONE ==========
else:
    
    col_input, col_help = st.columns([3, 1])
    
    with col_input:
        share_url_input = st.text_input(
            "URL di Condivisione Google",
            placeholder="https://share.google/... o https://search.app/...",
            help="Incolla l'URL breve di condivisione",
            label_visibility="visible"
        )
    
    with col_help:
        with st.expander("Info"):
            st.markdown("""
            **URL supportati:**
            
            - `https://share.google/xxxxx`
            - `https://search.app/xxxxx`
            
            Entrambi reindirizzano all'entità del Knowledge Graph.
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Estrai MID", type="primary", use_container_width=False):
        if not share_url_input:
            st.warning("Inserisci un URL di condivisione prima di procedere")
        elif not (share_url_input.startswith("https://share.google/") or share_url_input.startswith("https://search.app/")):
            st.error("L'URL deve iniziare con https://share.google/ o https://search.app/")
        else:
            with st.spinner("Estrazione MID in corso..."):
                mid, final_url, error = extract_mid_from_share_url(share_url_input)
                
                if error:
                    st.error(error)
                elif mid:
                    st.success(f"MID estratto: {mid}")
                    
                    mid_clean, cpid, urls = generate_urls_from_mid(mid)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Informazioni estratte
                    with st.container(border=True):
                        st.markdown("### Informazioni Estratte")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**MID**")
                            st.code(mid_clean, language="text")
                        
                        with col2:
                            st.markdown("**Profile ID**")
                            st.code(cpid, language="text")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Link generati
                    st.markdown("### Link Generati")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.link_button(
                            "Google Search",
                            urls['google_search'],
                            use_container_width=True
                        )
                    
                    with col_b:
                        st.link_button(
                            "Google Profile",
                            urls['profile'],
                            use_container_width=True
                        )
                    
                    # Copia URL
                    with st.expander("Copia le URL"):
                        st.text_input("URL Originale", share_url_input, disabled=True, label_visibility="visible")
                        st.text_input("MID Estratto", mid_clean, disabled=True, label_visibility="visible")
                        st.text_input("Google Search", urls['google_search'], disabled=True, label_visibility="visible")
                        st.text_input("Google Profile", urls['profile'], disabled=True, label_visibility="visible")
                else:
                    st.error("Impossibile estrarre il MID dall'URL fornito")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<p class="caption">Knowledge Graph Explorer - Estrazione e generazione URL da MID</p>', unsafe_allow_html=True)