import os
import json
import aiohttp
import time
import sys
import requests
import asyncio
import ffmpeg
import shutil
from pyrogram import Client
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# Telegram and Google Drive API credentials
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.json'
CHAT_ID = 'sdbvipmovie'  # Replace with your target chat ID

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

async def save_video_with_api_key(key, session, movie_data, retries=1, delay=60):
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,my;q=0.8,ca;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest",
                "cookie": "adonis-remember-token=f033e081f9f32df542abb27ca3843727LMkGBLD3yNLlnVtU2v3qW0zoO5zNXtkDkH0BF1rZKZ4VherCxabyfch6kSyk9arZX9Jen00wNiW6nRQkvVG0ROYBs12sDUfKuMwLnnG3EsbuM3J3cTWOgNuKlEUgqbqd; _gid=GA1.2.5648603.1724083726; _ga=GA1.2.702253506.1723665907; __gads=ID=d19dd9f6e85b1e64:T=1723665905:RT=1724122454:S=ALNI_Mbu0UxBAGgE3DE8EyfN4CLF1k7MLw; __gpi=UID=00000ebf173d6e96:T=1723665905:RT=1724122454:S=ALNI_MY3ISM32YM9RXxxlDi5Npvmy9S7wg; __eoi=ID=54497ef89a9f2f5c:T=1723665905:RT=1724122454:S=AA-Afjay81IOjtGh_JTvnt0ujWYN; adonis-session=1b7c99d89c7f9ab14815c64c23a6a981ImeEAsw4BRW1L4C9M8VJNwjZvSDHaacWyjiFGN5s4GRWst1dh9mj0u%2Be1NBZyjf06BV3x95iAHSuGuYId%2FrSEhnmfeAxiLWJ1vm5hxJ0ugf5gi7Ckhl5zSG0Ukroo7Z6; XSRF-TOKEN=13e9676937abc6969e54811a50b6f387jE0IzB7%2BJ%2FyCnK1qbwG%2BIxOOTxX%2FMON7qYfXXVuRzls8x%2FWjxQ2xX1b%2FOgXOwh%2Fr6MihxmkXjkvB%2FoS1%2BIlwyrB9LWIoRTuxK%2FjwkqEYhjvLuFLWLZhymHdEqaagin1C; adonis-session-values=161356f775d28e7933f237f27fcbc82bJy4NZQGHg9qAzauWA0MBiDYGTrj0dJAXT%2BKikIrBiJ2ppPqnMQU5OWX9PfsngFSh47bkvhJxwt2bUJvPOhV1KweSAoK4E181x%2FebREyYELz1ks%2FUY74miuTale3arcnOL%2B3i3svJXzz9BmTB8zV5xcKJH8Mqx30EYynMfvtT9dHbDs3kooiPWivTAo%2F9bIBdSo8KkE8PpewSnw%2Fs8pQHTSOKVdxafVevp6a5rAro%2FRY%3D; _gat_gtag_UA_84556149_5=1; _ga_KXGEV8GJMZ=GS1.1.1724122358.9.1.1724122727.0.0.0",
                "Referer": "https://yoteshinportal.cc/drive/your-referer",  # Replace with actual Referer
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
            async with session.post("https://yoteshinportal.cc/api/save", headers=headers, json={"key": key}) as response:
                if response.status != 200:
                    response_text = await response.text()
                    data = await response.json()
                    reason = data.get("reason")

                    if reason == "rateLimitExceeded":
                        print(f"Rate limit exceeded for movie: {movie_data['name']}. Retrying attempt {attempt} of {retries}.")
                        await asyncio.sleep(delay)
                        continue  # Retry the request

                    elif reason == "notFound":
                        print(f"Error: File not found for movie: {movie_data['name']}. Removing from 1.json.")
                        remove_movie_from_json(movie_data)
                        return None  # Stop processing this movie and move to the next one

                    else:
                        print(f"Error: Received status code {response.status}")
                        print(f"Response content: {response_text}")
                        continue  # Retry other errors
                
                data = await response.json()
                if 'fileId' in data:
                    return data['fileId']
                else:
                    print(f"Unexpected response format: {data}")
                    continue  # Retry on unexpected response format

        except Exception as e:
            print(f"Attempt {attempt} of {retries}. Retrying in {delay} seconds. Exception: {e}")
            await asyncio.sleep(delay)

    print("Max retries exceeded. Moving to the next movie.")
    return None  # Return None after max retries

def remove_movie_from_json(movie_data):
    try:
        with open('1.json', 'r+', encoding='utf-8') as f:
            all_movies = json.load(f)
            updated_movies = [movie for movie in all_movies if movie['id'] != movie_data['id']]
            f.seek(0)
            json.dump(updated_movies, f, ensure_ascii=False, indent=4)
            f.truncate()
        print(f"Removed {movie_data['name']} from 1.json.")
    except Exception as e:
        print(f"Failed to remove {movie_data['name']} from 1.json: {e}")

def download_file_from_drive(file_id, drive_service, download_path):
    request = drive_service.files().get_media(fileId=file_id)
    with open(download_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
    print(f"File downloaded from Google Drive to {download_path}")

def delete_file_from_drive(file_id, drive_service):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        print(f"File with ID {file_id} deleted from Google Drive.")
    except Exception as e:
        print(f"Failed to delete file from Google Drive: {e}")

def extract_video_metadata(file_path):
    try:
        metadata = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)

        if not video_stream:
            raise ValueError("No video stream found")

        # Attempt to extract metadata
        try:
            duration = int(float(video_stream.get('duration', 0)))
        except (TypeError, ValueError):
            duration = None

        width = video_stream.get('width')
        height = video_stream.get('height')

        if duration is None or not width or not height:
            print(f"Extracted Metadata: {metadata}")
            print(f"Duration: {duration}, Width: {width}, Height: {height}")
            raise ValueError("Duration, width, or height not found in video metadata")

        return {
            'width': width,
            'height': height,
            'duration': duration
        }
    except ffmpeg.Error as e:
        print(f"Error probing video file: {e.stderr.decode('utf-8')}")
        raise

async def create_thumbnail(file_path, thumb_path):
    try:
        (
            ffmpeg
            .input(file_path, ss=60)  # Seeks to 10 seconds into the video
            .filter('thumbnail', n=2)  # Change the 'n' value to at least 2 1280 x 720
            .output(thumb_path, vframes=1, format='image2', vcodec='mjpeg', s='1280x720')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Thumbnail created successfully at {thumb_path}")
    except ffmpeg.Error as e:
        print(f"Error creating thumbnail: {e.stderr.decode('utf-8')}")

async def upload_movie(app, movie_data):
    creds = authenticate_google()
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Download and process the movie
    temp_download_path = f"{movie_data['key']}_temp_video"
    download_path = f"{movie_data['name']}_video"
    thumb_path = 'thumbnail.jpg'
    
    async with aiohttp.ClientSession() as session:
        try:
            key = movie_data['key']
            file_id = await save_video_with_api_key(key, session,movie_data)
            download_file_from_drive(file_id, drive_service, temp_download_path)
            
            if os.path.exists(temp_download_path):
                ext = os.path.splitext(temp_download_path)[-1]
            else:
                ext = ".mp4"
            
            final_temp_path = temp_download_path + ext
            final_download_path = download_path + ext
            os.rename(temp_download_path, final_temp_path)
            shutil.move(final_temp_path, final_download_path)
            
            metadata = extract_video_metadata(final_download_path)
            await create_thumbnail(final_download_path, thumb_path)
            
            post_link = await upload_to_telegram(app, final_download_path, thumb_path, movie_data, metadata)
            print(f"movieLink saved: {post_link}")
            return post_link
            
        finally:
            if os.path.exists(final_download_path):
                os.remove(final_download_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            if os.path.exists(final_temp_path):
                os.remove(final_temp_path)
            delete_file_from_drive(file_id, drive_service)


async def process_movie_data(movie_data, app):
    try:
        # Check if mainMovieLink exists, skip if it does
        if 'mainMovieLink' in movie_data and movie_data['mainMovieLink']:
            print(f"Skipping {movie_data['name']} as it already has a mainMovieLink.")
            return

        # Check if synopsisLink exists, if not send the synopsis
        if 'synopsisLink' not in movie_data or not movie_data['synopsisLink']:
            print(f"Sending synopsis for {movie_data['name']}.")
            synopsis_link = await send_synopsis(app, movie_data)
            movie_data['synopsisLink'] = synopsis_link
            save_movie_data(movie_data)
        
        # Check if movieLink exists, if not upload the movie
        if 'movieLink' not in movie_data or not movie_data['movieLink']:
            print(f"Uploading movie for {movie_data['name']}.")
            movie_link = await upload_movie(app, movie_data)
            if movie_link is None:
                # If movie upload failed, skip the rest of the process
                return
            movie_data['movieLink'] = movie_link
            save_movie_data(movie_data)
        
        # Finally, send the poster and caption, and save mainMovieLink
        print(f"Sending poster and caption for {movie_data['name']}.")
        main_movie_link = await send_poster_and_caption(app, movie_data)
        movie_data['mainMovieLink'] = main_movie_link
        save_movie_data(movie_data)
    
    except Exception as e:
        print(f"Error processing {movie_data['name']}: {e}")
        # Continue to the next movie without stopping the program

def save_movie_data(movie_data):
    try:
        with open('1.json', 'r+', encoding='utf-8') as f:
            all_movies = json.load(f)
            for i, movie in enumerate(all_movies):
                if movie['id'] == movie_data['id']:
                    all_movies[i] = movie_data
                    break
            f.seek(0)
            json.dump(all_movies, f, ensure_ascii=False, indent=4)
            f.truncate()
        print(f"Movie data saved for {movie_data['name']}.")
    except Exception as e:
        print(f"Failed to save movie data for {movie_data['name']}: {e}")


async def send_synopsis(app, movie_data):
    synopsis = movie_data.get('synopsis')
    name = movie_data.get('name')

    # Check if the synopsis is None or empty/whitespace
    if not synopsis or synopsis.strip() == '':
        print(f"No synopsis available for {name}. Skipping.")
        return None

    # Format the message to include the movie name and the synopsis
    message_text = f"<b>{name}</b>\n\n{synopsis.strip()}"

    # Send the synopsis to the mivieso chat
    try:
        sent_message = await app.send_message('mivieso', text=message_text)
        print(f"synopsisLink saved: https://t.me/mivieso/{sent_message.id}")
        return f"https://t.me/mivieso/{sent_message.id}"
    except Exception as e:
        print(f"Error sending synopsis: {e}")
        return None

async def upload_to_telegram(app, file_path, thumb_path, movie_data, metadata):
    # Create the caption
    name = movie_data['name']
    caption = name
    if movie_data.get('genres'):
        genres = ', '.join(movie_data['genres'])
        caption += f" · {genres}"
    if movie_data.get('imdb') and movie_data['imdb'].get('rating'):
        imdb_rating = movie_data['imdb']['rating']
        caption += f" · IMDb: {imdb_rating}"
    caption += f"\nDuration: {timedelta(seconds=metadata['duration'])}"

    # Upload the video to Telegram
    print(f"Uploading video to Telegram.", flush=True)
    sent_message = await app.send_video(
        chat_id=CHAT_ID,
        video=file_path,
        thumb=thumb_path,
        caption=caption,
        duration=metadata['duration'],
        width=metadata['width'],
        height=metadata['height'],
        supports_streaming=True,
    )
    print(f"Video uploaded to Telegram successfully.", flush=True)

    # Generate the copy-post link
    if sent_message.chat.username:  # Public channel/chat
        post_link = f"https://t.me/{sent_message.chat.username}/{sent_message.id}"
    else:  # Private chat/channel
        post_link = f"https://t.me/c/{sent_message.chat.id}/{sent_message.id}"
    
    print(f"Copy-post link: {post_link}", flush=True)
    return post_link

async def send_poster_and_caption(app, movie_data):
    caption = f"<b>{movie_data['name']}</b>"
    if movie_data.get('genres'):
        genres = ', '.join(movie_data['genres'])
        caption += f" · {genres}"
    if movie_data.get('imdb') and movie_data['imdb'].get('rating'):
        imdb_rating = movie_data['imdb']['rating']
        caption += f" · IMDb: {imdb_rating}"
    caption += f"\n\n<a href='{movie_data.get('movieLink')}'>ဇာတ်ကားကြည့်ရန်</a>\n\n<a href='{movie_data.get('synopsisLink')}'>ဇာတ်ညွန်းဖတ်ရန်</a>"
    
    poster_path = 'poster.jpg'
    try:
        response = requests.get(movie_data['poster'], stream=True)
        if response.status_code == 200:
            with open(poster_path, 'wb') as f:
                f.write(response.content)
            sent_message = await app.send_photo('sdbvip', photo=poster_path, caption=caption)
        else:
            sent_message = await app.send_message('sdbvip', text=caption,disable_web_page_preview=True)
        main_movie_link = f"https://t.me/sdbvip/{sent_message.id}"
        print(f"mainMovieLink saved: {main_movie_link}")
        return main_movie_link
    except Exception as e:
        print(f"Error downloading or sending poster: {e}")
        sent_message = await app.send_message('sdbvip', text=caption,disable_web_page_preview=True)
        main_movie_link = f"https://t.me/sdbvip/{sent_message.id}"
        print(f"mainMovieLink saved: {main_movie_link}")
        return main_movie_link
    finally:
        if os.path.exists(poster_path):
            os.remove(poster_path)

async def main():
    async with app:
        me = await app.get_me()
        print(f"Logged in as {me.username}")

        # Load the movie data
        with open('1.json', 'r', encoding='utf-8') as f:
            movies_data = json.load(f)

        # Process each movie in the list
        for movie in movies_data:
            await process_movie_data(movie, app)

# Run the main function using app.run()
app.run(main())
