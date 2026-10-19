import warnings
import googleapiclient.discovery
import googleapiclient.errors

warnings.filterwarnings("ignore")

# Define YouTube API setup
API_KEY = ''  # Replace with your API key
youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=API_KEY)

# Emotion-to-Attributes Mapping
emotion_to_attributes = {
    'happy': ['happy', 'energetic', 'pop', 'danceable', 'mood booster'],
    'sad': ['sad', 'melancholic', 'emotional', 'heartbreak', 'pain'],
    'romantic': ['romantic', 'love', 'soft melody', 'valentine', 'couple song'],
    'shocked': ['shocking', 'thriller', 'intense', 'unexpected'],
    'angry': ['aggressive', 'angry', 'hard rock', 'revenge'],
    'calm': ['calm', 'peaceful', 'soothing', 'meditation'],
    'item songs': ['item song', 'dance hit', 'party'],
    'miscellaneous': ['trending', 'variety', 'mix', 'popular songs']
}

# Function to search YouTube for playlists/videos
def search_youtube_song(query, language, max_results=5, search_type="playlist"):
    """Searches YouTube for playlists or videos with emotion + language constraints."""
    search_query = f"{query} {language} songs"  # Enforce strong emotion-language connection
    request = youtube.search().list(q=search_query, part="snippet", maxResults=max_results, type=search_type)
    response = request.execute()

    if not response.get('items'):
        return []

    results = []
    for item in response['items']:
        video_id = item['id'].get('videoId')
        playlist_id = item['id'].get('playlistId')
        title = item['snippet']['title']
        channel_title = item['snippet']['channelTitle']
        url = f"https://www.youtube.com/watch?v={video_id}" if video_id else f"https://www.youtube.com/playlist?list={playlist_id}"

        # Fetch additional details (views, etc.)
        stats = {}
        if video_id:
            video_request = youtube.videos().list(part="statistics", id=video_id)
            video_response = video_request.execute()
            if video_response['items']:
                stats = video_response['items'][0]['statistics']

        results.append({
            'name': title,
            'artist': channel_title,
            'url': url,
            'views': int(stats.get('viewCount', 0)) if stats else 0,
            'likes': stats.get('likeCount', 'N/A'),
            'is_playlist': bool(playlist_id),
            'language': language
        })

    return results

# Function to get song recommendations based on user feeling and language choice
def get_song_recommendations(user_feeling, selected_languages):
    user_feeling = user_feeling.lower()
    if user_feeling not in emotion_to_attributes:
        print("Sorry, I don't have recommendations for that feeling.")
        return

    attributes = emotion_to_attributes[user_feeling]
    query = " ".join(attributes)  # Create a strong query for searching

    # Get playlists (1 per selected language)
    playlists = []
    for lang in selected_languages:
        results = search_youtube_song(query, lang, max_results=5, search_type="playlist")
        if results:
            playlists.append(results[0])  # Pick the first relevant playlist
    
    # Get highest-viewed songs based on emotion
    song_candidates = []
    for lang in selected_languages:
        results = search_youtube_song(query, lang, max_results=5, search_type="video")
        if results:
            song_candidates.extend(results)

    # Sort songs by views (descending)
    song_candidates.sort(key=lambda x: x['views'], reverse=True)
    
    # Determine how many highest-viewed songs to include based on selected languages
    num_languages = len(selected_languages)
    
    if num_languages == 3:
        additional_songs = song_candidates[:1]  # 1 highest-viewed song
    elif num_languages == 2:
        additional_songs = [song for song in song_candidates if song['language'] in selected_languages][:2]  # 2 highest-viewed songs (one from each language)
    else:
        additional_songs = [song for song in song_candidates if song['language'] in selected_languages][:3]  # 3 highest-viewed songs (from selected language)

    # Prepare the final recommendations list (ensuring 4 recommendations total)
    recommendations = playlists[:num_languages] + additional_songs[:4 - num_languages]

    # Print recommendations
    if recommendations:
        print(f"\nRecommended songs for a {user_feeling} mood:\n")
        for idx, song in enumerate(recommendations, 1):
            print(f"{idx}. {song['name']} by {song['artist']} ({song['language']})")
            print(f"Link: {song['url']}")
            print(f"Views: {song['views']}, Likes: {song['likes']}\n")

# User input
print("HI! I'm MRS")
user_feeling = input("\nHow are you feeling? \n(e.g., happy, sad, romantic, shocked, angry, calm, item songs, miscellaneous): ")

# Get user language choice
print("\nSelect languages for recommendations (you can choose 1, 2, or all 3):")
print("1. Hindi")
print("2. Kannada")
print("3. Telugu")

selected_numbers = input("Enter the numbers corresponding to your language choices (e.g., 1 2 for Hindi & Kannada): ")
valid_options = {"1": "hindi", "2": "kannada", "3": "telugu"}

selected_languages = [valid_options[num] for num in selected_numbers.split() if num in valid_options]

if not selected_languages:
    print("No valid language selected. Defaulting to all three languages.")
    selected_languages = ["hindi", "kannada", "telugu"]

# Get/display song recommendations 
get_song_recommendations(user_feeling, selected_languages)

input("\nPress Enter to exit...")
