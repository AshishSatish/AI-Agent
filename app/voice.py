"""Voice interaction module for speech-to-text and text-to-speech"""

import speech_recognition as sr
import pyttsx3
from typing import Optional
import threading


class VoiceInterface:
    """Handle voice input and output"""

    def __init__(self):
        """Initialize voice interface"""
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume (0-1)

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen to microphone and convert speech to text

        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for phrase

        Returns:
            Transcribed text or None if failed
        """
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            print("Processing speech...")

            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")

            return text

        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return None

    def speak(self, text: str, async_mode: bool = False):
        """
        Convert text to speech

        Args:
            text: Text to speak
            async_mode: If True, speak in background thread
        """
        if async_mode:
            # Speak in background
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
        else:
            self._speak_sync(text)

    def _speak_sync(self, text: str):
        """Synchronous speech (internal method)"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error during speech synthesis: {e}")

    def set_voice(self, voice_id: int = 0):
        """
        Set the voice to use

        Args:
            voice_id: Index of voice to use (0 for first voice, 1 for second, etc.)
        """
        voices = self.tts_engine.getProperty('voices')
        if 0 <= voice_id < len(voices):
            self.tts_engine.setProperty('voice', voices[voice_id].id)

    def set_rate(self, rate: int = 150):
        """
        Set speech rate

        Args:
            rate: Words per minute (default 150)
        """
        self.tts_engine.setProperty('rate', rate)

    def set_volume(self, volume: float = 0.9):
        """
        Set speech volume

        Args:
            volume: Volume level 0.0 to 1.0
        """
        self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))

    def interactive_conversation(self, agent, exit_phrases=None):
        """
        Run an interactive voice conversation

        Args:
            agent: ConversationalAgent instance
            exit_phrases: List of phrases that exit the conversation
        """
        if exit_phrases is None:
            exit_phrases = ["exit", "quit", "goodbye", "stop"]

        self.speak("Hello! I'm your Company Research Assistant. How can I help you today?")

        while True:
            # Listen for user input
            user_input = self.listen()

            if not user_input:
                self.speak("I didn't catch that. Could you please repeat?")
                continue

            # Check for exit phrases
            if any(phrase in user_input.lower() for phrase in exit_phrases):
                self.speak("Goodbye! Have a great day!")
                break

            # Get response from agent
            response = agent.get_response(user_input)

            # Speak the response
            self.speak(response, async_mode=False)


# CLI interface for voice mode
def run_voice_mode():
    """Run the assistant in voice mode"""
    from app.config import get_settings
    from app.agent import ConversationalAgent

    settings = get_settings()

    # Initialize components
    agent = ConversationalAgent(
        api_key=settings.groq_api_key,
        model=settings.groq_model
    )

    voice = VoiceInterface()

    print("\n" + "=" * 50)
    print("Company Research Assistant - Voice Mode")
    print("=" * 50)
    print("\nStarting voice interface...")
    print("Say 'exit', 'quit', or 'goodbye' to end the conversation.\n")

    try:
        voice.interactive_conversation(agent)
    except KeyboardInterrupt:
        print("\n\nSession ended by user.")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    run_voice_mode()
