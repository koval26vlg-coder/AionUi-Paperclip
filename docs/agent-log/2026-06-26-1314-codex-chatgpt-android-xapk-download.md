# 2026-06-26 13:14 - Codex - ChatGPT Android XAPK download

## User request
User asked to find and then download an Android APK for the ChatGPT app.

## Plan
- Prefer official source information first.
- If no direct official APK is available, use a mirror with package metadata.
- Save the deliverable in the current Codex thread `outputs` folder.
- Verify the saved file is an app package archive and not an HTML error page.

## What was done
- Confirmed official install route is Google Play for package `com.openai.chatgpt`.
- APKMirror listed a newer `1.2026.174` bundle, but direct terminal download returned a Cloudflare JavaScript challenge rather than the file.
- Downloaded `ChatGPT_1.2026.167_apkcombo.com.xapk` from APKCombo direct signed storage URL.
- Saved file to `C:\Users\koval\Documents\Codex\2026-06-26\new-chat-2\outputs\ChatGPT_1.2026.167_apkcombo.com.xapk`.

## Files changed
- Added this agent-log entry.
- User-facing output: `C:\Users\koval\Documents\Codex\2026-06-26\new-chat-2\outputs\ChatGPT_1.2026.167_apkcombo.com.xapk`.

## Verification
- File size: 150,708,177 bytes / 143.73 MB.
- SHA-256: `125BBCDA8B4FD4428FD1FE4DC4001FE51B24860FA693D8CA13F2EDD75447C186`.
- XAPK manifest fields:
  - `package_name`: `com.openai.chatgpt`
  - `name`: `ChatGPT`
  - `version_name`: `1.2026.167`
  - `version_code`: `2616700`
  - `min_sdk_version`: `32`
- Archive contains base `com.openai.chatgpt.apk` plus split APKs.

## Risks and limitations
- This is not an official OpenAI download channel; the safest installation path remains Google Play.
- File is XAPK/APKS-style split package, so Android's built-in single-APK installer may not install it directly. Use APKCombo Installer, APKMirror Installer, or SAI.
- APKMirror had a newer listed version, but automated terminal download was blocked by Cloudflare.

## Next agent notes
- If the user insists on the latest `1.2026.174`, manual browser download from APKMirror may be required.
- Do not install on the user's device without explicit confirmation.
