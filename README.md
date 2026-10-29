# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 동작을 검토하기 위한 로컬·Docker 랩입니다.
대상은 Pet Shop뿐이며, **방어는 XC에서만** 수행합니다.

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약한 Pet Shop API (소유권 미검사) |
| `scenarios/run_bola.py` | 시나리오 트래픽 재생 + 로컬 라벨(JSONL) |

서버 응답에는 탐지용 표식을 넣지 않습니다. 라벨은 러너가 로컬에서만 계산합니다.

## Pet Shop

- `POST /api/v1/auth/token` — 24시간 access token (JWT)
  - claim: `sub`, `customer_id`, `operator_code`, `iat`, `exp`
  - 같은 계정/운영자로 6시간 이내 재요청 → 기존 토큰 재사용
  - `issued_at`(unix 초)을 주면 해당 시각 기준 재발급(랩용)
- 비공개 조회는 소유권 검사 없이 **항상 200**
- 신원 키: JWT의 `customer_id` / `operator_code` (IP는 `X-Forwarded-For`로 소스만 재현)

공식 문서:

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)

## 사용법

```bash
# 1) API (Docker, 192.168.47.81:80)
curl -s http://192.168.47.81/health

# 재배포가 필요할 때 (서버)
cd /root/nginx && docker compose up -d --force-recreate petshop

# 2) 시나리오 러너 (맥/로컬)
cd ~/Downloads/XC-PoC/scenarios
python3 -m pip install -r requirements.txt
python3 run_bola.py --base http://192.168.47.81
```

결과: `scenarios/out/*.jsonl`, `*.summary.json`

## 시나리오

| scenario | expected | 무엇을 재현하나 |
|----------|----------|----------------|
| `public_catalog` | benign | 공개 조회 |
| `self_order` | benign | 본인 객체 |
| `operator_cyclic` | benign | 다수 배정 계정 순환 + 공유 IP (오탐 후보) |
| `operator_fixed` | benign | 계정 고정 + IP만 변경 (오탐 후보) |
| `access_token_reissue` | benign | 24h access_token 재발급, 신원 claim 유지 |
| `operator_large` | benign | 한 IP에서 다수 ID |
| `cross_customer_bola` | bola | 타 계정 객체 직접 조회 |
| `id_enumeration` | bola(대부분) | 연속 객체 ID 열거 |

## 다음 단계

XC API Protection / Discovery에 이 트래픽을 통과시켜
정상 멀티계정·토큰 재발급과 실제 BOLA를 어떻게 구분하는지 검토합니다.
