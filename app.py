"""인스타 릴스 → 일본어 텍스트 추출 웹앱 (Streamlit + yt-dlp + faster-whisper)"""
import os
import subprocess
import tempfile

import numpy as np
import streamlit as st
import yt_dlp
from faster_whisper import WhisperModel

st.set_page_config(page_title="릴스 → 일본어 텍스트", page_icon="🎌", layout="centered")


@st.cache_resource(show_spinner="음성 인식 모델 불러오는 중... (처음 한 번만)")
def load_model(size: str) -> WhisperModel:
    return WhisperModel(size, device="cpu", compute_type="int8")


def download_audio(url: str, workdir: str, cookiefile: str | None = None) -> str:
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(workdir, "media.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if cookiefile:
        opts["cookiefile"] = cookiefile
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def fmt_ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def load_audio(path: str) -> np.ndarray:
    """ffmpeg로 16kHz 모노 오디오를 직접 디코딩 (PyAV 호환성 문제 회피)"""
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path,
         "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(out, np.int16).astype(np.float32) / 32768.0


def transcribe(path: str, model: WhisperModel):
    segments, _ = model.transcribe(
        load_audio(path),
        language="ja",
        beam_size=5,
        vad_filter=True,  # 무음 구간 건너뛰기 → 엉뚱한 문장 생성 방지
    )
    return [(s.start, s.end, s.text.strip()) for s in segments if s.text.strip()]


def to_srt(segs) -> str:
    return "\n".join(
        f"{i}\n{fmt_ts(a)} --> {fmt_ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(segs, 1)
    )


# ---------------- UI ----------------
st.title("🎌 릴스 → 일본어 텍스트")
st.caption("인스타 릴스 링크를 넣으면 일본어 음성을 텍스트로 뽑아줘요.")

with st.expander("⚙️ 설정"):
    model_size = st.selectbox(
        "인식 모델 (클수록 정확하지만 느림)",
        ["small", "medium", "base"],
        index=0,
        help="무료 클라우드 서버에서는 small 이하를 추천해요.",
    )
    cookie_file = st.file_uploader(
        "cookies.txt (인스타가 로그인을 요구할 때만)", type=["txt"]
    )

tab_link, tab_file = st.tabs(["🔗 링크로", "📁 파일 올리기"])
with tab_link:
    url = st.text_input("릴스 링크", placeholder="https://www.instagram.com/reel/...")
    go_link = st.button("텍스트 추출", type="primary", use_container_width=True, key="go_link")
with tab_file:
    up = st.file_uploader(
        "영상/음성 파일 (링크가 막힐 때)", type=["mp4", "mov", "m4a", "mp3", "wav", "webm"]
    )
    go_file = st.button("텍스트 추출", type="primary", use_container_width=True, key="go_file")

if go_link or go_file:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            if go_link:
                if not url.strip():
                    st.warning("링크를 넣어주세요.")
                    st.stop()
                cpath = None
                if cookie_file:
                    cpath = os.path.join(tmp, "cookies.txt")
                    with open(cpath, "wb") as f:
                        f.write(cookie_file.getvalue())
                with st.spinner("릴스 다운로드 중..."):
                    media = download_audio(url.strip(), tmp, cpath)
            else:
                if not up:
                    st.warning("파일을 올려주세요.")
                    st.stop()
                media = os.path.join(tmp, up.name)
                with open(media, "wb") as f:
                    f.write(up.getvalue())

            model = load_model(model_size)
            with st.spinner("일본어 받아쓰는 중..."):
                segs = transcribe(media, model)
        except yt_dlp.utils.DownloadError as e:
            st.error(
                "다운로드 실패했어요. 비공개 계정이거나 인스타가 로그인을 요구하는 경우예요.\n\n"
                "→ 설정에서 cookies.txt를 올리거나, '파일 올리기' 탭을 써주세요.\n\n"
                f"상세: {e}"
            )
            st.stop()
        except subprocess.CalledProcessError as e:
            st.error(
                "오디오를 읽지 못했어요. 파일이 손상됐거나 지원하지 않는 형식일 수 있어요.\n\n"
                f"상세: {e.stderr.decode(errors='ignore')[-500:]}"
            )
            st.stop()

    if not segs:
        st.info("인식된 음성이 없어요. (배경음악만 있는 영상일 수 있어요)")
        st.stop()

    st.session_state["segs"] = segs

if segs := st.session_state.get("segs"):
    st.success(f"완료! {len(segs)}문장")
    show_ts = st.toggle("타임스탬프 표시", value=False)
    if show_ts:
        text = "\n".join(f"[{fmt_ts(a)[3:8]}] {t}" for a, _, t in segs)
    else:
        text = "\n".join(t for _, _, t in segs)
    st.text_area("결과 (길게 눌러 복사)", text, height=300)
    st.code(text, language=None)  # 우측 상단 복사 버튼용
    c1, c2 = st.columns(2)
    c1.download_button("📄 .txt 저장", text, "reels_ja.txt", use_container_width=True)
    c2.download_button("🎬 .srt 자막 저장", to_srt(segs), "reels_ja.srt", use_container_width=True)
