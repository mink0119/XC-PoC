# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 동작을 검토하기 위한 로컬·Docker 랩입니다.
대상은 Pet Shop뿐이며, **방어는 XC에서만** 수행합니다.

시나리오 상세·플로우·실행 예시는 **[docs/SCENARIOS.md](docs/SCENARIOS.md)** 를 보세요.
문서를 열어 두고 `--scenario` 로 하나씩 돌리며 확인할 수 있습니다.

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약한 Pet Shop API (소유권 미검사) |
| `scenarios/run_bola.py` | 시나리오 트래픽 + 로컬 라벨(JSONL) |
| `docs/SCENARIOS.md` | 시나리오 플로우·예시·walkthrough |

## 빠른 실행

```bash
curl -s http://192.168.47.81/health

cd ~/Downloads/XC-PoC/scenarios
python3 run_bola.py --list
python3 run_bola.py --base http://192.168.47.81 --scenario operator_cyclic --cyclic 5
python3 run_bola.py --base http://192.168.47.81 --scenario cross_customer_bola
python3 run_bola.py --base http://192.168.47.81   # 전체
```

## 순환형 vs 대규모 (요약)

둘 다 **배정 계정 순환 = benign** 입니다. 공격 종류가 다르지 않습니다.

| | cyclic | large |
|--|--------|-------|
| 계정 수 | 264 | 500 |
| IP | 2개 교대 | 1개 고정 |
| path | `/orders/{id}` | `/customers/{id}/orders` |

자세한 표·예시는 [docs/SCENARIOS.md](docs/SCENARIOS.md) 참고.

## Pet Shop

- `POST /api/v1/auth/token` — 24h access token (`customer_id`, `operator_code`, `iat`, `exp`)
- 6시간 이내 동일 신원 재요청 시 기존 토큰 재사용
- private GET은 소유권 검사 없이 항상 200

## Docker

`192.168.47.81` `/root/nginx/petshop` — `docker compose up -d --force-recreate petshop`

## 공식 문서

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)
