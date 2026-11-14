# 🎌 릴스 → 일본어 텍스트 추출기

인스타 릴스 링크를 넣으면 일본어 음성을 텍스트(.txt)와 자막(.srt)으로 뽑아줘요.
링크가 막히면 영상 파일을 직접 올려도 돼요.

파일 구성: `app.py`, `requirements.txt`, `packages.txt` (세 파일을 한 폴더에 두세요)

---

## 1. PC에서 쓰기

1. [Python 3.10 이상](https://www.python.org/downloads/) 설치 (설치할 때 "Add to PATH" 체크)
2. 이 폴더에서 터미널(명령 프롬프트)을 열고 실행:
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. 브라우저가 자동으로 열려요 (http://localhost:8501)

> 첫 실행 때 음성 인식 모델(약 500MB)을 한 번 내려받아요.

## 2. 폰에서 쓰기 — 방법 A: 같은 와이파이

PC에서 이렇게 실행하면:
```
streamlit run app.py --server.address 0.0.0.0
```
터미널에 뜨는 **Network URL** (예: `http://192.168.0.12:8501`)을 폰 브라우저에 입력하면 돼요.
PC가 켜져 있어야 하지만, 가장 빠르고 인스타 차단도 덜 당해요.

## 3. 폰에서 쓰기 — 방법 B: 무료 클라우드 (PC 꺼져도 됨)

**Streamlit Community Cloud** (무료):
1. [GitHub](https://github.com)에 새 저장소를 만들고 세 파일을 업로드
2. [share.streamlit.io](https://share.streamlit.io)에 GitHub로 로그인
3. **Create app** → 저장소 선택 → Main file: `app.py` → **Deploy**
4. 생긴 주소(`https://xxxx.streamlit.app`)를 폰 홈 화면에 추가

> ⚠️ 인스타는 클라우드 서버 접속을 자주 막아요. 다운로드가 실패하면:
> - **cookies.txt 올리기**: PC 크롬에 "Get cookies.txt LOCALLY" 확장 설치 → 인스타 로그인 상태에서 instagram.com 쿠키 내보내기 → 앱 설정에서 업로드
>   (쿠키는 계정 로그인 정보라서 남에게 주면 안 돼요. 부계정 쿠키를 쓰는 걸 추천해요)
> - **파일 올리기 탭**: 폰에 릴스를 저장한 뒤 직접 업로드
>
> 무료 서버는 느려서 1분짜리 릴스에 1~2분 정도 걸려요. 모델은 `small`로 쓰는 걸 추천해요.

---

## 팁
- 정확도가 아쉬우면 설정에서 모델을 `medium`으로 바꿔요 (PC 추천, 더 느려요).
- 배경음악만 있고 말소리가 없으면 결과가 비어 있을 수 있어요.
- 개인 공부용으로만 쓰세요. 추출한 텍스트나 영상을 재배포하면 저작권 문제가 생길 수 있어요.
