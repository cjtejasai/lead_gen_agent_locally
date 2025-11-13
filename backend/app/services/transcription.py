"""
Transcription service using OpenAI Whisper
Handles audio transcription without diarization for now
"""

import whisper
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


class TranscriptionService:
    """Whisper-based transcription service"""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       base is good balance of speed/accuracy for demo
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Transcription service initialized with device: {self.device}")

    def _load_model(self):
        """Lazy load model when first needed"""
        if self.model is None:
            logger.info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded successfully")

    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with transcription results:
            {
                'text': 'full transcript',
                'language': 'en',
                'segments': [{'start': 0.0, 'end': 1.5, 'text': '...'}],
                'duration': 60.0
            }
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self._load_model()

        logger.info(f"Transcribing: {audio_path}")

        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language="en",  # Can be auto-detected by removing this
                task="transcribe",  # vs "translate"
                fp16=False  # Use FP32 for CPU compatibility
            )

            # Extract segments with timestamps
            segments = []
            for seg in result.get("segments", []):
                segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                    "confidence": seg.get("no_speech_prob", 0.0)
                })

            transcription = {
                "text": result["text"].strip(),
                "language": result.get("language", "en"),
                "segments": segments,
                "duration": segments[-1]["end"] if segments else 0.0
            }

            logger.info(f"Transcription completed: {len(transcription['text'])} chars, "
                       f"{len(segments)} segments")

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service(model_size: str = "base") -> TranscriptionService:
    """Get or create transcription service instance"""
    global _transcription_service

    if _transcription_service is None:
        _transcription_service = TranscriptionService(model_size=model_size)

    return _transcription_service