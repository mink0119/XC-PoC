# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud(API Security)에서 **정상 다중 ID·IP 패턴**과 **비정상 객체 접근(BOLA)** 을 구분하는지 검증하기 위한 **트래픽 생성 랩**입니다.

- **Pet Shop** = 대상 API (기본: 소유권 미검사 → XC가 BOLA를 관찰)
- **로컬 lab** = 공격/학습 트래픽 생성기 (`scenarios/`)
- 탐지·차단 확인은 **F5 XC Console**. 이 랩이 인라인 차단을 대신하지 않습니다.

제품 방향: **[docs/PRD.md](docs/PRD.md)** · 시나리오 상세: **[docs/SCENARIOS.md](docs/SCENARIOS.md)**

```text
[로컬 PC]  scenarios/serve_lab.py  또는  run_bola.py
    │  HTTP (가능하면 XC VIP → Pet Shop)
    ▼
[Pet Shop]  Docker  (예: 192.168.47.81:80)
    ┊
[F5 XC]  Discovery · BOLA Incident · (완화 시) Protection / Rate Limit / Block
```

---

## 1. Pet Shop 서버 — Docker 설치·실행 (`192.168.47.81`)

### 준비물

- Docker Engine + Docker Compose plugin (`docker compose`)
- 호스트 **80/tcp** 사용 (다른 포트: `PETSHOP_PORT`)

### A. 이 저장소에서 바로 올리는 방법 (권장)

서버에서:

```bash
# 코드 받기
git clone https://github.com/mink0119/XC-PoC.git
cd XC-PoC/petshop

# 빌드 + 기동
docker compose up -d --build

# 확인
docker compose ps
curl -s http://127.0.0.1/health
# → {"status":"ok", ...}
```

외부에서: `http://192.168.47.81/health` · Swagger `http://192.168.47.81/docs` · OpenAPI `http://192.168.47.81/swagger.json`

### B. 로컬에서 빌드해 서버로 동기화

```bash
# (로컬) 최신 코드 반영 후 서버에 petshop만 복사
scp -r petshop root@192.168.47.81:/root/XC-PoC/

# (서버)
ssh root@192.168.47.81
cd /root/XC-PoC/petshop
docker compose up -d --build
curl -s http://127.0.0.1/health
```

### 운영 명령

```bash
cd /path/to/XC-PoC/petshop

docker compose logs -f petshop          # 로그
docker compose restart petshop          # 재시작
docker compose up -d --build            # 코드 변경 후 재빌드
docker compose down                     # 중지·삭제
```

### 환경 변수

| 변수 | 기본 | 의미 |
|------|------|------|
| `PETSHOP_PORT` | `80` | 호스트에 노출할 포트 |
| `ENFORCE_OWNERSHIP` | `0` | `1`이면 정상 API처럼 소유권 검사(남의 객체 403) |

예:

```bash
PETSHOP_PORT=8080 ENFORCE_OWNERSHIP=0 docker compose up -d --build
```

요청 헤더 `X-Enforce-Ownership: 1` 로도 요청 단위 전환 가능합니다.

### Docker Compose 없이 이미지 직접

```bash
cd petshop
docker build -t petshop-bola .
docker run -d --name petshop-api --restart unless-stopped \
  -p 80:80 -e PORT=80 -e ENFORCE_OWNERSHIP=0 \
  petshop-bola
```

---

## 2. 로컬 — 일괄트래픽(학습) / 시나리오 GUI

공격·학습 UI는 **Pet Shop 호스트에 두지 않습니다.** 로컬에서 실행합니다.

### 설치

```bash
git clone https://github.com/mink0119/XC-PoC.git
cd XC-PoC/scenarios
# GUI는 표준 라이브러리만 사용 (추가 pip 없음)
```

### 실행

```bash
python3 serve_lab.py
# → http://127.0.0.1:8765
```

| 옵션 | 예 |
|------|-----|
| 포트 | `python3 serve_lab.py --port 8765` |
| 브라우저 자동 오픈 끄기 | `python3 serve_lab.py --no-open` |

### 화면 사용

1. **대상 서버 주소** = Pet Shop (또는 XC VIP)  
   예: `http://192.168.47.81`
2. 왼쪽 **일괄트래픽(학습)**
   - **정상 · XC 학습** — baseline (BOLA 제외) × N (기본 300)
   - **비정상 · BOLA/이상** — 학습 후 공격 세트
   - **전체 시나리오** — 정상+비정상
3. **HTTP 요청/응답 로그 남기기**
   - **OFF(기본)** — 카운트만 (대량 학습)
   - **ON** — 하단 HTTP 로그에 request/response 적재 (차단·상태코드 확인용)
4. P1/P2/P3 항목은 **단건** 실행·설명용입니다.

> 탐지(Incident) ≠ 자동 차단. 차단은 XC에서 API Protection / Rate Limit / IP·User Block 등을 켠 뒤, 로그 ON으로 응답 코드·차단 여부를 확인하세요.

---

## 3. CLI (선택)

```bash
cd scenarios
python3 -m pip install -r requirements.txt

# 정상 학습 300회 (기본: HTTP 상세 로그 OFF)
python3 run_bola.py --base http://192.168.47.81 --batch benign --repeat 300

# 학습이지만 HTTP JSONL까지 남기기
python3 run_bola.py --base http://192.168.47.81 --batch benign --repeat 10 --http-log

# 비정상 세트 1회 + 상세 로그
python3 run_bola.py --base http://192.168.47.81 --batch attack --repeat 1 --http-log

# 단건
python3 run_bola.py --base http://192.168.47.81 --scenario cross_customer_bola
```

| 플래그 | 의미 |
|--------|------|
| `--batch benign\|attack\|all` | 일괄 세트 |
| `--repeat N` | 세트 반복 (N>1이면 기본 quiet) |
| `--http-log` | 반복이어도 `*.http.jsonl` 기록 |
| `--quiet-http` | 항상 상세 로그 생략 |
| `--enforce-ownership` | 대상에 소유권 검사 헤더 |

산출물: `scenarios/out/*.jsonl`, `*.http.jsonl`, `*.summary.json`

---

## 4. 구성

| 경로 | 역할 |
|------|------|
| `docs/PRD.md` | 제품 기준 (P1/P2/P3) |
| `petshop/` | 대상 API + `Dockerfile` + `docker-compose.yml` |
| `petshop/swagger.json` | OpenAPI (XC 업로드용, `accounts/inquire` 포함) |
| `scenarios/lab/` | 로컬 GUI |
| `scenarios/serve_lab.py` | GUI 서버 `:8765` |
| `scenarios/run_bola.py` | CLI |

| 그룹 | 내용 |
|------|------|
| **일괄트래픽(학습)** | 정상 / 비정상 / 전체 세트 |
| **P1** | Path·Body `accountNo`·ID 열거 BOLA |
| **P2** | 순환·고정 IP·토큰 재발급 (오탐) |
| **P3** | 정상 후 급탐색 |

---

## 5. XC 참고

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security) — Incident 후 완화(Protection / Rate limit / Block 등)
- [Import OpenAPI](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/how-to/adv-security/import-openapi-spec)
- [API Rate Limiting](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/how-to/api-security/configure-api-rate-limiting)
