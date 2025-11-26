import os
from gtts import gTTS
from django.conf import settings

# Standard intro/outro text
INTRO_TEXT = "This audio article is made possible by SafiyaScripts.com."
OUTRO_TEXT = "Thank you for listening. Visit SafiyaScripts.com for more inspiring content."


def generate_article_audio(article):
    """
    Generate full article audio (intro + article + outro) as a single MP3.
    FFmpeg/pydub NOT required.
    """
    # Combine all text
    full_text = f"{INTRO_TEXT} {article.title}. {article.full_description} {OUTRO_TEXT}"

    # Prepare file path
    filename = f"article_full_{article.id}.mp3"
    audio_path = os.path.join(settings.MEDIA_ROOT, "article_audio", filename)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    # Generate TTS
    tts = gTTS(full_text, lang="en")
    tts.save(audio_path)

    # Update article field
    article.audio_file = os.path.join("article_audio", filename)
    article.save()

    return article.audio_file
