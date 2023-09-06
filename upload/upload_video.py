#!/usr/bin/python3
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Credenciales y token de acceso
access_token = "[access_token]"
credentials = google.oauth2.credentials.Credentials(access_token)

# Crea un servicio de YouTube
youtube = build("youtube", "v3", credentials=credentials)

# Parámetros del video
video_path = "/Users/fleyva/projects/@eyvotTest/content/youtube/short-067.mov"
video_title = "Video de prueba"
video_description = "Prueba de descripción"
video_tags = ["TAG1", "TAG2", "TAG3"]
video_category_id = "20"

# Sube el video
media = MediaFileUpload(video_path)
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": video_title,
            "description": video_description,
            "tags": video_tags,
            "categoryId": video_category_id
        },
        "status": {
            "privacyStatus": "private"
        }
    },
    media_body=media
)
response = request.execute()

# Imprime el ID del video subido
video_id = response["id"]
print(f"Video subido con éxito. ID del video: {video_id}")
