"""
Transcription service using OpenAI Whisper + pyannote for speaker diarization
"""

import whisper
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
import os
import subprocess
import tempfile


class TranscriptionService:
    """Whisper-based transcription service with speaker diarization"""

    def __init__(self, model_size: str = "base", enable_diarization: bool = True):
        """
        Initialize Whisper model and optionally pyannote diarization

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            enable_diarization: Enable speaker diarization with pyannote
        """
        self.model_size = model_size
        self.model = None
        self.diarization_pipeline = None
        self.enable_diarization = enable_diarization
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Transcription service initialized with device: {self.device}")

        # Load diarization if enabled
        if enable_diarization:
            self._load_diarization()

    def _load_model(self):
        """Lazy load model when first needed"""
        if self.model is None:
            logger.info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded successfully")

    def _load_diarization(self):
        """Load pyannote diarization pipeline"""
        try:
            from pyannote.audio import Pipeline

            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                logger.warning("HF_TOKEN not found, speaker diarization disabled")
                logger.warning("Get token from https://huggingface.co/settings/tokens")
                logger.warning("Accept license at https://huggingface.co/pyannote/speaker-diarization-3.1")
                self.enable_diarization = False
                return

            logger.info("Loading pyannote speaker diarization model...")
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )

            if self.device == "cuda":
                self.diarization_pipeline.to(torch.device("cuda"))

            logger.info("Speaker diarization loaded successfully")
        except Exception as e:
            logger.error(f"Could not load diarization model: {e}")
            logger.warning("Continuing without speaker diarization")
            self.enable_diarization = False

    def _convert_to_wav(self, audio_path: Path) -> Path:
        """
        Convert audio file to 16kHz mono WAV for optimal Whisper processing

        Args:
            audio_path: Path to input audio file

        Returns:
            Path to converted WAV file (or original if already WAV)
        """
        # If already WAV, check sample rate
        if str(audio_path).endswith('.wav'):
            return audio_path

        # Convert webm/mp3/m4a to WAV
        logger.info(f"Converting {audio_path.suffix} to 16kHz mono WAV...")
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav.close()

        try:
            subprocess.run([
                'ffmpeg', '-i', str(audio_path),
                '-ar', '16000',  # 16kHz sample rate (Whisper optimal)
                '-ac', '1',       # Mono channel
                '-y',             # Overwrite output
                temp_wav.name
            ], check=True, capture_output=True, text=True)

            logger.info(f"Converted to WAV: {temp_wav.name}")
            return Path(temp_wav.name)
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio conversion failed: {e.stderr}")
            raise RuntimeError(f"Failed to convert audio: {e.stderr}")

    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribe audio file with optional speaker diarization

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with transcription results:
            {
                'text': 'full transcript',
                'language': 'en',
                'segments': [{'start': 0.0, 'end': 1.5, 'text': '...', 'speaker': 'SPEAKER_00'}],
                'duration': 60.0,
                'num_speakers': 2
            }
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self._load_model()

        logger.info(f"Transcribing: {audio_path}")

        # Convert to WAV if needed
        converted_path = None
        try:
            audio_file_to_use = self._convert_to_wav(audio_path)
            if audio_file_to_use != audio_path:
                converted_path = audio_file_to_use
        except Exception as e:
            logger.warning(f"Conversion failed, using original file: {e}")
            audio_file_to_use = audio_path

        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_file_to_use),
                language="en",
                task="transcribe",
                fp16=False
            )

            # Get speaker diarization if enabled
            speaker_segments = {}
            if self.enable_diarization and self.diarization_pipeline:
                try:
                    logger.info("Running speaker diarization...")
                    diarization = self.diarization_pipeline(str(audio_path))

                    # Map time ranges to speakers
                    for segment, _, speaker in diarization.itertracks(yield_label=True):
                        speaker_segments[(segment.start, segment.end)] = speaker

                    logger.info(f"Diarization found {len(set(speaker_segments.values()))} speakers")
                except Exception as e:
                    logger.error(f"Diarization failed: {e}")

            # Extract segments with timestamps and speakers
            segments = []
            for seg in result.get("segments", []):
                # Find speaker for this segment
                speaker = "SPEAKER_00"  # Default
                if speaker_segments:
                    seg_start = seg["start"]
                    seg_end = seg["end"]

                    # Find overlapping speaker segment
                    for (start, end), spk in speaker_segments.items():
                        if start <= seg_start <= end or start <= seg_end <= end:
                            speaker = spk
                            break

                segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                    "speaker": speaker,
                    "confidence": seg.get("no_speech_prob", 0.0)
                })

            # Count unique speakers
            unique_speakers = len(set(seg["speaker"] for seg in segments))

            transcription = {
                "text": result["text"].strip(),
                "language": result.get("language", "en"),
                "segments": segments,
                "duration": segments[-1]["end"] if segments else 0.0,
                "num_speakers": unique_speakers
            }

            logger.info(f"Transcription completed: {len(transcription['text'])} chars, "
                       f"{len(segments)} segments, {unique_speakers} speakers")

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
        finally:
            # Clean up temporary WAV file if created
            if converted_path and converted_path.exists():
                try:
                    converted_path.unlink()
                    logger.info(f"Cleaned up temporary WAV: {converted_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temporary WAV: {e}")


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service(model_size: str = "base", enable_diarization: bool = True) -> TranscriptionService:
    """Get or create transcription service instance"""
    global _transcription_service

    if _transcription_service is None:
        _transcription_service = TranscriptionService(
            model_size=model_size,
            enable_diarization=enable_diarization
        )

    return _transcription_service