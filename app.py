import streamlit as st
import time
import random
from io import BytesIO

# --- 1. 核心相容性修復 ---
def safe_rerun():
    """自動判斷並執行重整"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
            st.stop()

def safe_play_audio(text):
    """語音播放安全模式"""
    try:
        from gtts import gTTS
        # 使用印尼語 (id) 發音
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.caption(f"🔇 (語音生成暫時無法使用)")

# --- 0. 系統配置 ---
st.set_page_config(page_title="Unit 26: O Demak", page_icon="💃", layout="centered")

# --- CSS 美化 (活力洋紅色調) ---
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .source-tag { font-size: 12px; color: #aaa; text-align: right; font-style: italic; }
    
    /* 單字卡 */
    .word-card {
        background: linear-gradient(135deg, #F3E5F5 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #AB47BC;
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #7B1FA2; }
    .chinese-text { font-size: 16px; color: #7f8c8d; }
    
    /* 句子框 */
    .sentence-box {
        background-color: #F3E5F5;
        border-left: 5px solid #CE93D8;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
    }

    /* 按鈕 */
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #E1BEE7; color: #4A148C; border: 2px solid #AB47BC; padding: 12px;
    }
    .stButton>button:hover { background-color: #BA68C8; border-color: #7B1FA2; }
    .stProgress > div > div > div > div { background-color: #AB47BC; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料庫 (Unit 26: 14個單字 - 句子提取核心詞) ---
vocab_data = [
    {"amis": "Misakero", "chi": "跳舞", "icon": "💃", "source": "Row 344"},
    {"amis": "Tayni", "chi": "來", "icon": "👉", "source": "Row 250"},
    {"amis": "Mi'araw", "chi": "看 / 注視", "icon": "👀", "source": "Row 725"},
    {"amis": "Sowal", "chi": "語言 / 話語", "icon": "💬", "source": "Row 402"},
    {"amis": "Lifon", "chi": "工資 / 薪水", "icon": "💰", "source": "Row 517"},
    {"amis": "Mingata", "chi": "靠近 / 接近", "icon": "🚶", "source": "Row 482"},
    {"amis": "Radiw", "chi": "歌 / 歌曲", "icon": "🎵", "source": "Row 212"},
    {"amis": "Demak", "chi": "事情 / 事件", "icon": "📝", "source": "Row 238"},
    {"amis": "Fafahi", "chi": "太太 / 妻子", "icon": "👩", "source": "Row 212"},
    {"amis": "Kaying", "chi": "小姐", "icon": "👧", "source": "Row 9"},
    {"amis": "Tamdaw", "chi": "人", "icon": "🧑", "source": "Row 222"},
    {"amis": "Kapot", "chi": "同伴 / 隊友", "icon": "🤝", "source": "Row 19"},
    {"amis": "Fa'elohay", "chi": "新的", "icon": "🆕", "source": "Row 352"},
    {"amis": "'Orip", "chi": "生活 / 生命", "icon": "🌱", "source": "Row 541"},
]

# --- 句子庫 (7句: 嚴格源自 CSV 並移除連字號) ---
sentences = [
    {"amis": "O raromadiw ato misakero kita i Taypak.", "chi": "我們將在台北唱歌和跳舞。", "icon": "💃", "source": "Row 344"},
    {"amis": "Hacowa ci Kaiming a tayni?", "chi": "愷銘何時來？", "icon": "👉", "source": "Row 707"},
    {"amis": "Kicowaen no mita a mi'araw?", "chi": "大家要從哪裡看？", "icon": "👀", "source": "Row 725"},
    {"amis": "Oni ko hatatodong no lifon.", "chi": "以此做為工錢的回報。", "icon": "💰", "source": "Row 517"},
    {"amis": "Mingataay ciira takowanan a romakat.", "chi": "他正往我這邊走來了。", "icon": "🚶", "source": "Row 482"},
    {"amis": "Fa'elohay koni a radiw a tengilen.", "chi": "這首歌聽起來是新的。", "icon": "🎵", "source": "Row 352"},
    {"amis": "O nia demak 'i, caay kafana' kako.", "chi": "這件事呢，我不知道。", "icon": "🤷", "source": "Row 238"},
]

# --- 3. 隨機題庫 (Synced) ---
raw_quiz_pool = [
    {
        "q": "O raromadiw ato misakero kita...",
        "audio": "O raromadiw ato misakero kita",
        "options": ["我們將唱歌和跳舞", "我們將吃飯和喝酒", "我們將睡覺和休息"],
        "ans": "我們將唱歌和跳舞",
        "hint": "Misakero (跳舞) (Row 344)"
    },
    {
        "q": "Hacowa ci Kaiming a tayni?",
        "audio": "Hacowa ci Kaiming a tayni",
        "options": ["愷銘何時來？", "愷銘何時去？", "愷銘何時回家？"],
        "ans": "愷銘何時來？",
        "hint": "Tayni (來) (Row 707)"
    },
    {
        "q": "單字測驗：Lifon",
        "audio": "Lifon",
        "options": ["工資/薪水", "禮物", "食物"],
        "ans": "工資/薪水",
        "hint": "工作的報酬 (Row 517)"
    },
    {
        "q": "單字測驗：Fa'elohay",
        "audio": "Fa'elohay",
        "options": ["新的", "舊的", "壞的"],
        "ans": "新的",
        "hint": "Row 352: Fa'elohay koni a radiw (這首歌是新的)"
    },
    {
        "q": "Mingataay ciira takowanan a romakat.",
        "audio": "Mingataay ciira takowanan a romakat",
        "options": ["他正往我這邊走來(靠近)", "他正離開我", "他正看著我"],
        "ans": "他正往我這邊走來(靠近)",
        "hint": "Mingata (靠近) (Row 482)"
    },
    {
        "q": "單字測驗：Kapot",
        "audio": "Kapot",
        "options": ["同伴", "敵人", "老師"],
        "ans": "同伴",
        "hint": "一起做事的夥伴 (Row 19)"
    },
    {
        "q": "單字測驗：Demak",
        "audio": "Demak",
        "options": ["事情/事件", "時間", "地點"],
        "ans": "事情/事件",
        "hint": "Row 238: O nia demak (這件事)"
    },
    {
        "q": "單字測驗：Sowal",
        "audio": "Sowal",
        "options": ["語言/話語", "歌聲", "哭聲"],
        "ans": "語言/話語",
        "hint": "Sowal no Pangcah (阿美語) (Row 402)"
    }
]

# --- 4. 狀態初始化 (洗牌邏輯) ---
if 'init' not in st.session_state:
    st.session_state.score = 0
    st.session_state.current_q_idx = 0
    st.session_state.quiz_id = str(random.randint(1000, 9999))
    
    # 抽題與洗牌
    selected_questions = random.sample(raw_quiz_pool, 3)
    final_questions = []
    for q in selected_questions:
        q_copy = q.copy()
        shuffled_opts = random.sample(q['options'], len(q['options']))
        q_copy['shuffled_options'] = shuffled_opts
        final_questions.append(q_copy)
        
    st.session_state.quiz_questions = final_questions
    st.session_state.init = True

# --- 5. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #7B1FA2;'>Unit 26: O Demak</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>行為與事件 (Actions & Events)</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📚 詞彙與句型", "🎲 隨機挑戰"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字 (從句子提取)")
    col1, col2 = st.columns(2)
    for i, word in enumerate(vocab_data):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="word-card">
                <div class="emoji-icon">{word['icon']}</div>
                <div class="amis-text">{word['amis']}</div>
                <div class="chinese-text">{word['chi']}</div>
                <div class="source-tag">src: {word['source']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 聽發音", key=f"btn_vocab_{i}"):
                safe_play_audio(word['amis'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型 (Data-Driven)")
    for i, s in enumerate(sentences):
        st.markdown(f"""
        <div class="sentence-box">
            <div style="font-size: 20px; font-weight: bold; color: #7B1FA2;">{s['icon']} {s['amis']}</div>
            <div style="font-size: 16px; color: #555; margin-top: 5px;">{s['chi']}</div>
            <div class="source-tag">src: {s['source']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 播放句型", key=f"btn_sent_{i}"):
            safe_play_audio(s['amis'])

# === Tab 2: 隨機挑戰模式 ===
with tab2:
    st.markdown("### 🎲 隨機評量")
    
    if st.session_state.current_q_idx < len(st.session_state.quiz_questions):
        q_data = st.session_state.quiz_questions[st.session_state.current_q_idx]
        
        st.progress((st.session_state.current_q_idx) / 3)
        st.markdown(f"**Question {st.session_state.current_q_idx + 1} / 3**")
        
        st.markdown(f"### {q_data['q']}")
        if q_data['audio']:
            if st.button("🎧 播放題目音檔", key=f"btn_audio_{st.session_state.current_q_idx}"):
                safe_play_audio(q_data['audio'])
        
        # 使用洗牌後的選項
        unique_key = f"q_{st.session_state.quiz_id}_{st.session_state.current_q_idx}"
        user_choice = st.radio("請選擇正確答案：", q_data['shuffled_options'], key=unique_key)
        
        if st.button("送出答案", key=f"btn_submit_{st.session_state.current_q_idx}"):
            if user_choice == q_data['ans']:
                st.balloons()
                st.success("🎉 答對了！")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q_idx += 1
                safe_rerun()
            else:
                st.error(f"不對喔！提示：{q_data['hint']}")
                
    else:
        st.progress(1.0)
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #E1BEE7; border-radius: 20px; margin-top: 20px;'>
            <h1 style='color: #7B1FA2;'>🏆 挑戰成功！</h1>
            <h3 style='color: #333;'>本次得分：{st.session_state.score}</h3>
            <p>你已經學會描述各種事件了！</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再來一局 (重新抽題)", key="btn_restart"):
            st.session_state.score = 0
            st.session_state.current_q_idx = 0
            st.session_state.quiz_id = str(random.randint(1000, 9999))
            
            new_questions = random.sample(raw_quiz_pool, 3)
            final_qs = []
            for q in new_questions:
                q_copy = q.copy()
                shuffled_opts = random.sample(q['options'], len(q['options']))
                q_copy['shuffled_options'] = shuffled_opts
                final_qs.append(q_copy)
            
            st.session_state.quiz_questions = final_qs
            safe_rerun()
