import streamlit as st
import mysql.connector
import pandas as pd
import os

new_folder_path = './image'

if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f"Folder '{new_folder_path}' created successfully.")
else:
    print(f"Folder '{new_folder_path}' already exists.")

new_folder_path = './video'

if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f"Folder '{new_folder_path}' created successfully.")
else:
    print(f"Folder '{new_folder_path}' already exists.")

conn = mysql.connector.connect(
    host="localhost",
    database="ott",
    user="root",
    password="Vardhan@24",
    auth_plugin='mysql_native_password'
)

cursor = conn.cursor()

gusername = ""

if 'username' not in st.session_state:
    st.session_state.username = ""

content_query = 'SELECT * FROM content'
cursor.execute(content_query)
content_data = cursor.fetchall()

content = {}
for row in content_data:
    content[row[1]] = {
        'poster': str(row[7]),
        'description': row[2],
        'genre': row[6],
        'subscription': row[5],
        'release_date': row[3],
        'duration': row[4],
    }


dict_content = {"Basic": 1, "Premium": 2}


def display_movie_details(title):
    movie = content[title]
    st.title(title)

    if 'poster' in movie and movie['poster']:
        st.image(f"image/{movie['poster']}",
                 caption=f"{title} Poster", width=250)

    else:
        st.warning("No poster available for this movie.")

    st.write(f"Year of Release: {movie['release_date'].strftime('%Y-%m-%d')}")
    st.write(f"Description: {movie['description']}")
    st.write(f"Duration: {movie['duration']} minutes")
    st.write(f"Genre: {movie['genre']}")
    st.write(f"Rating: {movie['subscription']}")


def display_content():
    if gusername == "":
        st.title("Please LOGIN before coming to the movies page")
    for title, details in content.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(details['poster'],
                     caption=f"{title} Poster", use_column_width=True)
        with col2:
            st.write("Title:", title)
            st.write("Description:", details['description'])
            st.write("Genre:", details['genre'])
            st.write("Subscription:", details['subscription'])
            st.write("Year of Release:",
                     details['release_date'].strftime('%Y-%m-%d'))
            st.write("Duration:", f"{details['duration']} minutes")
            st.button("View Details", key=f"{title}_details",
                      on_click=display_movie_details, args=(title,))


def admin():
    st.title("ADD A MOVIE")
    images_directory = "image"
    videos_directory = "video"
    os.makedirs(images_directory, exist_ok=True)
    with st.expander("Click to expand"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        release_date = st.date_input("Release Date")
        duration = st.number_input("Duration", min_value=0)
        rating = st.slider("Rating", min_value=0.0, max_value=10.0, step=0.1)
        content_genre = st.text_input("Content Genre")

        # File uploader for image
        image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

        # File uploader for video
        video = st.file_uploader("Upload Video", type=["mp4"])

    # If files are uploaded, save them and display
    if image:
        image_path = os.path.join(images_directory, image.name)
        with open(image_path, "wb") as f:
            f.write(image.read())
        st.image(image_path, caption="Uploaded Image", use_column_width=True)

    if video:
        video_path = os.path.join(videos_directory, video.name)
        with open(video_path, "wb") as f:
            f.write(video.read())
        st.video(video_path)

    video_name = st.text_input("Video Name")
    image_name = st.text_input("Image Name")

    if st.button("Submit"):
        query = 'INSERT INTO content(Title, Description, Release_Date, Duration, Rating, ContentGenre, image, Video_Name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (title, description, release_date,
                       duration, rating, content_genre, image_name, video_name))
        conn.commit()
        st.success("Movie added successfully!")

    st.header("Delete a Movie")

    # Fetch existing movies
    movies_query = 'SELECT Title FROM content'
    cursor.execute(movies_query)
    movies_data = cursor.fetchall()
    movie_to_delete = st.selectbox("Select a movie to delete", [
                                   movie[0] for movie in movies_data])

    if st.button("Delete Movie"):
        # Fetch image and video names for the selected movie
        fetch_names_query = 'SELECT image, Video_Name FROM content WHERE Title = %s'
        cursor.execute(fetch_names_query, (movie_to_delete,))
        names_data = cursor.fetchone()

        if names_data:
            image_name, video_name = names_data

            # Delete movie from the database
            delete_query = 'DELETE FROM content WHERE Title = %s'
            cursor.execute(delete_query, (movie_to_delete,))
            conn.commit()
            st.success("Movie deleted successfully!")

            # Delete corresponding image and video files
            image_path = os.path.join(images_directory, image_name)
            video_path = os.path.join(videos_directory, video_name)

            if os.path.exists(image_path):
                os.remove(image_path)
                st.success("Image deleted successfully!")

            if os.path.exists(video_path):
                os.remove(video_path)
                st.success("Video deleted successfully!")
        else:
            st.error("Movie not found in the database.")

    calculate_revenue()

    selected_user = st.selectbox("Select a User:", get_usernames())

    if st.button("Fetch Reviews"):
        # Fetch reviews for the selected user
        reviews_data = fetch_reviews(selected_user)

        # Display reviews in a DataFrame
        if reviews_data:
            columns = ['Username', 'Email', 'Review', 'Title']
            df_reviews = pd.DataFrame(reviews_data, columns=columns)
            st.dataframe(df_reviews)
        else:
            st.warning("No reviews found for the selected user.")


def fetch_reviews(username):
    query = '''
    SELECT user.Username, user.Email, review.Comment, content.Title
    FROM (
        SELECT UserID, Username, Email
        FROM user
        WHERE Username = %s
    ) user
    JOIN review ON user.UserID = review.UserID
    JOIN content ON review.ContentID = content.ContentID;
    '''

    cursor.execute(query, (username,))
    result = cursor.fetchall()
    return result


def get_usernames():
    query = "SELECT DISTINCT Username FROM user;"
    cursor.execute(query)
    result = cursor.fetchall()
    usernames = [user[0] for user in result]
    return usernames


def calculate_revenue():
    st.title("Calculate Revenue")
    subscription_type = st.selectbox(
        "Select Subscription Type", ["Basic", "Premium"])

    if st.button("Calculate Revenue"):
        # Use a SELECT statement to call the function
        query = 'SELECT CalcTotalRevenue(%s)'
        cursor.execute(query, (dict_content[subscription_type],))
        result = cursor.fetchone()

        if result:
            total_revenue = result[0]
            st.success(
                f"Total Revenue for {subscription_type} users: ${total_revenue}")
        else:
            st.warning("No revenue data available.")


def login():
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    login_button = st.button("Login")

    st.markdown("New user? [Signup here](?route=signup)",
                unsafe_allow_html=True)

    if login_button:
        login_query = 'SELECT * FROM user WHERE Username = %s AND Password = %s'
        cursor.execute(login_query, (username, password))
        user_data = cursor.fetchone()

        if user_data:
            query = 'select Role from User where Username=%s AND Password=%s'
            cursor.execute(query, (username, password))
            Role = cursor.fetchone()
            print(Role)
            if Role[0].capitalize() == 'Admin':
                st.experimental_set_query_params(route="admin")
                return username
            st.success("Logged in successfully")
            st.experimental_set_query_params(route="movies")
            st.session_state.username = username  # Store the username in session state
            return username
        else:
            st.error("Incorrect username or password")
            return None


def signup():
    st.title("Sign Up")
    with st.expander("Click to expand"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        email = st.text_input("Email")
        name = st.text_input("Name")
        title = st.selectbox("Select content", ["Basic", "Premium"])

    if st.button("Signup"):
        check_username_query = 'SELECT * FROM user WHERE Username = %s'
        cursor.execute(check_username_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            st.error("Username already exists. Please choose a different one.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            insert_user_query = (
                'INSERT INTO user (Username, Password, Email, Name, Subscription_ID) '
                'VALUES (%s, %s, %s, %s, %s)'
            )
            user_data = (username, password, email, name, dict_content[title])
            cursor.execute(insert_user_query, user_data)
            conn.commit()
            st.success("Account created successfully. You can now log in.")
            st.experimental_set_query_params(route="login")


def play_video(video_name):
    st.title("Video Player")
    st.video(f"video/{video_name}")
    display_reviews(video_name)
    st.header("Add Your Review")
    user_review = st.text_area("Your Review", max_chars=500)
    user_rating = st.slider("Your Rating", min_value=1, max_value=10, value=5)

    if st.button("Submit Review"):
        submit_review(gusername, video_name, user_review, user_rating)
        st.success("Review submitted successfully!")


def submit_review(username, video_name, user_review, user_rating):
    user_id_query = 'SELECT UserID FROM user WHERE Username = %s'
    cursor.execute(user_id_query, (st.session_state.username,))
    user_result = cursor.fetchone()
    if user_result is not None:
        user_id = user_result[0]
        content_id_query = 'SELECT ContentID FROM content WHERE Video_Name = %s'
        cursor.execute(content_id_query, (video_name,))
        content_result = cursor.fetchone()
        if content_result is not None:
            content_id = content_result[0]
            insert_review_query = 'INSERT INTO review (UserID, ContentID, Comment, Rating) VALUES (%s, %s, %s, %s)'
            cursor.execute(insert_review_query,
                           (user_id, content_id, user_review, user_rating))
            conn.commit()
            st.success("Review submitted successfully.")
        else:
            st.error("Content not found.")
    else:
        st.error("User not found.")


def display_reviews(video_name):
    st.header("User Reviews")
    reviews_query = 'SELECT review.*,user.Username FROM review JOIN content ON review.ContentID=content.ContentID JOIN user on user.UserID = review.UserID WHERE Video_Name = %s'
    cursor.execute(reviews_query, (video_name,))
    reviews_data = cursor.fetchall()
    if not reviews_data:
        st.write("No reviews available.")
    else:
        for review in reviews_data:
            st.write(f"User: {review[6]}")
            st.write(f"Rating: {review[3]}")
            st.write(f"Review: {review[4]}")
            st.write("---")


def main():
    st.set_page_config(page_title="OTT App")
    st.title("Welcome to the OTT App")

    route = st.experimental_get_query_params().get("route", [""])[0]

    if route == "":
        st.markdown(
            "New user? [Signup here](?route=signup)", unsafe_allow_html=True)
        st.markdown(
            "Existing user? [Login here](?route=login)", unsafe_allow_html=True)

    elif route == "login":
        login()

    elif route == "signup":
        signup()

    elif route == "movies":
        st.title("Select Content")
        title = st.selectbox("Choose a movie", list(content.keys()))
        with st.sidebar:
            st.title("Subscription Plan")
            new_subscription_plan = st.selectbox(
                "Change Subscription Plan", ["Basic", "Premium"])
            change_subscription_query = 'UPDATE user SET Subscription_ID = %s WHERE Username = %s'
            cursor.execute(change_subscription_query,
                           (dict_content[new_subscription_plan], st.session_state.username))
            conn.commit()
            st.success(f"Subscription plan changed to {new_subscription_plan}")

        if st.button("Play Video"):
            video_name_query = 'SELECT Video_Name FROM content WHERE Title = %s'
            cursor.execute(video_name_query, (title,))
            video_name = cursor.fetchone()[0]
            st.experimental_set_query_params(
                route="video", video_name=video_name)
            display_movie_details(title)

    elif route == "video":
        video_name = st.experimental_get_query_params().get("video_name", [""])[
            0]
        play_video(video_name)

    elif route == "admin":
        admin()


if __name__ == "__main__":
    main()
