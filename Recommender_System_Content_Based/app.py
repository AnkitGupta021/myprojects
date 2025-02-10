
import streamlit as st
import joblib
import requests
import time

# Load models
df = joblib.load('movies.pkl')
similarity = joblib.load('similarity_vec.pkl')


@st.cache_data
def fetch_path(movie_id, retries=3, delay=5):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=63a0965b07eac923c5a327e98e4e77fc&language=en-US"

    for _ in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            break
        except requests.exceptions.RequestException:
            time.sleep(delay)

    return "https://via.placeholder.com/500"


def recommend(movie):
    recommended_movies = []
    recommended_movies_path = []

    try:
        index = df[df.title == movie].index[0]
    except IndexError:
        return [], []

    dis = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    for i in dis[1:6]:
        movie_index = i[0]
        recommended_movies.append(df.iloc[movie_index].title)
        recommended_movies_path.append(fetch_path(df.iloc[movie_index].movie_id))

    return recommended_movies, recommended_movies_path


# Streamlit UI
st.title('Movie Recommendation System')

# Initialize session state
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = df['title'].values[0]
if 'recommend_movies' not in st.session_state:
    st.session_state.recommend_movies = []
    st.session_state.recommend_posters = []

# Movie selection
option = st.selectbox('Select a movie', df['title'].values,
                      index=list(df['title'].values).index(st.session_state.selected_movie))

# If a new movie is selected, reset recommendations
if option != st.session_state.selected_movie:
    st.session_state.selected_movie = option
    st.session_state.recommend_movies = []  # Clear old recommendations
    st.session_state.recommend_posters = []
    st.rerun()

# Fetch and display the selected movie's poster
selected_movie_id = df[df.title == st.session_state.selected_movie].movie_id.values[0]
selected_movie_poster = fetch_path(selected_movie_id)
movie_url = f"https://www.themoviedb.org/movie/{selected_movie_id}"

st.image(selected_movie_poster, width=150)
st.link_button("View on TMDB", movie_url)

# Recommend button
if st.button("Recommend"):
    st.session_state.recommend_movies, st.session_state.recommend_posters = recommend(st.session_state.selected_movie)

# Display recommendations only if the button is clicked
if st.session_state.recommend_movies:
    names, posters = st.session_state.recommend_movies, st.session_state.recommend_posters

    if names:
        col = st.columns(5)
        for i in range(5):
            with col[i]:
                movie_id = df[df.title == names[i]].movie_id.values[0]
                movie_url = f"https://www.themoviedb.org/movie/{movie_id}"

                # Display the poster
                st.image(posters[i])

                # Clickable recommended movie with unique key
                if st.button(names[i], key=f"rec_btn_{i}"):
                    st.session_state.selected_movie = names[i]
                    st.session_state.recommend_movies, st.session_state.recommend_posters = recommend(names[i])
                    st.rerun()

                # Add clickable button below the image
                st.link_button("View on TMDB", movie_url)
