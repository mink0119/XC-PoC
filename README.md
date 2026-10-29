# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 동작을 검토하기 위한 로컬·Docker 랩입니다.
대상은 Pet Shop뿐이며, **방어는 XC에서만** 수행합니다.

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약한 Pet Shop API (소유권 미검사) |
| `scenarios/run_bola.py` | 합의된 시나리오 트래픽 재생 + 로컬 라벨(JSONL) |

서버 응답에는 탐지용 표식(`authorizedAccess`, 특수 헤더 등)을 넣지 않습니다.
라벨은 시나리오 러너가 `bola_model`로 로컬 계산합니다.

## Pet Shop

- `POST /api/v1/auth/token` — HS256 JWT (`sub`, `customer_id`, `operator_code`, `token_day`)
- 비공개 조회(`/api/v1/orders/{id}`, `/payments/{id}`, `/customers/{id}`, `/pets/{id}` 등)는 **항상 200** (취약)
- 신원 키는 JWT의 `operator_code` / `customer_id`. IP는 시나리오에서 `X-Forwarded-For`로 소스 IP만 재현

공식 문서:

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)

## Docker (서버)

배포 대상: `192.168.47.81` `/root/nginx/petshop`  
`/root/nginx/docker-compose.yml`의 `petshop` 서비스가 host 네트워크로 포트 80에 기동합니다.

```bash
# 서버에서
cd /root/nginx
docker compose up -d --force-recreate petshop
curl -s http://127.0.0.1/health
```

로컬에서 이미지로 단독 기동할 때:

```bash
cd petshop
docker build -t petshop-api .
docker run --rm -p 18080:80 petshop-api
```

## 시나리오 러너

```bash
cd scenarios
python3 -m pip install -r requirements.txt
python3 run_bola.py --base http://192.168.47.81
```

결과는 `scenarios/out/*.jsonl` 과 `*.summary.json` 에 저장됩니다.

| scenario | expected | 의미 |
|----------|----------|------|
| `public_catalog` | benign | 공개 카탈로그 조회 |
| `self_order` | benign | 본인 주문 |
| `operator_cyclic` | benign | 순환형 운영자(다수 ID), 공유 IP |
| `operator_fixed` | benign | 고정 ID, 소스 IP만 변경 |
| `daily_token_rotation` | benign | 일일 토큰 교체, `operator_code` 유지 |
| `operator_large` | benign | 한 IP에서 다수 ID 순환 |
| `cross_customer_bola` | bola | 배정되지 않은 타 계정 객체 |
| `id_enumeration` | bola(대부분) | 연속 ID 열거 |

## 다음 단계

XC Console에서 API Protection / Discovery로 이 트래픽을 통과시켜
정상 멀티계정 패턴과 실제 BOLA를 어떻게 구분하는지 검토합니다.
