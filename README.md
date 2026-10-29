# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 검토용 랩입니다.
**방어는 XC에서만** 합니다. Pet Shop은 취약(소유권 미검사)합니다.

## 역할 분리

| 위치 | 역할 |
|------|------|
| Pet Shop 서버 (예: `192.168.47.81`) | **대상 API만** |
| 로컬 PC (`scenarios/`) | **공격 시나리오** GUI / CLI |

```text
[로컬 PC]  설치 → serve_lab.py 실행 → 브라우저에서 시나리오 실행
     │  HTTP
     ▼
[Pet Shop] 설치 → API 기동 → /health OK
```

서버 `/lab` 은 안내 페이지만 제공합니다. 공격 UI는 로컬에서 설치·실행합니다.

---

## 사용 방법 ① — Pet Shop 서버 (설치 → 실행 → 확인)

대상 API를 **설치하고 실행**한 뒤 health로 확인합니다.

### 준비물

- Docker + Docker Compose, 또는 Python 3.9+
- 기본 포트 **80/tcp** (`PORT`로 변경 가능)

### 현재 PoC 서버 (`192.168.47.81`)

```bash
# 1) 코드 배치 (최초 또는 갱신)
scp -r petshop/* root@192.168.47.81:/root/nginx/petshop/

# 2) 설치·기동 (compose가 pip install 후 app 실행)
ssh root@192.168.47.81
cd /root/nginx
docker compose up -d --force-recreate petshop

# 3) 실행 확인
docker compose ps petshop
curl -s http://127.0.0.1/health
# → {"status":"ok"}
```

이후 접속:

- API / health: `http://192.168.47.81/health`
- Swagger: `http://192.168.47.81/docs`

### 다른 호스트에 Docker로 설치·실행

```bash
cd petshop
docker build -t petshop-bola .          # 설치(이미지 빌드)
docker run -d --name petshop-api --restart always \
  -p 80:80 -e PORT=80 \
  petshop-bola                          # 실행
curl -s http://127.0.0.1/health           # 확인
```

### Docker 없이 설치·실행 (개발용)

```bash
cd petshop
python3 -m pip install -r requirements.txt   # 설치
PORT=18080 python3 app.py                    # 실행
curl -s http://127.0.0.1:18080/health        # 확인
```

---

## 사용 방법 ② — 공격자 GUI (설치 → 실행 → 시나리오)

로컬 PC에서 GUI를 **설치(클론)하고 실행**한 뒤, 대상 URL을 가리켜 시나리오를 돌립니다.  
추가 `pip` 패키지는 없습니다 (Python 3 표준 라이브러리만 사용).

### 설치

```bash
git clone https://github.com/mink0119/XC-PoC.git
cd XC-PoC/scenarios
```

이미 클론해 두었다면 `cd XC-PoC/scenarios` 만 하면 됩니다.

### 실행

```bash
python3 serve_lab.py
# → http://127.0.0.1:8765  (브라우저 자동 오픈)
```

```bash
python3 serve_lab.py --port 8765       # 포트
python3 serve_lab.py --no-open         # 자동 오픈 끄기
```

### 화면에서 쓰기

1. **Target Base URL** = Pet Shop 주소  
   예: `http://192.168.47.81` 또는 로컬 `http://127.0.0.1:18080`
2. **대상 health 확인** — 서버가 떠 있는지 확인
3. 왼쪽 **attack type** 선택 — Expected flow / Example / 옵션 설명 확인
4. 옵션 조정 후 **이 시나리오 실행** (요청: 로컬 → Pet Shop)
5. 결과 표 + HTTP log / JSONL 다운로드로 검증

| 옵션 | 의미 |
|------|------|
| Target Base URL | 대상 Pet Shop (GUI 주소가 아님) |
| 순환 ID 개수 | `operator_cyclic` 전용, 1–500 |
| 순환·고정·열거 샘플 | 해당 시나리오 요청 횟수 |
| operator_code OFF/ON | 현재형(오탐) / 미래형 claim |

---

## 사용 방법 ③ — CLI (설치 → 실행, 선택)

```bash
cd scenarios
python3 -m pip install -r requirements.txt   # 설치 (requests)

python3 run_bola.py --list
python3 run_bola.py --base http://192.168.47.81 --scenario cross_customer_bola
python3 run_bola.py --base http://192.168.47.81 \
  --scenario operator_cyclic --cyclic-ids 264
```

산출물 (`scenarios/out/`): `*.jsonl` (요약), `*.http.jsonl` (요청·응답), `*.summary.json` (집계)

---

## 한 줄 요약

| 단계 | 서버 | 공격자(로컬) |
|------|------|----------------|
| 설치 | `petshop` 배치 + compose/build 또는 `pip install` | `git clone` → `scenarios/` |
| 실행 | `docker compose up -d petshop` 또는 `python3 app.py` | `python3 serve_lab.py` |
| 확인·사용 | `curl …/health` | 브라우저에서 시나리오 실행 |

---

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약 대상 API |
| `scenarios/lab/` | 공격 GUI 정적 파일 |
| `scenarios/serve_lab.py` | 로컬 GUI 서버 (`127.0.0.1:8765`) |
| `scenarios/run_bola.py` | CLI 러너 |
| `docs/SCENARIOS.md` | 시나리오·플로우 상세 |

## operator_code / 순환형

| 모드 | 토큰 | XC 검증 |
|------|------|---------|
| OFF (기본) | 운영자 claim 없음 | IP 다계정 **오탐** 후보 |
| ON | `operator_code` 포함 | 운영자 신원 구분 여부 |

`operator_cyclic` + 순환 ID 개수(1–500). 상세는 [docs/SCENARIOS.md](docs/SCENARIOS.md).

## 공식 문서

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)
