# import streamlit as st
# import joblib
# import requests, time
#
# df = joblib.load('movies.pkl')
# similarity = joblib.load('similarity_vec.pkl')
#
# def fetch_path(movie_id):
#     proxies = {
#         "http": "http://your-proxy.com:8080",
#         "https": "http://your-proxy.com:8080",
#     }
#     response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=63a0965b07eac923c5a327e98e4e77fc&language=en-US", timeout=20)
#     data = response.json()
#     return 'https://image.tmdb.org/t/p/w500/'+ data['poster_path']
#
#
# def recommend(movie):
#     recommended_movies = []
#     recommended_movies_path = []
#     index = df[df.title==movie].index[0] ## Finding the index of the movie entered by user
#
#     dis = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x:x[1])
#
#     for i in dis[1:6]:
#         movie_index = i[0] # Fetching the index of recommended movie
#
#         recommended_movies.append(df.iloc[movie_index].title)
#         # FETCH POSTER USING API KEY AT TMDB
#         recommended_movies_path.append(fetch_path(df.iloc[movie_index].movie_id))
#
#     return recommended_movies, recommended_movies_path
#
#
#
# # Display the title
# st.title('Movie Recommendation System')
#
# # Display movies in DropDown
#
# option = st.selectbox('Select a movies',df['title'].values)
#
# # Recommend Button and Display
#
# if st.button('Recommend'):
#     names, posters = recommend(option)
#
#     col = st.columns(5)
#     for i in range(5):
#         movie_id = df[df['title'] == names[i]].movie_id.values[0]  # Fetch movie ID
#         movie_url = f"https://www.themoviedb.org/movie/{movie_id}"  # Construct TMDB URL
#
#         with col[i]:
#             st.markdown(f'<a href="{movie_url}" target="_blank"><img src="{posters[i]}" width="150"></a>',
#                         unsafe_allow_html=True)
#             st.text(names[i])
#         # with col[i]:
#         #     st.text(names[i])
#         #     st.image(posters[i])

######################################
import streamlit as st
import joblib
import requests
import time

# Load models
df = joblib.load('movies.pkl')
similarity = joblib.load('similarity_vec.pkl')

@st.cache_data
# Function to fetch movie poster
def fetch_path(movie_id, retries=3, delay=5):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=63a0965b07eac923c5a327e98e4e77fc&language=en-US"

    for _ in range(retries):
        try:
            response = requests.get(url, timeout=10)  # Reduce timeout to 10s
            response.raise_for_status()  # Raise error for HTTP issues
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            break  # Exit loop if successful
        except requests.exceptions.RequestException:
            time.sleep(delay)  # Wait before retrying

    return "https://via.placeholder.com/500"  # Default placeholder image


# Function to recommend movies
def recommend(movie):
    recommended_movies = []
    recommended_movies_path = []

    try:
        index = df[df.title == movie].index[0]  # Get movie index
    except IndexError:
        return [], []  # Return empty lists if movie not found

    dis = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    for i in dis[1:6]:  # Get top 5 similar movies
        movie_index = i[0]
        recommended_movies.append(df.iloc[movie_index].title)
        recommended_movies_path.append(fetch_path(df.iloc[movie_index].movie_id))  # Fetch poster

    return recommended_movies, recommended_movies_path


# Streamlit UI
st.title('Movie Recommendation System')

# Movie selection
option = st.selectbox('Select a movie', df['title'].values)

# Fetch and display the selected movie's poster
if option:
    selected_movie_id = df[df.title == option].movie_id.values[0]  # Get movie ID
    selected_movie_poster = fetch_path(selected_movie_id)  # Fetch the poster

    # st.image(selected_movie_poster,width=150)
    movie_url = f"https://www.themoviedb.org/movie/{selected_movie_id}"  # Create TMDB URL

    # Display poster
    st.image(selected_movie_poster,width=150)

    # Add a clickable button below the image
    st.link_button("View on TMDB", movie_url)

# Recommend Button and Display
if st.button('Recommend'):
    names, posters = recommend(option)

    if names:
        col = st.columns(5)
        for i in range(5):
            with col[i]:
                # st.text(names[i])
                # st.image(posters[i])

                movie_id = df[df.title == names[i]].movie_id.values[0]  # Get recommended movie ID
                movie_url = f"https://www.themoviedb.org/movie/{movie_id}"  # Create TMDB URL

                # Display the poster
                st.image(posters[i])

                # Add clickable button below the image
                st.link_button("View on TMDB", movie_url)

                st.text(names[i])
