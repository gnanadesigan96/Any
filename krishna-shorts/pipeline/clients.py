"""Small API clients for ElevenLabs and the Gemini API (images + Veo). Standard library only."""
import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


class ApiError(Exception):
    def __init__(self, status, body, url=""):
        super().__init__(f"HTTP {status} from {url}: {body[:500]}")
        self.status = status
        self.body = body


def _request(method, url, headers, data=None, timeout=300):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode("utf-8", "replace"), url.split("?")[0])


def multipart(fields, files):
    """fields: {name: str}; files: {name: path}. Returns (body, content_type)."""
    boundary = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out += [f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode(),
                str(v).encode("utf-8"), b"\r\n"]
    for k, path in files.items():
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            data = f.read()
        out += [f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{k}"; filename="{os.path.basename(path)}"\r\n'.encode(),
                f"Content-Type: {ctype}\r\n\r\n".encode(), data, b"\r\n"]
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


# ---------------------------------------------------------------- ElevenLabs
class ElevenLabs:
    BASE = "https://api.elevenlabs.io"

    def __init__(self, key):
        self.key = key
        self._voices = None

    def _h(self, extra=None):
        h = {"xi-api-key": self.key}
        h.update(extra or {})
        return h

    def get_json(self, path):
        body, _ = _request("GET", self.BASE + path, self._h({"Accept": "application/json"}))
        return json.loads(body)

    def post_json(self, path, payload, want="json"):
        body, _ = _request("POST", self.BASE + path, self._h({"Content-Type": "application/json"}),
                           json.dumps(payload).encode("utf-8"))
        return json.loads(body) if want == "json" else body

    def post_files(self, path, fields, files):
        data, ctype = multipart(fields, files)
        body, _ = _request("POST", self.BASE + path, self._h({"Content-Type": ctype}), data)
        return body

    def linked(self):
        """Voices linked by hand (e.g. from the Voice Library): pipeline/voice_map.json {"KK_Kannan": "<voice_id>"}."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_map.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def voice_id(self, name):
        mapped = self.linked().get(name)
        if mapped:
            return mapped
        if self._voices is None:
            self._voices = {v["name"]: v["voice_id"] for v in self.get_json("/v1/voices").get("voices", [])}
        if name not in self._voices:
            raise KeyError(f"Voice '{name}' not found. Design it (python kk.py voices) or link one: "
                           f"python kk.py link {name} <voice_id>")
        return self._voices[name]

    def tts(self, voice_name, text, model="eleven_v3"):
        vid = self.voice_id(voice_name)
        q = "?output_format=mp3_44100_192"
        try:
            return self.post_json(f"/v1/text-to-speech/{vid}{q}",
                                  {"text": text, "model_id": model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
                                  want="bytes")
        except ApiError as e:
            if model == "eleven_v3" and e.status in (400, 422):
                # v2 does not understand [tags]: strip them
                import re
                plain = re.sub(r"\[[^\]]*\]\s*", "", text)
                return self.post_json(f"/v1/text-to-speech/{vid}{q}",
                                      {"text": plain, "model_id": "eleven_multilingual_v2",
                                       "voice_settings": {"stability": 0.4, "similarity_boost": 0.75, "style": 0.4}},
                                      want="bytes")
            raise

    def sound_effect(self, prompt, seconds):
        return self.post_json("/v1/sound-generation?output_format=mp3_44100_192",
                              {"text": prompt, "duration_seconds": max(0.5, min(22, seconds)), "prompt_influence": 0.5},
                              want="bytes")

    def music(self, prompt, seconds):
        return self.post_json("/v1/music?output_format=mp3_44100_192",
                              {"prompt": prompt + ". Instrumental only, no vocals.",
                               "music_length_ms": int(max(10, seconds) * 1000), "model_id": "music_v1"},
                              want="bytes")

    def isolate(self, audio_path):
        return self.post_files("/v1/audio-isolation", {}, {"audio": audio_path})

    def voice_change(self, voice_name, audio_path):
        vid = self.voice_id(voice_name)
        return self.post_files(f"/v1/speech-to-speech/{vid}?output_format=mp3_44100_192",
                               {"model_id": "eleven_multilingual_sts_v2", "remove_background_noise": "true"},
                               {"audio": audio_path})


# ---------------------------------------------------------------- Gemini API
class Gemini:
    BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, key, image_model=None, video_model=None):
        self.key = key
        self.image_model = image_model or os.environ.get("KK_IMAGE_MODEL", "gemini-2.5-flash-image")
        self.video_model = video_model or os.environ.get("KK_VIDEO_MODEL", "veo-3.1-fast-generate-preview")

    def _h(self, extra=None):
        h = {"x-goog-api-key": self.key}
        h.update(extra or {})
        return h

    def image(self, prompt, ref_paths=(), aspect="9:16"):
        parts = [{"text": prompt}]
        for p in ref_paths:
            with open(p, "rb") as f:
                parts.append({"inline_data": {"mime_type": mimetypes.guess_type(p)[0] or "image/png",
                                              "data": base64.b64encode(f.read()).decode()}})
        payload = {"contents": [{"role": "user", "parts": parts}],
                   "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
        body, _ = _request("POST", f"{self.BASE}/models/{self.image_model}:generateContent",
                           self._h({"Content-Type": "application/json"}), json.dumps(payload).encode())
        res = json.loads(body)
        for cand in res.get("candidates", []):
            for part in (cand.get("content") or {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])
        reason = (res.get("promptFeedback") or {}).get("blockReason") or \
            [c.get("finishReason") for c in res.get("candidates", [])]
        raise RuntimeError(f"No image returned (reason: {reason})")

    def video(self, prompt, first_frame=None, aspect="9:16", seconds=8, negative=None,
              resolution=None, poll=10, timeout=900, log=print):
        inst = {"prompt": prompt}
        if first_frame:
            with open(first_frame, "rb") as f:
                inst["image"] = {"bytesBase64Encoded": base64.b64encode(f.read()).decode(),
                                 "mimeType": mimetypes.guess_type(first_frame)[0] or "image/png"}
        params = {"aspectRatio": aspect, "durationSeconds": int(seconds)}
        if negative:
            params["negativePrompt"] = negative
        if resolution or os.environ.get("KK_VIDEO_RES"):
            params["resolution"] = resolution or os.environ["KK_VIDEO_RES"]
        body, _ = _request("POST", f"{self.BASE}/models/{self.video_model}:predictLongRunning",
                           self._h({"Content-Type": "application/json"}),
                           json.dumps({"instances": [inst], "parameters": params}).encode())
        op = json.loads(body)["name"]
        t0 = time.time()
        while True:
            time.sleep(poll)
            body, _ = _request("GET", f"{self.BASE}/{op}", self._h())
            st = json.loads(body)
            if st.get("done"):
                break
            if time.time() - t0 > timeout:
                raise TimeoutError(f"Veo operation {op} did not finish in {timeout}s")
            log(f"      ...rendering ({int(time.time() - t0)} s)")
        if "error" in st:
            raise RuntimeError(f"Veo error: {st['error']}")
        resp = st.get("response", {})
        samples = (resp.get("generateVideoResponse") or resp).get("generatedSamples") or \
            (resp.get("generateVideoResponse") or resp).get("generatedVideos") or []
        if not samples:
            raise RuntimeError(f"Veo returned no video (filtered?): {json.dumps(resp)[:400]}")
        uri = samples[0]["video"]["uri"]
        sep = "&" if "?" in uri else "?"
        data, _ = _request("GET", f"{uri}{sep}alt=media" if "alt=media" not in uri and ":download" in uri else uri,
                           self._h(), timeout=600)
        return data
