# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 검토용 랩입니다.
**방어는 XC에서만** 합니다. Pet Shop은 취약(소유권 미검사)합니다.

## 역할 분리

| 위치 | 역할 |
|------|------|
| `192.168.47.81` (Pet Shop) | **대상 API만** (`/health`, `/docs`, 취약 객체) |
| 로컬 PC (`scenarios/`) | **공격 시나리오** GUI / CLI |

서버의 `/lab` 은 안내 페이지만 보여 줍니다. 공격 UI는 로컬에서 띄웁니다.

## 가장 쉬운 사용법 (로컬 GUI)

Windows / macOS — 추가 패키지 없이 브라우저 + Python 표준 라이브러리.

```bash
cd scenarios
python3 serve_lab.py
# → http://127.0.0.1:8765  (자동으로 브라우저 오픈)
```

1. Target Base URL: `http://192.168.47.81`
2. 왼쪽에서 attack type 선택 → 예상 flow / 예시 확인
3. 옵션 설명 확인 후 **이 시나리오 실행**
4. 하단 HTTP log · JSONL 다운로드로 요청·응답 검증

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약 대상 API (Docker on 47.81) |
| `scenarios/lab/` | 로컬 공격 GUI |
| `scenarios/serve_lab.py` | 로컬 GUI 서버 (`127.0.0.1:8765`) |
| `scenarios/run_bola.py` | CLI 러너 |
| `docs/SCENARIOS.md` | 시나리오·플로우 설명 |

## operator_code

| 모드 | 토큰 | XC 검증 포인트 |
|------|------|----------------|
| OFF (기본) | 운영자 claim 없음 | 현재 환경 · IP 다계정 **오탐** |
| ON | `operator_code` 포함 | 운영자 신원 있을 때 구분 가능 여부 |

## 순환형

`operator_cyclic` + **순환 ID 개수** (1–500). 예전 `operator_large`는 통합됨.

## CLI (선택)

```bash
cd scenarios
python3 run_bola.py --base http://192.168.47.81 --scenario operator_cyclic --cyclic-ids 264
python3 run_bola.py --base http://192.168.47.81 --scenario cross_customer_bola
# → out/*.jsonl + *.http.jsonl + *.summary.json
```

## 요청·응답 로그

| 경로 | 내용 |
|------|------|
| 로컬 GUI | HTTP log 패널 + JSONL 다운로드 |
| CLI `scenarios/out/*.http.jsonl` | 교환 전체 |
| CLI `scenarios/out/*.jsonl` | 시나리오 요약 라벨 |

## Docker (대상 서버)

`192.168.47.81:/root/nginx/petshop` — `docker compose up -d --force-recreate petshop`

## 공식 문서

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)
