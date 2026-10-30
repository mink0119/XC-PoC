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

고객이 “BOLA”라고 부르는 요구에는 **두 문제가 섞여 있다. 반드시 분리한다.**

| 구분 | 의미 | 이 랩에서의 대응 |
|------|------|------------------|
| **P1 객체 BOLA** | 인증 주체가 권한 없는 객체(계좌/주문 등)에 접근 | 교차 객체 조회, Body 필드 객체 조회 |
| **P2 식별·오탐** | 다중 ID / IP 변경 / 토큰 재발급을 공격으로 오인하지 않는지 | 순환·고정·토큰 재발급 + operator_code ON/OFF |
| **P3 이상행위** | 정상 순환과 다른 탐색·주문 패턴 | 정상 순환 직후 타인 객체 연속 탐색 등 |

IP 변경 자체는 BOLA가 아니다. BOLA는 **권한 없는 객체 접근**이다.

## 3. 제품 범위

### In scope (이 저장소)

- **Pet Shop** = 대상 API. 기본은 취약(소유권 미검사)해 XC BOLA PoC가 200 유출을 관찰한다.
  - **정상 API 모드**: `ENFORCE_OWNERSHIP=1` 또는 요청 헤더 `X-Enforce-Ownership: 1` → JWT 주체와 객체 소유자(인메모리 저장소)를 비교해 401/403.
  - 고객 실명·증권 도메인 명칭은 UI/코드에 넣지 않는다.
- **로컬 공격 실행기** (`scenarios/serve_lab.py`, `run_bola.py`) = 트래픽 생성·라벨·요청/응답 로그.
- XC가 학습·탐지할 **정상/공격 패턴 재현**.
- Body에 들어가는 **Private Resource 유사 필드** (`accountNo`) 검증용 API.
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

- 공격 GUI는 **절대** Pet Shop 호스트에 두지 않는다. `/lab`은 안내만.
- 대상 서버는 CORS를 허용해 로컬 브라우저 실행을 지원한다.

## 5. 시나리오 맵 (P1–P6)

| ID | 그룹 | 랩 시나리오 키 | 기대 라벨 | 검증 질문 |
|----|------|----------------|-----------|-----------|
| P1a | P1 BOLA | `cross_customer_bola` | bola | Path 객체 교차 접근을 잡는가? |
| P1b | P1 BOLA | `account_body_bola` | bola | **Request Body**의 `accountNo`를 Private Resource로 보는가? |
| P1c | P1 BOLA | `id_enumeration` | bola | 연속 ID 열거를 이상/BOLA로 보는가? |
| P2a | P2 오탐 | `operator_cyclic` | benign | 다계정 순환을 공격으로 오인하지 않는가? |
| P2b | P2 오탐 | `operator_fixed` | benign | 동일 계정·IP 변경을 오인하지 않는가? |
| P2c | P2 오탐 | `access_token_reissue` | benign | 24h 토큰 재발급을 신규 공격자로 보지 않는가? |
| P2d | P2 오탐 | `operator_code` 토글 | — | Claim 없을 때(현재) vs 있을 때(미래) 비교 |
| P3a | P3 이상 | `abnormal_probe` | mixed | 정상 자기조회 후 타인 객체 급탐색을 구분하는가? |
| — | baseline | `public_catalog`, `self_order` | benign | 베이스라인 |
| P4–P6 | 문서 | — | — | Discovery·민감정보·Inline 차단은 XC/별도 Inline 환경. 랩은 민감 필드가 든 응답을 **제공**만 함 |

### 학습 기간

BOLA/행위 분석은 **학습 트래픽·시간이 필요**하다.  
시나리오를 돌린 직후 XC에 이벤트가 없다고 해서 “미지원”으로 단정하지 않는다. UI에 이 문구를 유지한다.

## 6. 데이터·명명 규칙

- 제품/UI/로그에 특정 증권사·고객사 명칭을 넣지 않는다.
- 대리 모델: Pet Shop `customer_id`, `order`, `accountNo`(계좌 번호 유사 Private Resource).
- JWT: `customer_id` 필수, `operator_code`는 **옵션(기본 OFF = 현재형 오탐 세계)**.
- 로컬 라벨 `benign`/`bola`는 러너 전용. API 응답에 라벨을 심지 않는다.

## 7. UX 원칙 (로컬 GUI)

1. 시나리오는 **P1 / P2 / P3 / 기본** 그룹으로 나열.
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

## 11. 갭 대비 로드맵 (이 PRD 기준)

| 상태 | 항목 |
|------|------|
| Done | 로컬 GUI/CLI, P1 path BOLA, P2 cyclic/fixed/token, operator_code, HTTP 로그 |
| Now | PRD 고정, Body `accountNo` BOLA(P1b), P3 abnormal_probe, UI 그룹·학습 안내 |
| Next | 민감정보 패턴용 응답 필드 보강, Discovery 대조용 endpoint 목록 export, Inline 체크리스트 문서 |

## 12. 참고

- 내부: `docs/SCENARIOS.md`, `README.md`
- F5: Runtime API Security / BOLA, BIG-IP OOB API Discovery (공식 문서 — 버전·지원 범위는 PoC 시점에 재확인)
