import httpx
import base64
import struct
import logging
import os
import asyncio
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

STATIC_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "../../static/audio")


class TTSService:
    """Text-to-Speech service using Gemini 2.5 Flash TTS API"""

    TTS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
        self._welcome_media_id: Optional[str] = None
        os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def generate_audio(self, text: str, voice: str = "Kore") -> Optional[bytes]:
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

    async def generate_wav_file(self, text: str, output_path: str, voice: str = "Kore") -> Optional[str]:
        """Generate and save a WAV audio file. Returns file path or None."""
        pcm_data = await self.generate_audio(text, voice)
        if not pcm_data:
            return None

        wav_data = self.pcm_to_wav(pcm_data)
        with open(output_path, 'wb') as f:
            f.write(wav_data)

        logger.info(f"WAV file saved: {output_path} ({len(wav_data)} bytes)")
        return output_path

    async def generate_and_upload(self, text: str, voice: str = "Kore") -> Optional[str]:
        """Generate TTS audio and upload to WhatsApp, returning media_id"""
        from app.services.whatsapp_service import whatsapp_service

        temp_path = os.path.join(STATIC_AUDIO_DIR, "temp_tts.wav")
        result = await self.generate_wav_file(text, temp_path, voice)
        if not result:
            return None

        media_id = await whatsapp_service.upload_media(temp_path, "audio/wav")

        try:
            os.remove(temp_path)
        except Exception:
            pass

        return media_id

    async def get_welcome_media_id(self) -> Optional[str]:
        """Get or generate the cached welcome audio media_id"""
        if self._welcome_media_id:
            return self._welcome_media_id

        from app.services.whatsapp_service import whatsapp_service

        welcome_path = os.path.join(STATIC_AUDIO_DIR, "welcome.wav")

        if not os.path.exists(welcome_path):
            welcome_text = (
                "أهلا وسهلا فيك بليون ديليفري! "
                "عنا أكتر من مية مطعم ومحل بصيدا. "
                "ليون ديليفري بخدمتك، اطلب يلي بدك ياه ونحنا منوصلك ياه لعندك! "
                "أطيب أكل بأسرع وقت!"
            )
            result = await self.generate_wav_file(welcome_text, welcome_path)
            if not result:
                logger.error("Failed to generate welcome audio")
                return None

        self._welcome_media_id = await whatsapp_service.upload_media(welcome_path, "audio/wav")
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
