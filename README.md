# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud(API Security)에서 **정상 다중 ID·IP 패턴**과 **비정상 객체 접근(BOLA)** 을 구분하는지 검증하기 위한 **트래픽 생성 랩**입니다.

| 구성 | 역할 | 예 (192.168.47.81) |
|------|------|---------------------|
| **Pet Shop** | 대상 API | `http://192.168.47.81/` (`:80`) |
| **Attack lab** | 학습/공격 시나리오 UI | `http://192.168.47.81:8765/` |

탐지·차단 확인은 **F5 XC Console**. 이 랩이 인라인 차단을 대신하지 않습니다.

방향: **[docs/PRD.md](docs/PRD.md)** · 시나리오: **[docs/SCENARIOS.md](docs/SCENARIOS.md)**

```text
[브라우저] → http://192.168.47.81:8765   (attack-lab 컨테이너)
                 │  fetch (대상 URL)
                 ▼
           http://192.168.47.81/         (petshop 컨테이너 :80)
                 ┊
              [F5 XC]
```

---

## 한 번에 올리기 (권장 · 47.81)

서버에서:

```bash
git clone https://github.com/mink0119/XC-PoC.git
cd XC-PoC

docker compose up -d --build

# 확인
curl -s http://127.0.0.1/health          # Pet Shop API
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/   # Attack lab UI → 200
```

| 접속 | URL |
|------|-----|
| **시나리오 / 학습 UI** | **http://192.168.47.81:8765** |
| Pet Shop health | http://192.168.47.81/health |
| Pet Shop Swagger | http://192.168.47.81/docs |

UI의 **대상 서버 주소**는 Pet Shop API를 가리킵니다 → `http://192.168.47.81`  
(lab 포트 `8765`가 아닙니다. XC VIP를 쓰면 VIP URL.)

### 로그

```bash
# Attack lab 접속 로그 (serve_lab access log)
docker compose logs -f attack-lab

# Pet Shop API 로그
docker compose logs -f petshop

# 둘 다
docker compose logs -f
```

UI에서 **일괄트래픽(학습)** → **HTTP 요청/응답 로그 남기기 ON** 이면, 브라우저 화면에 Pet Shop으로 나간 request/response도 쌓입니다 (차단·상태코드 확인용).

### 갱신·재시작

```bash
cd XC-PoC
git pull
docker compose up -d --build
```

### 분리 기동

```bash
# API만
cd petshop && docker compose up -d --build

# 공격 UI만
cd scenarios && docker compose up -d --build
```

---

## 로컬 PC에서 lab만 (Docker 없이)

```bash
cd scenarios
python3 serve_lab.py
# → http://127.0.0.1:8765
```

대상 서버: `http://192.168.47.81`

---

## UI에서 할 일

1. **http://192.168.47.81:8765** 접속
2. 대상 서버 = `http://192.168.47.81` (또는 XC VIP)
3. 왼쪽 **일괄트래픽(학습)**
   - **정상 · XC 학습** × N (기본 300) — baseline
   - **비정상 · BOLA/이상** — 학습 후
   - **전체 시나리오**
4. 필요 시 **HTTP 요청/응답 로그 남기기** ON
5. P1/P2/P3는 단건 실행·설명용

> Incident 탐지 ≠ 자동 차단. XC에서 Protection / Rate Limit / Block 적용 후, 로그 ON으로 응답이 막히는지 확인하세요.

---

## CLI (선택)

```bash
cd scenarios
python3 -m pip install -r requirements.txt

python3 run_bola.py --base http://192.168.47.81 --batch benign --repeat 300
python3 run_bola.py --base http://192.168.47.81 --batch attack --repeat 1 --http-log
```

| 플래그 | 의미 |
|--------|------|
| `--batch benign\|attack\|all` | 일괄 세트 |
| `--repeat N` | 반복 (N>1이면 기본 HTTP JSONL OFF) |
| `--http-log` | 상세 `*.http.jsonl` 강제 |
| `--quiet-http` | 상세 로그 생략 |

---

## 환경 변수

| 변수 | 기본 | 대상 |
|------|------|------|
| `PETSHOP_PORT` | `80` | Pet Shop 호스트 포트 |
| `LAB_PORT` | `8765` | Attack lab 호스트 포트 |
| `ENFORCE_OWNERSHIP` | `0` | Pet Shop 소유권 검사 (`1`=정상 API) |

---

## 구성

| 경로 | 역할 |
|------|------|
| `docker-compose.yml` | Pet Shop + Attack lab 한 번에 |
| `petshop/` | 대상 API |
| `scenarios/` | lab UI · `serve_lab.py` · CLI |
| `scenarios/lab/index.html` | 브라우저 UI |

---

## XC 참고

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Import OpenAPI](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/how-to/adv-security/import-openapi-spec)
- [API Rate Limiting](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/how-to/api-security/configure-api-rate-limiting)
