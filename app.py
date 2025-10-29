"""
Author: Aman Jha
Email: kr.amanjha02@gmail.com
Date: 2025-Oct-15
"""

import pickle
import streamlit as st
import requests
import pandas as pd

# -------------------- Utility Functions -------------------- #
def fetch_poster(movie_id):
    """Fetches the movie poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


def recommend(movie):
    """Recommends 5 similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], [], [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_years.append(movies.iloc[i[0]].year)
        recommended_movie_ratings.append(movies.iloc[i[0]].vote_average)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings


# -------------------- Streamlit Page Config -------------------- #
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

# -------------------- Header -------------------- #
st.markdown(
    """
    <div style="text-align:center; padding: 10px 0;">
        <h1 style="color:#FF4B4B;">🎬 Movie Recommender System</h1>
        <h4 style="color:gray;">Discover your next favorite movie powered by Machine Learning</h4>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Load Models -------------------- #
try:
    movies_dict = pickle.load(open('models/movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("⚠️ Model files not found. Please run the preprocessing notebook first.")
    st.stop()

# -------------------- Movie Selection -------------------- #
st.markdown("### 🔍 Search for a Movie")
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown:",
    movies['title'].values,
    index=None,
    placeholder="e.g. Avatar, The Dark Knight, Interstellar..."
)

# -------------------- Recommendation Button -------------------- #
if st.button("🎥 Show Recommendations", use_container_width=True):
    if not selected_movie:
        st.warning("Please select a movie first!")
    else:
        with st.spinner("🔎 Finding movies you might like..."):
            names, posters, years, ratings = recommend(selected_movie)

        if names:
            st.success(f"Here are 5 movies similar to **{selected_movie}** 🎉")

            # Create cards for each movie
            cols = st.columns(5, gap="medium")
            for i, col in enumerate(cols):
                with col:
                    st.image(posters[i], width=150)
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                            <h5 style="margin:5px 0; color:#FF4B4B;">{names[i]}</h5>
                            <p style="color:gray;">📅 {int(years[i]) if pd.notna(years[i]) else 'N/A'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Ratings visual
                    rating = ratings[i] if pd.notna(ratings[i]) else 0
                    st.progress(min(rating / 10, 1.0))
                    st.caption(f"⭐ {rating:.1f}/10")

# -------------------- Footer -------------------- #
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:gray;">
        Built with ❤️ by <b>Aman Jha</b> | Powered by Streamlit & TMDB API
    </div>
    """,
    unsafe_allow_html=True,
)
