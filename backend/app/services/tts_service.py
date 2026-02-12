import httpx
import base64
import struct
import logging
import os
import asyncio
import subprocess
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

STATIC_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "../../static/audio")


class TTSService:
    """Text-to-Speech service using Gemini 2.5 Pro TTS API"""

    TTS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-tts:generateContent"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
        self._welcome_media_id: Optional[str] = None
        os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def generate_audio(self, text: str, voice: str = "Leda") -> Optional[bytes]:
        """Generate audio from text using Gemini TTS. Returns raw PCM16 bytes."""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set, TTS disabled")
            return None

        url = f"{self.TTS_ENDPOINT}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": voice}
                    }
                }
            }
        }

        try:
            client = self._get_client()
            response = await client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            pcm_data = base64.b64decode(audio_b64)
            logger.info(f"TTS generated {len(pcm_data)} bytes of audio")
            return pcm_data
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    @staticmethod
    def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bit_depth: int = 16) -> bytes:
        """Convert raw PCM16 to WAV format (pure Python, no ffmpeg needed)"""
        byte_rate = sample_rate * channels * (bit_depth // 8)
        block_align = channels * (bit_depth // 8)
        data_size = len(pcm_data)

        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size, b'WAVE',
            b'fmt ', 16, 1, channels,
            sample_rate, byte_rate, block_align, bit_depth,
            b'data', data_size
        )
        return header + pcm_data

    async def generate_wav_file(self, text: str, output_path: str, voice: str = "Leda") -> Optional[str]:
        """Generate and save a WAV audio file. Returns file path or None."""
        pcm_data = await self.generate_audio(text, voice)
        if not pcm_data:
            return None

        wav_data = self.pcm_to_wav(pcm_data)
        with open(output_path, 'wb') as f:
            f.write(wav_data)

        logger.info(f"WAV file saved: {output_path} ({len(wav_data)} bytes)")
        return output_path

    @staticmethod
    def wav_to_ogg(wav_path: str, ogg_path: str) -> Optional[str]:
        """Convert WAV to OGG Opus using ffmpeg (required for WhatsApp)"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libopus", "-b:a", "64k", ogg_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0 and os.path.exists(ogg_path):
                logger.info(f"Converted to OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")
                return ogg_path
            logger.error(f"ffmpeg conversion failed: {result.stderr.decode()}")
            return None
        except Exception as e:
            logger.error(f"WAV to OGG conversion error: {e}")
            return None

    async def generate_and_upload(self, text: str, voice: str = "Leda") -> Optional[str]:
        """Generate TTS audio and upload to WhatsApp, returning media_id"""
        from app.services.whatsapp_service import whatsapp_service

        temp_wav = os.path.join(STATIC_AUDIO_DIR, "temp_tts.wav")
        temp_ogg = os.path.join(STATIC_AUDIO_DIR, "temp_tts.ogg")
        result = await self.generate_wav_file(text, temp_wav, voice)
        if not result:
            return None

        ogg_path = self.wav_to_ogg(temp_wav, temp_ogg)
        if not ogg_path:
            return None

        media_id = await whatsapp_service.upload_media(ogg_path, "audio/ogg")

        for f in [temp_wav, temp_ogg]:
            try:
                os.remove(f)
            except Exception:
                pass

        return media_id

    async def get_welcome_media_id(self) -> Optional[str]:
        """Get or generate the cached welcome audio media_id"""
        if self._welcome_media_id:
            return self._welcome_media_id

        from app.services.whatsapp_service import whatsapp_service

        welcome_wav = os.path.join(STATIC_AUDIO_DIR, "welcome.wav")
        welcome_ogg = os.path.join(STATIC_AUDIO_DIR, "welcome.ogg")

        if not os.path.exists(welcome_ogg):
            welcome_text = (
                "Say in a warm, friendly Lebanese Arabic accent: "
                "أهلا وسهلا فيك بليون ديليفري! "
                "عنا أكتر من مية مطعم ومحل بصيدا. "
                "ليون ديليفري بخدمتك، اطلب يلي بدك ياه ونحنا منوصلك ياه لعندك! "
                "أطيب أكل بأسرع وقت!"
            )
            result = await self.generate_wav_file(welcome_text, welcome_wav)
            if not result:
                logger.error("Failed to generate welcome audio")
                return None
            ogg_result = self.wav_to_ogg(welcome_wav, welcome_ogg)
            if not ogg_result:
                logger.error("Failed to convert welcome audio to OGG")
                return None

        self._welcome_media_id = await whatsapp_service.upload_media(welcome_ogg, "audio/ogg")
        if self._welcome_media_id:
            logger.info(f"Welcome audio ready, media_id: {self._welcome_media_id}")
        return self._welcome_media_id

    def invalidate_welcome_cache(self):
        """Invalidate cached welcome media_id (e.g. after 30 days expiry)"""
        self._welcome_media_id = None

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


tts_service = TTSService()
