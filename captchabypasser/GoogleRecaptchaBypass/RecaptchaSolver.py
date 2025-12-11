import os
import urllib.request
import random
import pydub
import pydub.exceptions
import speech_recognition
import time
from typing import Optional
from DrissionPage import ChromiumPage

# Set the path to ffmpeg for pydub
try:
    import platform
    if platform.system() == "Windows":
        # For Windows, try common conda/pip installation paths
        ffmpeg_path = os.environ.get('CONDA_PREFIX', '') + r'\Library\bin\ffmpeg.exe'
        if os.path.exists(ffmpeg_path):
            pydub.AudioSegment.converter = ffmpeg_path

        # Also check if ffmpeg is in PATH
        import shutil
        if shutil.which('ffmpeg'):
            pydub.AudioSegment.converter = 'ffmpeg'
        if shutil.which('ffprobe'):
            pydub.AudioSegment.ffmpeg = 'ffprobe'
except:
    pass  # If this fails, pydub will use its default behavior


class RecaptchaSolver:
    """A class to solve reCAPTCHA challenges using audio recognition."""

    # Constants
    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 7
    TIMEOUT_SHORT = 1
    TIMEOUT_DETECTION = 0.05

    def __init__(self, driver: ChromiumPage) -> None:
        """Initialize the solver with a ChromiumPage driver.

        Args:
            driver: ChromiumPage instance for browser interaction
        """
        self.driver = driver

    def solveCaptcha(self) -> None:
        """Attempt to solve the reCAPTCHA challenge.

        Raises:
            Exception: If captcha solving fails or bot is detected
        """
        print("Starting reCAPTCHA solving process...")

        # Handle main reCAPTCHA iframe
        self.driver.wait.ele_displayed(
            "@title=reCAPTCHA", timeout=self.TIMEOUT_STANDARD
        )
        time.sleep(0.1)
        iframe_inner = self.driver("@title=reCAPTCHA")

        # Click the checkbox
        print("Locating and clicking the reCAPTCHA checkbox...")
        iframe_inner.wait.ele_displayed(
            ".rc-anchor-content", timeout=self.TIMEOUT_STANDARD
        )
        checkbox_element = iframe_inner(".rc-anchor-content", timeout=self.TIMEOUT_SHORT)
        print(f"Checkbox element found: {checkbox_element}")
        checkbox_element.click()
        time.sleep(1)  # Wait longer after clicking

        # Check if solved by just clicking
        print("Checking if captcha was solved by clicking checkbox...")
        if self.is_solved():
            print("Captcha was solved just by clicking the checkbox!")
            return

        print("Captcha not solved by clicking, proceeding to audio challenge...")

        # Handle audio challenge - First click the audio button to switch to audio mode
        iframe = self.driver("xpath://iframe[contains(@title, 'recaptcha')]")
        print("Attempting to locate the audio switch button...")

        # Click the audio button to switch from image to audio challenge
        # From your HTML: <button class="rc-button goog-inline-block rc-button-audio" title="Get an audio challenge" value="" id="recaptcha-audio-button" tabindex="0"></button>
        try:
            iframe.wait.ele_displayed("#recaptcha-audio-button", timeout=self.TIMEOUT_STANDARD)
            audio_switch_button = iframe("#recaptcha-audio-button", timeout=self.TIMEOUT_SHORT)
            print("Found audio switch button, clicking it to switch to audio challenge...")
            audio_switch_button.click()
            time.sleep(1)  # Wait for audio challenge to load
        except:
            print("Audio switch button not found, might already be in audio mode or different challenge type")
            # Continue and look for the audio interface elements

        # Now look for the PLAY button in the audio interface
        print("Looking for the PLAY button in audio challenge...")
        try:
            # Wait for PLAY button to appear (it might take a moment after clicking audio button)
            iframe.wait.ele_displayed("button:contains('PLAY')", timeout=self.TIMEOUT_STANDARD)
            play_button = iframe("button:contains('PLAY')", timeout=self.TIMEOUT_SHORT)
            print("Found PLAY button, clicking it...")
            play_button.click()
            time.sleep(1)  # Give time for audio to potentially play
        except:
            print("PLAY button not found, checking if audio is already loaded...")
            # Check if audio source is available without clicking play
            try:
                iframe.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
                print("Audio source found without needing to click PLAY")
            except:
                raise Exception("Could not find audio challenge interface after switching to audio mode")

        time.sleep(0.3)

        if self.is_detected():
            raise Exception("Captcha detected bot behavior")

        print("Locating audio source...")
        # Based on the HTML, the audio source has id 'audio-source'
        try:
            iframe.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
            audio_source = iframe("#audio-source")
            print("Found audio source element")
        except:
            raise Exception("Could not find audio source")

        src = audio_source.attrs["src"] if "src" in audio_source.attrs else None
        if not src:
            raise Exception("Could not get audio source URL")

        print(f"Found audio source URL: {src[:50]}...")  # Print first 50 chars

        try:
            print("Processing audio challenge...")
            text_response = self._process_audio_challenge(src)
            print(f"Audio recognition result: {text_response}")

            # Based on the HTML, the response input has id 'audio-response'
            try:
                response_input = iframe("#audio-response")
            except:
                raise Exception("Could not find audio response input field")

            response_input.input(text_response.lower())

            # Based on the HTML, the verify button has id 'recaptcha-verify-button'
            try:
                verify_button = iframe("#recaptcha-verify-button")
            except:
                raise Exception("Could not find verify button")

            print("Clicking verify button...")
            verify_button.click()
            time.sleep(0.4)

            if not self.is_solved():
                print("Captcha not solved, checking for additional challenges...")
                # The audio challenge might have multiple parts or need verification retries
                # Sometimes reCAPTCHA needs time to update its internal state after verification
                for i in range(5):  # Try multiple times to see if it gets solved
                    time.sleep(1)
                    if self.is_solved():
                        print("Captcha solved after waiting!")
                        return
                    # Check if we need to process another audio challenge
                    try:
                        # Check if the response field still exists (indicating more challenges)
                        next_audio_source = iframe("#audio-source", timeout=0.5)
                        if next_audio_source:
                            print("Found another audio challenge, processing...")
                            # Process the next audio segment
                            src = next_audio_source.attrs["src"]
                            text_response = self._process_audio_challenge(src)
                            response_input = iframe("#audio-response")
                            response_input.input(text_response.lower())
                            verify_button = iframe("#recaptcha-verify-button")
                            verify_button.click()
                    except:
                        # If there's no next audio source, continue waiting
                        continue

                # Final check if captcha is solved
                if self.is_solved():
                    print("Captcha solved after additional attempts!")
                    return
                else:
                    # Sometimes recognition fails, so we can try to reprocess
                    print("Captcha still not solved. The recognized text may have been incorrect.")
                    print("This can happen due to audio quality or recognition accuracy.")
                    raise Exception("Failed to solve the captcha after processing audio")

        except Exception as e:
            print(f"Full error traceback: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise Exception(f"Audio challenge failed: {str(e)}")

    def _process_audio_challenge(self, audio_url: str) -> str:
        """Process the audio challenge and return the recognized text.

        Args:
            audio_url: URL of the audio file to process

        Returns:
            str: Recognized text from the audio file
        """
        # Import required modules at the beginning to avoid scoping issues
        import os
        import subprocess
        import platform

        # Ensure ffmpeg is properly set for pydub
        if platform.system() == "Windows":
            # Add conda bin directory to PATH to make ffmpeg and ffprobe accessible
            conda_bin_path = r"C:\Users\ahmed\anaconda3\Library\bin"
            if os.path.exists(conda_bin_path):
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = conda_bin_path + os.pathsep + current_path
                print(f"Added {conda_bin_path} to system PATH")

            # Check and set paths
            conda_ffmpeg_path = os.path.join(conda_bin_path, "ffmpeg.exe")
            conda_ffprobe_path = os.path.join(conda_bin_path, "ffprobe.exe")

            if os.path.exists(conda_ffmpeg_path):
                pydub.AudioSegment.converter = conda_ffmpeg_path
                print(f"Set ffmpeg path to: {conda_ffmpeg_path}")

            if os.path.exists(conda_ffprobe_path):
                pydub.AudioSegment.ffprobe = conda_ffprobe_path  # Correct attribute name
                print(f"Set ffprobe path to: {conda_ffprobe_path}")

        mp3_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.mp3")
        wav_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.wav")

        try:
            print(f"Downloading audio from: {audio_url}")
            urllib.request.urlretrieve(audio_url, mp3_path)
            print(f"Downloaded audio to: {mp3_path}")

            print("Converting MP3 to WAV...")
            try:
                sound = pydub.AudioSegment.from_mp3(mp3_path)
                sound.export(wav_path, format="wav")
                print("Audio conversion completed using pydub")
            except Exception as pydub_error:
                print(f"Pydub conversion failed: {pydub_error}")
                print("Attempting direct ffmpeg conversion...")

                # Fallback: Direct ffmpeg call
                result = subprocess.run(
                    [
                        conda_ffmpeg_path,
                        "-i", mp3_path,
                        "-acodec", "pcm_s16le",
                        "-ar", "16000",
                        "-ac", "1",
                        wav_path
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

                print("Audio conversion completed using direct ffmpeg call")

            print("Performing speech recognition...")
            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            result = recognizer.recognize_google(audio)
            print(f"Speech recognition result: {result}")
            return result

        except Exception as e:
            print(f"Error in audio processing: {e}")
            # Print the system PATH to help debug
            print(f"System PATH: {os.environ.get('PATH', 'Not found')}")
            if hasattr(pydub.AudioSegment, 'converter'):
                print(f"pydub converter path: {pydub.AudioSegment.converter}")
            raise e

        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"Cleaned up temporary file: {path}")
                    except OSError:
                        pass

    def is_solved(self) -> bool:
        """Check if the captcha has been solved successfully."""
        try:
            return (
                "style"
                in self.driver.ele(
                    ".recaptcha-checkbox-checkmark", timeout=self.TIMEOUT_SHORT
                ).attrs
            )
        except Exception:
            return False

    def is_detected(self) -> bool:
        """Check if the bot has been detected."""
        try:
            return (
                self.driver.ele("Try again later", timeout=self.TIMEOUT_DETECTION)
                .states()
                .is_displayed
            )
        except Exception:
            return False

    def get_token(self) -> Optional[str]:
        """Get the reCAPTCHA token if available."""
        try:
            return self.driver.ele("#recaptcha-token").attrs["value"]
        except Exception:
            return None