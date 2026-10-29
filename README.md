# XC PoC — Pet Shop BOLA lab

F5 Distributed Cloud API Security의 BOLA 탐지·오탐 검토용 랩입니다.
**방어는 XC에서만** 합니다. Pet Shop은 취약(소유권 미검사)합니다.

## 가장 쉬운 사용법 (GUI)

추가 설치 없이 브라우저만 있으면 됩니다 (Windows / macOS).

1. API 확인: http://192.168.47.81/health  
2. 랩 열기: **http://192.168.47.81/lab**  
3. 설정 후 버튼 클릭  
   - **순환 ID 개수** 1–500 (264/500 등)  
   - **operator_code** OFF=현재형(토큰에 운영자 없음) / ON=미래형  

상세: [docs/SCENARIOS.md](docs/SCENARIOS.md)

## 구성

| 경로 | 역할 |
|------|------|
| `petshop/` | 취약 API + `/lab` GUI |
| `scenarios/run_bola.py` | CLI 러너 (선택) |
| `docs/SCENARIOS.md` | 시나리오·플로우 설명 |

## operator_code

| 모드 | 토큰 | XC 검증 포인트 |
|------|------|----------------|
| OFF (기본) | 운영자 claim 없음 | 현재 환경 · IP 다계정 **오탐** |
| ON | `operator_code` 포함 | 운영자 신원 있을 때 구분 가능 여부 |

## 순환형

`operator_large`는 제거했습니다. `operator_cyclic` + **ID 개수**만 조절합니다.

## CLI (선택)

```bash
cd scenarios
python3 run_bola.py --base http://192.168.47.81 --scenario operator_cyclic --cyclic-ids 264
python3 run_bola.py --base http://192.168.47.81 --scenario operator_cyclic --cyclic-ids 500 --operator-code
```

## Docker

`192.168.47.81:/root/nginx/petshop` — `docker compose up -d --force-recreate petshop`

## 공식 문서

- [Runtime API Security Detections — BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security)
- [Setting Up API Protection](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-protection)
