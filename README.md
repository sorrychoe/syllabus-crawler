# syllabus-crawler

한동대학교 학사정보시스템(HISNet)에 로그인하여 특정 학기·학부의 개설 강의 중
**강의계획서가 등록된 과목**을 조회하고, 선택한 과목의 강의 개요 및 평가 기준을
터미널에서 확인할 수 있는 CLI 크롤러입니다.

## 주요 기능

- HISNet 계정으로 자동 로그인 (ID/비밀번호는 실행 중 입력)
- 조회할 연도·학기(`예: 2021-2`)와 학부 선택
- 개설 강의 목록을 페이지 단위로 순회하며 강의계획서 등록 여부 확인
- 강의계획서가 등록된 과목의 `과목코드 / 과목명 / 담당교수` 출력
- 특정 과목코드 입력 시 강의 개요, 인정 전공, 평가 비중(출석·중간·기말·퀴즈·팀프로젝트·개인과제·기타) 출력
- 실행 중인 Chrome 버전에 맞는 ChromeDriver 자동 설치

## 요구 사항

- Python 3
- Google Chrome (설치되어 있어야 하며, 버전에 맞는 ChromeDriver는 자동 설치됨)
- 유효한 HISNet 계정

의존성:

| 패키지 | 용도 |
| --- | --- |
| `selenium` | 브라우저 자동화 |
| `chromedriver-autoinstaller` | Chrome 버전에 맞는 드라이버 자동 설치 |
| `urllib3` | selenium 의존성 |

## 설치

```bash
# 개발 환경 포함 설치 (lint 도구 + pre-commit 훅)
make init

# 또는 실행에 필요한 최소 의존성만 설치
pip install -r requirements.txt
```

`make init`은 다음을 수행합니다.

- `pip` 업그레이드
- `requirements-dev.txt` 설치 (`requirements.txt` + `flake8`, `isort`, `pre-commit`, `pylint`)
- `pre-commit` 훅 설치

## 사용법

```bash
make run
# 또는
python main.py
```

실행 순서는 다음과 같습니다.

1. `HISNet ID` / `Password` 입력 → 자동 로그인
2. 조회할 학기 입력 (`YYYY-{1~4}` 형식, 예: `2021-2`)
3. 출력된 학부 목록에서 번호를 선택
   - `%` : 전체
   - `#` : 창의융합교육원
   - `$` : AI융합학부
   - `0`~`9` : 개별 학부 (`faculty.py` 참고)
4. 해당 조건의 강의를 순회하며 강의계획서가 등록된 과목 목록을 출력
5. 개요 조회 여부를 묻는 프롬프트에서 `Y` 입력 후 과목코드를 입력하면
   강의 개요 · 인정 전공 · 평가 기준을 출력

## 프로젝트 구조

```
.
├── main.py            # 크롤러 진입점 (로그인 → 강의 조회 → 개요 출력)
├── faculty.py         # 학부 코드/이름 매핑 테이블
├── Makefile           # init / lint / run / clear 태스크
├── requirements.txt       # 실행 의존성
├── requirements-dev.txt   # 개발 의존성
├── .flake8 / .isort.cfg   # 린트 설정
└── .pre-commit-config.yaml
```

## 개발

```bash
make lint     # isort + flake8 실행
make clear    # __pycache__ 및 chromedriver 캐시 삭제
```

커밋 시 `pre-commit` 훅으로 `make lint`, trailing whitespace 정리,
`add-trailing-comma` 등이 자동 실행됩니다.

## 참고 사항

- HISNet의 DOM 구조(테이블 위치, XPath 등)에 강하게 의존하므로,
  학사정보시스템 화면이 변경되면 셀렉터를 수정해야 할 수 있습니다.
- 로그인 정보는 저장되지 않으며 매 실행마다 입력해야 합니다.
