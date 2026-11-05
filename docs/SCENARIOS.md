# BOLA lab scenario guide

기준 문서: **[PRD.md](PRD.md)**  
Pet Shop은 소유권을 검사하지 않습니다. 방어는 XC에서만 합니다.

## 역할 분리

| 위치 | 역할 |
|------|------|
| 로컬 `scenarios/` | 공격·정상 패턴 **트래픽 생성** |
| Pet Shop | 취약 **대상 API**만 |
| F5 XC | Discovery / BOLA / 이상행위 **탐지** (이 랩 밖) |

## 시나리오와 옵션 (필요한 것만)

| 시나리오 | 의미 | UI에 나오는 옵션 |
|----------|------|------------------|
| `public_catalog` | 공개 상품 | (없음) |
| `self_order` | 내 주문 1건 | (없음) |
| `matched_order_learn` | 계정 N → `/orders/N` + **계정마다 다른 XFF** | 계정 수, 반복 횟수 |
| `matched_account_learn` | 계정 N → 본인 `accountNo` + 계정마다 다른 XFF | 계정 수, 반복 횟수 |
| `cross_customer_bola` | Path로 남의 객체 | (없음) |
| `account_body_bola` | Body로 남의 계좌 | (없음) |
| `id_enumeration` | 주문번호 연속 | 열거 개수 |
| `operator_cyclic` | **운영사**: 다계정 + **공유 IP** | 계정 수, 요청 수, 공유 IP 개수, operator_code |
| `operator_fixed` | 같은 계정 + IP만 변경 | IP 변경 횟수, operator_code |
| `access_token_reissue` | 토큰 일자 재발급 | operator_code |
| `abnormal_probe` | 정상 후 타인 급탐색 | (없음) |

일괄 **정상 · XC 학습**: 세트 반복 + 학습 계정 수(+매칭 반복) + HTTP 로그 ON/OFF 만.

## IP 규칙 (기억할 것 2가지)

1. **일반** (매칭 학습 등): `customer_id` 마다 `X-Forwarded-For`가 **다름** (1:1). 소켓 IP는 그대로.
2. **운영사** (`operator_cyclic`): 여러 계정을 **1개(또는 소수) IP**로 쏨 → 오탐 재현용.

요약 표의 `source_ip` 열 · HTTP 로그 Request 헤더의 `X-Forwarded-For`로 확인하세요.  
XC가 실제 클라이언트 IP만 보면 전부 같아 보입니다 — XFF를 User Identification에 쓰도록 XC 쪽 설정이 필요합니다.

## matched_order_learn

```text
JWT customer_id=1  → GET /orders/1  · XFF 198.51.100.1
JWT customer_id=2  → GET /orders/2  · XFF 198.51.100.2
…
× matched-rounds
```

예: 계정 40 · 반복 10 → 400 GET. IP 식별 학습이면 계정 수 ≥30.

## 사용

```bash
cd scenarios
python3 serve_lab.py          # http://127.0.0.1:8765
python3 run_bola.py --base http://192.168.47.81 --scenario matched_order_learn --matched-customers 40 --matched-rounds 2
python3 run_bola.py --base http://192.168.47.81 --scenario operator_cyclic --cyclic-ids 264 --operator-shared-ips 1
```

## operator_code

| 모드 | JWT | 의미 |
|------|-----|------|
| OFF (기본) | 운영자 claim 없음 | 현재형 · 오탐 검토 |
| ON | `operator_code` 포함 | 미래형 |

## 학습 기간

BOLA/행위 분석은 학습 트래픽·시간이 필요할 수 있습니다.  
실행 직후 XC 이벤트가 없다고 미지원으로 단정하지 마세요.
