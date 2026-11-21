import streamlit as st
from google import genai
from google.genai import types

# Konfigurasi Halaman Mobile-First
st.set_page_config(page_title="HistoriBot AI", page_icon="🇮🇩", layout="centered")

# Inisialisasi Klien Gemini API dari Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Basis Pengetahuan & Guardrail Sejarah Pergerakan Nasional (1908-1945)
SYSTEM_INSTRUCTION = """
Kamu adalah HistoriBot AI, asisten belajar Sejarah Pergerakan Nasional Indonesia (1908-1945) untuk murid SMA Fase F.
Aturan ketat:
1. Jawab HANYA seputar Sejarah Pergerakan Nasional Indonesia (Budi Utomo 1908, Sarekat Islam, Indische Partij, Sumpah Pemuda 1928, Pendudukan Jepang, hingga Proklamasi 1945).
2. Jika murid bertanya di luar topik sejarah Indonesia, tolak dengan sopan dan arahkan kembali ke materi.
3. Gunakan bahasa Indonesia yang ramah, edukatif, dan mudah dipahami murid SMA.
"""

st.title("🇮🇩 HistoriBot AI")
st.caption("Asisten Interaktif Sejarah Pergerakan Nasional (1908–1945)")

menu = st.sidebar.radio("Pilih Menu Belajar:", [
    "1. Peta Kronologi (1908–1945)",
    "2. Tanya-Jawab AI",
    "3. Roleplay Tokoh Sejarah",
    "4. Kuis Singkat HOTS"
])

# Simpan riwayat chat agar tidak hilang saat pindah menu
if "messages" not in st.session_state:
    st.session_state.messages = []

if menu == "1. Peta Kronologi (1908–1945)":
    st.subheader("Garis Waktu Pergerakan Nasional")
    peristiwa = st.selectbox("Pilih Tahun / Peristiwa Penting:", [
        "1908 - Berdirinya Budi Utomo",
        "1912 - Sarekat Islam & Indische Partij",
        "1928 - Kongres Pemuda II & Sumpah Pemuda",
        "1942–1945 - Masa Pendudukan Jepang & BPUPKI",
        "17 Agustus 1945 - Proklamasi Kemerdekaan"
    ])
    if st.button("Jelaskan Peristiwa Ini"):
        with st.spinner("HistoriBot sedang menyusun penjelasan..."):
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Jelaskan latar belakang, tokoh utama, dan dampak dari peristiwa: {peristiwa}",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
            )
            st.markdown(res.text)

elif menu == "2. Tanya-Jawab AI":
    st.subheader("Ruang Diskusi Sejarah")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tanyakan materi Pergerakan Nasional..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mencari referensi sejarah..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})

elif menu == "3. Roleplay Tokoh Sejarah":
    st.subheader("Simulasi Wawancara Tokoh")
    tokoh = st.radio("Pilih Tokoh yang Ingin Diajak Bicara:", ["Ir. Soekarno (Bung Karno)", "Mohammad Yamin"], horizontal=True)
    
    persona = f"Berperanlah secara penuh sebagai {tokoh} pada era perjuangan kemerdekaan Indonesia (1928-1945). Gunakan gaya bahasa berapi-api dan sudut pandang masa perjuangan tersebut. Jangan keluar dari karakter."
    
    tanya_tokoh = st.text_input(f"Ajukan pertanyaan kepada {tokoh}:")
    if st.button("Kirim Pertanyaan") and tanya_tokoh:
        with st.spinner(f"{tokoh} sedang menjawab..."):
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=tanya_tokoh,
                config=types.GenerateContentConfig(system_instruction=persona)
            )
            st.info(res.text)

elif menu == "4. Kuis Singkat HOTS":
    st.subheader("Uji Pemahaman Analisis")
    nama = st.text_input("Nama Murid:")
    jawaban = st.text_area("Soal HOTS: Mengapa strategi perjuangan setelah tahun 1908 berubah dari perlawanan fisik kedaerahan menjadi organisasi modern bersifat nasional?")
    if st.button("Kirim & Nilai Jawaban") and nama and jawaban:
        with st.spinner("Menilai jawaban..."):
            penilaian = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Nilai jawaban murid bernama {nama} untuk soal: 'Mengapa strategi perjuangan setelah 1908 berubah menjadi organisasi modern nasional?'. Jawaban murid: '{jawaban}'. Berikan skor (0-100) dan umpan balik singkat.",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
            )
            st.success(penilaian.text)
