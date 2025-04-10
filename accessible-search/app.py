import streamlit as st
import scrapper as sc
import pandas as pd
from gtts import gTTS
import io
import base64


# Function to generate and return the audio content as base64 string
def text_to_speech_base64(text):
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    return f"data:audio/mp3;base64,{b64}"


# Function to handle navigation
def nav_page(page):
    st.session_state.page = page


# Sidebar with navigation links
st.sidebar.title("Navigation")
if st.sidebar.button("Home               "):
    nav_page("Home")
if st.sidebar.button("web検索        "):
    nav_page("fast-search")

# Define the default page
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Display content based on the selected page
if st.session_state.page == "Home":
    st.title("ようこそ！！")
    st.write("このwebサイトでは検索した言葉の読み上げを行い検索をサポートします")

elif st.session_state.page == "fast-search":
    search = st.text_input("ここに検索したい言葉を入れてね！")
    # Check if search term is not empty and has changed
    if search:
        search_ = search.replace(' ','+')
        # Use a spinner while fetching search results
        with st.spinner(f'Fetching search results for {search} ....'):
            response = sc.get_response(
                f'https://www.google.com/search?q={search_}')

        if isinstance(response, str):
            st.error(response)
        else:
            data_result = sc.google_search(response)
            if data_result['snippets']:
                df = pd.DataFrame(data_result)

                # Display the DataFrame with an "Announce" button for each row
                for i, row in df.iterrows():
                    st.write(row['snippets'])
                    st.write(', '.join(row['links']))
                    st.write(row['providers'])
                    if st.button(f"Announce {i+1}", key=f"announce_{i}"):
                        audio_data = text_to_speech_base64(row['snippets'])
                        st.markdown(
                            f'<audio controls autoplay src="{audio_data}"></audio>',
                            unsafe_allow_html=True,
                        )
                    st.write("---")
            else:
                st.warning("何も見つかりませんでした。")
