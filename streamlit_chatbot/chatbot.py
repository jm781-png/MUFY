import streamlit as st
import random
from collections import defaultdict

# Load 5-letter words from words.txt
@st.cache_data
def load_words():
    try:
        with open("streamlit_chatbot/words.txt", "r") as f:
            return [word.strip().lower() for word in f if len(word.strip()) == 5 and word.strip().isalpha()]
    except FileNotFoundError:
        st.error("❌ 'words.txt' not found. Please add a file with one 5-letter word per line.")
        return []

WORD_LIST = load_words()

# Function to get feedback on a guess
def get_feedback(guess, target):
    feedback = [('', letter) for letter in guess]
    target_chars = list(target)

    # First pass: green
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = ('🟩', guess[i])
            target_chars[i] = None

    # Second pass: yellow and white
    for i in range(5):
        if feedback[i][0] == '':
            if guess[i] in target_chars:
                idx = target_chars.index(guess[i])
                target_chars[idx] = None
                feedback[i] = ('🟨', guess[i])
            else:
                feedback[i] = ('⬜', guess[i])
    return feedback

# Update keyboard coloring
def update_keyboard_colors(key_colors, feedback):
    priority = {'🟩': 3, '🟨': 2, '⬜': 1}
    for symbol, letter in feedback:
        letter = letter.upper()
        if priority[symbol] > priority.get(key_colors.get(letter, ''), 0):
            key_colors[letter] = symbol
    return key_colors

# Keyboard layout
KEYBOARD_ROWS = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM")
]

# Initialize session state
if 'target_word' not in st.session_state:
    st.session_state.target_word = random.choice(WORD_LIST)
    st.session_state.guesses = []
    st.session_state.status = 'playing'
    st.session_state.key_colors = {}  # Tracks keyboard colors

# Title
st.title("🔠 Streamlit Wordle!!!")

# Game status
if st.session_state.status == 'won':
    st.header("🎉 You Win!")
elif st.session_state.status == 'lost':
    st.header("❌ You Lost!")
else:
    st.caption("Guess the secret 5-letter word. You have 6 tries.")

# Input box
if st.session_state.status == 'playing':
    guess_input = st.text_input("Your guess:", max_chars=5)
    guess = guess_input.lower() if guess_input else ""

    if st.button("Submit Guess"):
        if len(guess) != 5 or not guess.isalpha():
            st.warning("🚫 Please enter a valid 5-letter word.")
        elif guess not in WORD_LIST:
            st.warning("🧐 Not a valid word in the list.")
        else:
            feedback = get_feedback(guess, st.session_state.target_word)
            st.session_state.guesses.append((guess, feedback))
            st.session_state.key_colors = update_keyboard_colors(st.session_state.key_colors, feedback)

            if guess == st.session_state.target_word:
                st.session_state.status = 'won'
            elif len(st.session_state.guesses) >= 6:
                st.session_state.status = 'lost'

# Display past guesses
if st.session_state.guesses:
    st.subheader("Your Guesses:")
    for guess, feedback in st.session_state.guesses:
        colors = ''.join(symbol for symbol, _ in feedback)
        word_display = ' '.join(letter.upper() for _, letter in feedback)
        st.markdown(f"**{word_display}** &nbsp;&nbsp; {colors}", unsafe_allow_html=True)

# Draw on-screen keyboard below guesses
def draw_keyboard(colors):
    st.subheader("⌨️ On-Screen Keyboard")
    key_style = {
        '🟩': 'background-color: green; color: white;',
        '🟨': 'background-color: orange; color: white;',
        '⬜': 'background-color: gray; color: white;',
        '': 'background-color: #e0e0e0; color: black;'
    }

    for row in KEYBOARD_ROWS:
        cols = st.columns(len(row), gap='small')
        for i, key in enumerate(row):
            color = colors.get(key, '')
            css = f"""
                <div style='
                    text-align:center;
                    font-size: 20px;
                    padding: 14px;
                    border: 2px solid #888;
                    border-radius: 6px;
                    font-weight:bold;
                    {key_style[color]}
                '>{key}</div>
            """
            cols[i].markdown(css, unsafe_allow_html=True)

draw_keyboard(st.session_state.key_colors)

# Game end messages
if st.session_state.status == 'won':
    st.balloons()
elif st.session_state.status == 'lost':
    st.error(f"The word was: **{st.session_state.target_word.upper()}**")

# Restart game button
if st.session_state.status != 'playing':
    if st.button("🔄 Play Again"):
        st.session_state.target_word = random.choice(WORD_LIST)
        st.session_state.guesses = []
        st.session_state.status = 'playing'
        st.session_state.key_colors = {}

# Attempt counter
st.caption(f"🔢 Attempts: {len(st.session_state.guesses)}/6")