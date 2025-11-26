import os
from gtts import gTTS
from django.conf import settings

def generate_article_audio(article):
    """Generate MP3 audio for an article."""
    text = f"{article.title}. {article.full_description}"

    tts = gTTS(text, lang="en")

    audio_path = os.path.join("article_audio", f"article_{article.id}.mp3")
    full_path = os.path.join(settings.MEDIA_ROOT, audio_path)

    # Create directory if needed
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Save audio file
    tts.save(full_path)

    # Update article field
    article.audio_file = audio_path
    article.save()

    return audio_path
