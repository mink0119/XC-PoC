# PRD — XC BOLA / 이상행위 PoC Lab

최종 갱신: 2026-10-30  
제품 코드명: **XC-PoC** (Pet Shop 대리 모델)

## 1. 한 줄 목표

> 실제 Open API 운용 환경에서 **정상적인 다중 ID·IP·토큰 패턴**과 **비정상 객체 접근·탐색 행위**를 구분할 수 있는지, F5 XC가 OOB로 관찰 가능한 범위까지 검증할 수 있는 **로컬 트래픽 생성 랩**을 제공한다.

이 도구의 성공 지표는 “BOLA 화면 한 장”이 아니라 **식별 정확도 · 오탐 구분 · 근거 제시**다.

## 2. 배경 (고객 미팅에서 고정된 문제)

고객은 솔루션 기능 데모보다 아래를 본다.

| 우선 | 질문 |
|------|------|
| 1 | 정상 다중 ID 순환 vs 타 객체 비정상 접근을 가르는가? |
| 2 | 일 수백 건 경보를 “조사할 만한 것” 중심으로 줄일 수 있는가? |
| 3 | IP·토큰이 바뀌어도 동일 운용 주체로 추적 가능한가? |
| 4 | OOB(미러/BIG-IP 연계)에서 어디까지 보이는가? |

랩 시나리오는 **세 갈래**로만 둔다.

| 구분 | 의미 | 랩 키 |
|------|------|-------|
| **정상** | `customer_id` = path `/orders/{id}` | `normal_orders` |
| **공격** | `customer_id` ≠ path `/orders/{id}` | `attack_orders` |
| **운영사(정상·오탐)** | 계정 풀 순환 + 자기 주문 + **공유 IP** | `operator_orders` |

Body Private Resource(`accountNo`)는 추후. IP 변경 자체는 BOLA가 아니다.

## 3. 제품 범위

### In scope (이 저장소)

- **Pet Shop** = 대상 API. 기본은 취약(소유권 미검사)해 XC BOLA PoC가 200 유출을 관찰한다.
  - **정상 API 모드**: `ENFORCE_OWNERSHIP=1` 또는 요청 헤더 `X-Enforce-Ownership: 1` → JWT 주체와 객체 소유자(인메모리 저장소)를 비교해 401/403.
  - 고객 실명·증권 도메인 명칭은 UI/코드에 넣지 않는다.
- **로컬 공격 실행기** (`scenarios/serve_lab.py`, `run_bola.py`) = 트래픽 생성·라벨·요청/응답 로그.
- XC가 학습·탐지할 **정상/공격 패턴 재현**.
- Path `/orders/{id}` 매칭·불일치 트래픽. (Body `accountNo` 는 추후)
- PoC 엔지니어용 **시나리오 설명·흐름·예시**.

### Out of scope (이 랩이 직접 증명하지 않음)

- F5 XC / BIG-IP / CE 설치·라이선스·10G·20K TPS 성능.
- OOB에서 실제 차단(Inline 전용 기능).
- 실트래픽 미러링·마스킹 정책 구현.
- 고객 실계좌·실토큰 사용.

OOB vs Inline 역할은 README/시나리오 안내 문구로만 명시한다.  
**이 랩 = 트래픽·패턴 생성기.** 탐지 UI는 XC 콘솔에서 본다.

## 4. 아키텍처 원칙

```text
[로컬 PC]  scenarios/lab 또는 run_bola.py
    │  HTTP 시나리오 트래픽
    ▼
[Pet Shop]  대상 API (예: 192.168.47.81)
    ┊  (미러 / BIG-IP OOB / Inline CE — 고객 환경)
    ▼
[F5 XC]  Discovery · BOLA · 이상행위 분석
```

- 공격 GUI의 기본 위치는 **로컬**이다. Pet Shop의 `/lab`은 안내만.
- 공유 PoC 호스트에서는 **별도 포트(기본 8765) Docker**로 lab UI를 띄울 수 있다. Pet Shop(API :80)과 프로세스를 섞지 않는다.
- 대상 서버는 CORS를 허용해 브라우저에서 lab → API 호출을 지원한다.

## 5. 시나리오 맵

| 키 | 기대 | 검증 질문 |
|----|------|-----------|
| `normal_orders` | benign | 매칭 주문 + ≥50 XFF 정상 학습되는가? |
| `attack_orders` | bola | 불일치 주문(`/orders/{id}` only)을 BOLA로 보는가? |
| `operator_orders` | benign | 다계정·공유 IP를 공격으로 오인하지 않는가? |

라벨 판정: **오직** `JWT customer_id == order path id`. `operator_code`는 라벨에 쓰지 않는다.

### 학습 기간

BOLA/행위 분석은 **학습 트래픽·시간이 필요**하다.  
시나리오를 돌린 직후 XC에 이벤트가 없다고 해서 “미지원”으로 단정하지 않는다.

User Identification이 **IP**이면 정상/공격은 **계정마다 XFF 1:1**(기본 50). 운영사만 공유 IP 개수를 조절한다.

## 6. 데이터·명명 규칙

- 제품/UI/로그에 특정 증권사·고객사 명칭을 넣지 않는다.
- 대리 모델: Pet Shop `customer_id`, `order`, `accountNo`(계좌 번호 유사 Private Resource).
- JWT: `customer_id` 필수, `operator_code`는 **옵션(기본 OFF = 현재형 오탐 세계)**.
- 로컬 라벨 `benign`/`bola`는 러너 전용. API 응답에 라벨을 심지 않는다.

## 7. UX 원칙 (로컬 GUI)

1. 시나리오는 **정상 / 공격 / 운영사** 세 그룹만.
2. **선택한 시나리오에 필요한 옵션만** 표시.
3. 이름·설명은 엔지니어가 바로 이해하게 (정상·오탐 검토·공격).
4. HTTP 로그의 요청/응답 칸에는 **무슨 정보인지 제목**을 붙인다.
5. 흐름도·요청 예시는 시나리오 선택 시 갱신.

## 8. 비기능

- GUI: Python 표준 라이브러리만 (`serve_lab.py`).
- CLI: `requests` 선택.
- 요청/응답 전체 JSONL 기록 (PoC 검증용).

## 9. 명시적 비목표

- 앱 단에서 BOLA를 “막아 주는” 방어 구현 (방어는 XC).
- 실서비스 20K TPS 부하 재현.
- OOB에서 차단 성공을 이 랩만으로 증명.

## 10. 진행 원칙 (에이전트·인간 공통)

1. 기능 추가 전 **이 PRD의 P1/P2/P3 중 어디에 속하는지** 적는다.
2. 고객 실명·실API 경로를 코드에 넣지 않는다. 개념만 Pet Shop으로 이식한다.
3. OOB로 못 보는 기능은 Inline 필요라고 문서에 쓰고, 가짜로 “됨”이라고 하지 않는다.
4. UI 카피·시나리오 키·README·SCENARIOS는 PRD와 모순되지 않게 맞춘다.

## 11. F5 XC Code Base Integration (코드 스캔 Discovery) 정렬

이후 PoC에서 **Code Base Integration → Discovery Source = Code Analysis** 를 검증한다.  
대상 API(`petshop/`)는 공식 **Code Discovery 지원 언어·프레임워크**만 사용한다.

공식 기준 ([Setting Up API Discovery](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-security) · Code Discovery):

| Language | Frameworks |
|----------|------------|
| Java | EE, Spring |
| .NET | 7.0, 6.0, 5.0, 3.1 |
| **Python** | **Flask**, Django (**function-based views**만) |
| JavaScript | Express, Hapi |
| Go | Gin |

추가 제약 (공식·지원 문서):

- SCM: Azure Repos, GitHub (Standard/Enterprise), GitLab (Standard/Enterprise). 스캔은 **organization 레벨**.
- **TypeScript 미지원** — Discovery Source에 Code가 안 붙는 대표 원인 ([K000150399](https://my.f5.com/manage/s/article/K000150399)).
- Django는 **class-based views 제외** (function-based만).
- 저장소 스캔은 **최대 수 시간~일 1회** 주기. 즉시 Code 소스가 안 뜬다고 미지원으로 단정하지 않는다.

### 이 랩의 고정 선택

| 항목 | 결정 |
|------|------|
| 대상 API 스택 | **Python + Flask + function-based `@app.route`** (`petshop/flask_routes.py`) |
| 금지 | 대상 API를 FastAPI/Django CBV/Express-TS/Nest 등으로 바꿔 Code 스캔 비호환 만들기 |
| 라우트 가시성 | 엔드포인트는 `@app.route(..., methods=[...])` 로 정적 스캔 가능해야 함 (thin wrapper → `invoke` 유지 가능) |
| 스펙 병행 | OpenAPI(`/swagger.json`)는 Inventory·Import용. Code 스캔과 **별개** 소스 |
| 검증 기대 | LB에 Code Base Integration + API Repositories 연결 후 Inventory에서 `Discovery Source`에 **Code Analysis** 포함 |

트래픽 학습(BOLA/행위)과 Code Discovery는 **다른 Discovery Source**다. 둘 다 쓰되 혼동하지 않는다.

## 12. 갭 대비 로드맵 (이 PRD 기준)

| 상태 | 항목 |
|------|------|
| Done | 로컬 GUI/CLI, **normal/attack/operator** 3시나리오, XFF 규칙, HTTP 로그, Flask Code Discovery 스택 |
| Now | Body `accountNo` 시나리오(추후), Code Base Integration 실연동 체크리스트 |
| Next | 민감정보 패턴 응답 보강, Inline 체크리스트 문서 |

## 13. 참고

- 내부: `docs/SCENARIOS.md`, `README.md`
- F5: [Setting Up API Discovery](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/quickstart/api-security) (Code Discovery 표), [Runtime API Security / BOLA](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/concepts/owasp-api-security), [Import OpenAPI](https://docs.cloud.f5.com/docs-v2/web-app-and-api-protection/how-to/adv-security/import-openapi-spec)
- 지원 범위는 PoC 시점에 공식 문서 재확인.
