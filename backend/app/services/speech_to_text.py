from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
from loguru import logger
import assemblyai as aai
from openai import OpenAI

from app.core.config import settings


class SpeechToTextService:
    """
    Service for converting audio/video to text using various providers
    """

    def __init__(self, provider: str = "assemblyai"):
        """
        Initialize speech-to-text service

        Args:
            provider: 'assemblyai' or 'whisper'
        """
        self.provider = provider

        if provider == "assemblyai":
            aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        elif provider == "whisper":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def transcribe(
        self,
        audio_file_path: str,
        speaker_diarization: bool = True,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text

        Args:
            audio_file_path: Path to audio file
            speaker_diarization: Enable speaker identification
            language: Language code (e.g., 'en', 'es')

        Returns:
            Dictionary containing:
            - full_transcript: Complete transcript text
            - segments: List of speaker segments with timestamps
            - num_speakers: Number of distinct speakers detected
            - language: Detected language
            - confidence: Overall confidence score
        """
        logger.info(f"Transcribing audio file: {audio_file_path}")

        if self.provider == "assemblyai":
            return self._transcribe_assemblyai(
                audio_file_path, speaker_diarization, language
            )
        elif self.provider == "whisper":
            return self._transcribe_whisper(
                audio_file_path, speaker_diarization, language
            )

    def _transcribe_assemblyai(
        self,
        audio_file_path: str,
        speaker_diarization: bool = True,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe using AssemblyAI (best for speaker diarization)
        """
        config = aai.TranscriptionConfig(
            speaker_labels=speaker_diarization,
            language_code=language,
            punctuate=True,
            format_text=True,
        )

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file_path, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"Transcription failed: {transcript.error}")
            raise Exception(f"Transcription failed: {transcript.error}")

        # Process results
        full_transcript = transcript.text
        segments = []

        if speaker_diarization and transcript.utterances:
            for utterance in transcript.utterances:
                segments.append(
                    {
                        "speaker_id": f"Speaker {utterance.speaker}",
                        "text": utterance.text,
                        "start_time": utterance.start / 1000.0,  # Convert ms to seconds
                        "end_time": utterance.end / 1000.0,
                        "confidence": utterance.confidence,
                    }
                )

        # Count unique speakers
        num_speakers = len(set(s["speaker_id"] for s in segments)) if segments else 1

        return {
            "full_transcript": full_transcript,
            "segments": segments,
            "num_speakers": num_speakers,
            "language": transcript.language_code or "en",
            "confidence": transcript.confidence or 0.0,
            "duration_seconds": transcript.audio_duration or 0,
        }

    def _transcribe_whisper(
        self,
        audio_file_path: str,
        speaker_diarization: bool = True,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe using OpenAI Whisper API
        (Note: Whisper API doesn't support speaker diarization natively)
        """
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language=language,
            )

        # Whisper doesn't provide speaker diarization
        # You'd need to use a separate service like pyannote for this
        segments = []
        if hasattr(transcript_response, "segments"):
            for segment in transcript_response.segments:
                segments.append(
                    {
                        "speaker_id": "Speaker 1",  # Whisper doesn't identify speakers
                        "text": segment["text"],
                        "start_time": segment["start"],
                        "end_time": segment["end"],
                        "confidence": 0.0,  # Whisper doesn't provide word-level confidence
                    }
                )

        return {
            "full_transcript": transcript_response.text,
            "segments": segments,
            "num_speakers": 1,  # Can't detect multiple speakers with Whisper alone
            "language": transcript_response.language or "en",
            "confidence": 0.0,
            "duration_seconds": transcript_response.duration,
        }

    def transcribe_from_url(
        self,
        audio_url: str,
        speaker_diarization: bool = True,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio from URL

        Args:
            audio_url: Public URL to audio file
            speaker_diarization: Enable speaker identification
            language: Language code

        Returns:
            Transcription results
        """
        logger.info(f"Transcribing audio from URL: {audio_url}")

        if self.provider == "assemblyai":
            config = aai.TranscriptionConfig(
                speaker_labels=speaker_diarization,
                language_code=language,
                punctuate=True,
                format_text=True,
            )

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_url, config=config)

            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")

            return self._process_assemblyai_result(transcript, speaker_diarization)

        else:
            raise NotImplementedError(
                "URL transcription only supported for AssemblyAI"
            )

    def _process_assemblyai_result(
        self, transcript, speaker_diarization: bool
    ) -> Dict[str, Any]:
        """
        Process AssemblyAI transcript result into standard format
        """
        full_transcript = transcript.text
        segments = []

        if speaker_diarization and transcript.utterances:
            for utterance in transcript.utterances:
                segments.append(
                    {
                        "speaker_id": f"Speaker {utterance.speaker}",
                        "text": utterance.text,
                        "start_time": utterance.start / 1000.0,
                        "end_time": utterance.end / 1000.0,
                        "confidence": utterance.confidence,
                    }
                )

        num_speakers = len(set(s["speaker_id"] for s in segments)) if segments else 1

        return {
            "full_transcript": full_transcript,
            "segments": segments,
            "num_speakers": num_speakers,
            "language": transcript.language_code or "en",
            "confidence": transcript.confidence or 0.0,
            "duration_seconds": transcript.audio_duration or 0,
        }
