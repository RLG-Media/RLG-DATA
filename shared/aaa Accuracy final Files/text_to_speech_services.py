import os
import logging
from typing import Optional, Dict
from gtts import gTTS  # Google Text-to-Speech
from pydub import AudioSegment  # For audio processing
from pydub.playback import play  # For audio playback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("text_to_speech.log"),
        logging.StreamHandler()
    ]
)

class TextToSpeechService:
    """
    Text-to-Speech (TTS) service for RLG Data and RLG Fans.
    Converts text into audio using Google TTS and supports multiple languages.
    """

    def __init__(self, output_directory: str = "tts_output"):
        """
        Initialize the TextToSpeechService.

        Args:
            output_directory (str): Directory to save generated audio files.
        """
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
        logging.info("TextToSpeechService initialized with output directory: %s", output_directory)

    def convert_text_to_speech(self, text: str, language: str = "en", filename: Optional[str] = None) -> str:
        """
        Convert text into speech and save as an audio file.

        Args:
            text (str): The text to convert into speech.
            language (str): The language code for the TTS (default: "en").
            filename (Optional[str]): The name of the output audio file. Auto-generated if not provided.

        Returns:
            str: Path to the saved audio file.
        """
        try:
            if not text.strip():
                raise ValueError("Input text cannot be empty.")

            filename = filename or f"tts_{hash(text)}.mp3"
            file_path = os.path.join(self.output_directory, filename)

            tts = gTTS(text=text, lang=language)
            tts.save(file_path)

            logging.info("TTS conversion successful. File saved at: %s", file_path)
            return file_path
        except Exception as e:
            logging.error("Error during TTS conversion: %s", e)
            raise

    def play_audio(self, file_path: str):
        """
        Play an audio file.

        Args:
            file_path (str): Path to the audio file.
        """
        try:
            audio = AudioSegment.from_file(file_path)
            play(audio)
            logging.info("Playing audio: %s", file_path)
        except Exception as e:
            logging.error("Error playing audio file: %s", e)
            raise

    def generate_social_media_summary_audio(self, summaries: Dict[str, str], language: str = "en") -> Dict[str, str]:
        """
        Generate audio summaries for social media platforms.

        Args:
            summaries (Dict[str, str]): A dictionary where keys are platform names and values are summary texts.
            language (str): The language code for the TTS (default: "en").

        Returns:
            Dict[str, str]: A dictionary where keys are platform names and values are paths to audio files.
        """
        audio_files = {}
        for platform, summary in summaries.items():
            try:
                logging.info("Generating TTS for platform: %s", platform)
                audio_path = self.convert_text_to_speech(text=summary, language=language, filename=f"{platform}_summary.mp3")
                audio_files[platform] = audio_path
            except Exception as e:
                logging.error("Failed to generate TTS for %s: %s", platform, e)
        return audio_files

# Example usage
if __name__ == "__main__":
    tts_service = TextToSpeechService()

    # Example: Convert simple text to speech
    text = "Welcome to RLG Data and RLG Fans! Empowering your insights."
    audio_file = tts_service.convert_text_to_speech(text, language="en")
    tts_service.play_audio(audio_file)

    # Example: Generate social media summaries
    summaries = {
        "Twitter": "Your Twitter engagement increased by 15% this week.",
        "Facebook": "Your Facebook page received 300 new likes.",
        "Instagram": "Your Instagram posts reached 5,000 users this week."
    }
    audio_summaries = tts_service.generate_social_media_summary_audio(summaries, language="en")
    logging.info("Generated audio summaries: %s", audio_summaries)
