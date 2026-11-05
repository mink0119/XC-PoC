# BOLA lab scenario guide

기준: **[PRD.md](PRD.md)**  
Pet Shop은 기본 소유권 미검사. 방어·탐지는 XC.

## 시나리오 3개만

| 키 | 그룹 | 의미 | 기본 |
|----|------|------|------|
| `normal_orders` | 정상 | `customer_id` N → `GET /api/v1/orders/N` | 계정 **50**, XFF도 계정마다 다름 |
| `attack_orders` | 공격 | `customer_id` N → `GET /api/v1/orders/M` (**M≠N**) | 계정 **50**, XFF 계정마다 다름 |
| `operator_orders` | 운영사(정상) | 정해진 계정 풀을 순환, **각 계정은 자기 주문만**, XFF는 **공유 IP 개수**로만 | 풀 50 · 요청 50 · 공유 IP **1** |

Body `accountNo` 시나리오는 보류(추후). Path `/orders/{id}` 만 사용합니다.

## IP 규칙

| 시나리오 | X-Forwarded-For |
|----------|-----------------|
| 정상 / 공격 | 계정마다 1:1 (기본 50개 이상) |
| 운영사 | 설정한 공유 IP 개수만 순환 (계정마다 IP를 바꾸지 않음) |

소켓 IP는 바뀌지 않습니다. 요약 표 `XFF` 열 · HTTP 로그 Request 헤더로 확인하세요.

## 라벨

`customer_id == order_id` → **정상(benign)**  
아니면 → **BOLA**  
`operator_code` claim은 라벨에 영향 없음(XC 실험용 옵션).

## CLI

```bash
cd scenarios
python3 run_bola.py --base http://192.168.47.81 --scenario normal_orders --users 50 --rounds 1
python3 run_bola.py --base http://192.168.47.81 --scenario attack_orders --users 50 --rounds 1
python3 run_bola.py --base http://192.168.47.81 --scenario operator_orders --operator-customers 50 --operator-requests 100 --operator-shared-ips 1
```

GUI: `python3 serve_lab.py` → http://127.0.0.1:8765
