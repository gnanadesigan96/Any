# Create all character voices in ElevenLabs automatically

`create_elevenlabs_voices.py` designs and saves the 11 series voices (`KK_Kannan`, `KK_Yashoda`, `KK_Narrator`, `KK_Balarama`, `KK_Shridama`, `KK_Subala`, `KK_Gomathi`, `KK_Kamala`, `KK_Paati`, `KK_Nanda`, `KK_Kamsa`) in your ElevenLabs account, using the descriptions and Tamil sample lines in `voices.json`.

For each character it makes **3 previews**. You listen and pick the best; nothing is saved without your choice. The chosen voice IDs are written to `voice_register.json`.

## 1. Get an ElevenLabs API key
1. ElevenLabs → profile / **Developers** → **API Keys** → **Create API key**.
2. Give it permission for **Text to Voice / Voice Generation** and **Voices (write)**. Leave everything else off.
3. Copy the key. **Don't share it in chat or email.**

## 2a. Run it on your own computer (simplest)
1. Install **Python 3** from python.org (Windows: tick "Add Python to PATH" during install).
2. Download this repo (GitHub → **Code → Download ZIP**) and unzip it.
3. Open a terminal in the `krishna-shorts/tools` folder:
   - **Windows:** open the folder in File Explorer, click the address bar, type `cmd`, press Enter.
   - **Mac:** right-click the folder → **New Terminal at Folder**.
4. Run:
   ```
   python create_elevenlabs_voices.py
   ```
   (On Mac, use `python3`.)
5. Paste your API key when asked. It stays hidden and isn't saved.
6. For each character, the script makes 3 previews and opens the `voice_previews` folder. Listen, then type **1**, **2** or **3** to keep one, **r** for new previews, or **s** to skip.

Voices that already exist in your account (same name) are skipped, so you can stop and rerun at any time.

**Steering a voice:** if all 3 previews are wrong (e.g. the boy sounds too old), edit that character's `description` in `voices.json` (for example add "very young, small child, high pitched") and run again.

## 2b. Let Claude run it for you
In a Claude Code cloud session, the environment must allow `api.elevenlabs.io` and hold your key:
1. In the session's environment settings (the cloud environment menu in the title bar → **Edit**):
   - **Network access:** add `api.elevenlabs.io` to **Allowed domains**.
   - **Secrets / environment variables:** add `ELEVENLABS_API_KEY` with your key.
2. Start a new session (it picks up the new settings) and ask Claude to "run the ElevenLabs voice script".
3. Claude runs `preview`, sends you the preview MP3s, you say which number to keep for each voice, and Claude runs `save`.

Commands used in that mode:
```
python create_elevenlabs_voices.py preview                  # 3 previews for every voice
python create_elevenlabs_voices.py preview KK_Kannan        # just one voice
python create_elevenlabs_voices.py save KK_Kannan=2 KK_Yashoda=1
python create_elevenlabs_voices.py list                     # show your KK_ voices
python create_elevenlabs_voices.py check                    # validate voices.json (no API calls)
```

## Notes
- Each preview uses ElevenLabs credits; 11 voices × 3 previews is a small part of a Starter plan. Rerolls cost more.
- ElevenLabs may refuse to design some voices (child voices in particular). If that happens, use the real-child + Voice Changer method in [04-voices-and-cinematic-flow.md](../04-voices-and-cinematic-flow.md#a2-the-best-way-to-get-each-type-of-voice-honest-assessment).
- After the voices exist, generate the lines from [ep01-voice-lines-elevenlabs.md](../episodes/ep01-voice-lines-elevenlabs.md).
