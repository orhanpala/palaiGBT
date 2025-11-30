import streamlit as st
# *** DEĞİŞİKLİK BURADA ***
import google.genai as genai 
# Bu import, requirements.txt'deki 'google-genai-sdk' paketine karşılık gelir.
import os 

# --- YAPILANDIRMA VE HATA KONTROLÜ ---
MODEL_ADI = "gemini-2.5-pro"

try:
    # 1. st.secrets'tan anahtarı çekin
    API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # 2. Anahtarı yapılandırın (Sadece bir kez!)
    genai.configure(api_key=API_KEY)

except KeyError:
    # Anahtar çekilemezse (Streamlit Secrets'a eklenmemişse)
    st.error("🚨 HATA: API Anahtarı bulunamadı!")
    st.warning("Lütfen Streamlit Cloud'daki 'Secrets' ayarına 'GEMINI_API_KEY' adıyla anahtarınızı eklediğinizden emin olun.")
    st.stop() # Uygulamayı durdur, böylece aşağısı çalışmaz
except Exception as e:
    st.error(f"Genel Yapılandırma Hatası: {e}")
    st.stop()

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="PALAİ",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TASARIM (CSS) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
    }
    
    /* Input Alanı */
    .centered-input .stTextInput > div > div > input {
        background-color: #1E1F20;
        color: white;
        border-radius: 24px;
        padding: 12px 20px;
        border: 1px solid #3c4043;
        font-size: 18px;
    }
    
    input { caret-color: #4285F4; }

    /* Başlık Stili */
    .big-title {
        text-align: center;
        font-size: 7em !important;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.5em;
        color: #9aa0a6;
        font-weight: 300;
        margin-top: -10px;
        margin-bottom: 40px;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI BAĞLANTISI ---
def get_model():
    try:
        # Chat geçmişi kullanmıyorsanız, her seferinde yeni bir model oluşturmak yeterlidir.
        return genai.GenerativeModel(MODEL_ADI)
    except Exception as e:
        # Bu hata genelde API key veya model adı yanlışsa oluşur.
        st.error(f"Model Yükleme Hatası: {e}")
        return None

# Modeli bir kere yükle
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = get_model()
    
model = st.session_state.ai_model

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- YARDIMCI FONKSİYON: GÜVENLİ CEVAP ÜRETME ---
def stream_cevap_yazdir(prompt_input):
    if not model:
        st.error("AI modeli yüklenemedi. Lütfen API anahtarınızı kontrol edin.")
        return

    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_input)

    # Asistan cevabı (Streaming)
    with st.chat_message("assistant", avatar="✨"):
        placeholder = st.empty()
        full_response = ""
        try:
            # Yapılandırılmış model objesi ile API çağrısı
            response_stream = model.generate_content(prompt_input, stream=True)
            
            for chunk in response_stream:
                # Gelen parçada metin var mı diye kontrol et (Hata önleyici)
                if chunk.parts and chunk.text is not None:
                    text_parcasi = chunk.text
                    full_response += text_parcasi
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # API'den anlık bir hata gelirse
            if full_response:
                placeholder.markdown(full_response + "\n\n*(Cevap kesintiye uğradı: API Hatası)*")
            else:
                st.error(f"API Yanıt Hatası: {e}")

# ==========================================
#              ARAYÜZ MANTIĞI
# ==========================================

# DURUM 1: HİÇ MESAJ YOKSA (GİRİŞ EKRANI)
if len(st.session_state.messages) == 0:
    # Sayfa düzeni
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="big-title">PALAİ</div>', unsafe_allow_html=True)
    
    # Kişiselleştirme
    st.markdown(f'<div class="subtitle">Orhan Pala | Yapay Zeka Asistanı</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Baslangic input'u gönderen callback fonksiyonu
        def baslangic_submit():
            input_val = st.session_state.baslangic_input
            if input_val:
                st.session_state.temp_input = input_val

        st.text_input(
            "Ara", 
            placeholder="PALAİ'ye bir şeyler sor...", 
            key="baslangic_input", 
            label_visibility="collapsed",
            on_change=baslangic_submit
        )
        
        # Eğer input'tan değer geldiyse işlemi başlat ve sayfayı yenile
        if "temp_input" in st.session_state and st.session_state.temp_input:
            temp_text = st.session_state.temp_input
            del st.session_state.temp_input # Temizle
            stream_cevap_yazdir(temp_text)
            st.rerun()

        # Örnek öneriler butonları
        c1, c2, c3 = st.columns(3)
        
        # Kullanıcının siber güvenlik ilgisine uygun öneri
        if c1.button("🔒 Güvenlik", use_container_width=True):
            stream_cevap_yazdir("Siber güvenlikte Python'ın rolü nedir?")
            st.rerun()
        if c2.button("🐍 Python", use_container_width=True):
            stream_cevap_yazdir("Basit bir Python kodu yaz.")
            st.rerun()
        if c3.button("✨ Fikir", use_container_width=True):
            stream_cevap_yazdir("Munzur Üniversitesi'ndeki öğrenci projelerim için yaratıcı fikirler ver.")
            st.rerun()

# DURUM 2: SOHBET MODU
else:
    # Sohbet geçmişini göster
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "👤" if role == "user" else "✨"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])
            
    # Yeni Sohbet butonu (Sidebar'da)
    with st.sidebar:
        st.markdown("### PALAİ 🤖")
        if st.button("➕ Yeni Sohbet", type="primary", use_container_width=True):
            st.session_state.messages = []
            # st.session_state'te tutulan model objesini de temizle
            if 'ai_model' in st.session_state:
                del st.session_state.ai_model 
            st.rerun()
            
    # Sohbet inputu
    if prompt := st.chat_input("Sohbete devam et..."):
        stream_cevap_yazdir(prompt)
        st.rerun() # Yeni mesaj geldikten sonra tekrar yükle
