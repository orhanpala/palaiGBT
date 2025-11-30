import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="PALAİ Tanı Aracı", page_icon="🛠️")

st.header("🛠️ PALAİ Model Tanı Aracı")
st.write("Bu araç, API anahtarının hangi modellere erişebildiğini kesin olarak gösterir.")

# API Anahtarı girişi (Arayüzden gir, kodla uğraşma)
api_key_input = st.text_input("Yeni aldığın API Anahtarını buraya yapıştır:", type="password")

if st.button("Modelleri Listele"):
    if not api_key_input:
        st.warning("Lütfen önce API anahtarını kutucuğa gir.")
    else:
        try:
            # Yapılandırma
            genai.configure(api_key=api_key_input)
            
            st.info(f"Kullanılan Kütüphane Sürümü: {genai.__version__}")
            st.write("Google sunucularına bağlanılıyor...")
            
            modeller = []
            for m in genai.list_models():
                # Sadece 'generateContent' (metin üretimi) destekleyenleri filtrele
                if 'generateContent' in m.supported_generation_methods:
                    modeller.append(m.name)
            
            if modeller:
                st.success("✅ BAŞARILI! İşte kullanabileceğin tam model isimleri:")
                # Listeyi temiz bir şekilde göster
                st.code("\n".join(modeller), language="text")
                st.success("☝️ Yukarıdaki listeden bir ismi (örneğin 'models/gemini-1.5-flash') kopyala ve main.py dosyanı güncelle.")
            else:
                st.error("❌ Bağlantı kuruldu ama erişilebilir hiç model bulunamadı.")
                
        except Exception as e:
            st.error(f"❌ KRİTİK HATA: {e}")
            st.write("İpucu: Eğer 'INVALID_ARGUMENT' hatası alırsan API anahtarın yanlıştır.")