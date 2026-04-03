# Construction-Project-Planning-Master-MCP

**건설/건축 공사 사업계획을 AI와 함께 만듭니다**
**Plan Korean construction projects with AI assistance**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-orange.svg)](https://github.com/jlowin/fastmcp)

---

## 소개 | Introduction

CivilPlan MCP는 한국 토목/건축 사업의 **기획 단계 전 과정**을 AI가 지원하는 MCP(Model Context Protocol) 서버입니다. Claude, ChatGPT 등 AI 에이전트가 이 서버의 도구를 호출하여 사업비 산출, 법적 절차 확인, 도면 생성 등을 자동으로 수행합니다.

CivilPlan MCP is a FastMCP server that helps AI agents (Claude, ChatGPT, etc.) plan Korean civil engineering and building projects. It automates cost estimation, legal procedure identification, drawing generation, and more -- all through the MCP protocol.

> **철학 | Philosophy**: 제4의길-AI와 함께 새로운 세상을 만들어갑니다.  -- 전문 기획 지식에 대한 접근 불평등을 줄입니다.
> Reduce inequality in access to expert planning knowledge. Free to use, modify, and distribute.
<img width="765" height="531" alt="image" src="https://github.com/user-attachments/assets/78c2fc86-059e-44d4-91f5-b821de7fa180" />
<img width="757" height="689" alt="image" src="https://github.com/user-attachments/assets/bbd063b8-106b-442d-89f7-15ef45796fe4" />
<img width="623" height="770" alt="image" src="https://github.com/user-attachments/assets/bfd7b157-3ce4-4cb6-8e38-91ec79b37234" />
<img width="616" height="718" alt="image" src="https://github.com/user-attachments/assets/6c901740-a3d8-427e-80f5-f756b2b27a63" />
<img width="655" height="444" alt="image" src="https://github.com/user-attachments/assets/8fe258ff-ac8a-4693-bab5-505edc18fe5c" />
<img width="732" height="703" alt="image" src="https://github.com/user-attachments/assets/a46a310e-dc41-44f3-b521-c54f4b07036b" />
<img width="900" height="845" alt="image" src="https://github.com/user-attachments/assets/0c2b6dde-e63f-4bf5-8253-a7ec8fb7edbe" />
<img width="686" height="533" alt="image" src="https://github.com/user-attachments/assets/2a26a518-57c6-45cd-a711-9358d27d05fc" />
<img width="651" height="321" alt="image" src="https://github.com/user-attachments/assets/728b0d1d-e525-48e4-9cc8-6be6d0eee0e1" />
<img width="926" height="598" alt="image" src="https://github.com/user-attachments/assets/99140321-1533-40a0-b989-c657fc798d21" />
<img width="1082" height="631" alt="image" src="https://github.com/user-attachments/assets/088a8038-a23b-4d3f-96d1-9f748deb56cb" />
---

## 이런 분들에게 유용합니다 | Who Is This For?

| 대상 | 활용 예시 |
|------|----------|
| **지자체 공무원** | 도로/상하수도 사업 기획 시 개략 사업비와 인허가 절차를 빠르게 파악 |
| **건설 엔지니어** | 기획 단계 물량/단가 산출, 투자계획서 초안 작성 자동화 |
| **부동산 개발 기획자** | 개발 사업의 법적 절차, 영향평가 대상 여부 확인 |
| **건축주/시행사** | AI에게 자연어로 사업 설명 -> 구조화된 사업 계획 문서 일괄 생성 |
| **학생/연구자** | 한국 건설 법령/표준품셈 학습 및 시뮬레이션 |

| Who | Use Case |
|-----|----------|
| **Local government officials** | Quickly estimate project costs and permits for road/water projects |
| **Civil engineers** | Automate preliminary quantity takeoff, unit pricing, and investment reports |
| **Real estate developers** | Identify legal procedures and impact assessments for development projects |
| **Project owners** | Describe a project in natural language -> get structured planning documents |
| **Students & researchers** | Learn Korean construction law, standard specifications, and cost estimation |

---

## 주요 기능 | Key Features

### 19개 AI 도구 | 19 AI Tools

CivilPlan은 사업 기획의 전 과정을 커버하는 19개 도구를 제공합니다:

| # | 도구 Tool | 설명 Description |
|---|-----------|-----------------|
| 1 | `civilplan_parse_project` | 자연어 사업 설명 -> 구조화된 사업 정보 추출 / Parse natural language project description |
| 2 | `civilplan_get_legal_procedures` | 사업 유형/규모별 법적 절차 자동 산출 / Identify applicable legal procedures |
| 3 | `civilplan_get_phase_checklist` | 사업 단계별 체크리스트 생성 / Generate phase-specific checklists |
| 4 | `civilplan_evaluate_impact_assessments` | 9종 영향평가 대상 여부 판단 / Evaluate 9 types of impact assessments |
| 5 | `civilplan_estimate_quantities` | 표준 횡단면 기반 개략 물량 산출 / Estimate quantities from standard cross-sections |
| 6 | `civilplan_get_unit_prices` | 공종별 단가 조회 (지역계수 반영) / Query unit prices with regional factors |
| 7 | `civilplan_generate_boq_excel` | 사업내역서(BOQ) Excel 생성 / Generate BOQ spreadsheet |
| 8 | `civilplan_generate_investment_doc` | 투자계획서(사업계획서) Word 생성 / Generate investment plan document |
| 9 | `civilplan_generate_schedule` | 사업 추진 일정표 (간트차트형) 생성 / Generate project schedule |
| 10 | `civilplan_generate_svg_drawing` | 개략 도면 SVG 생성 (평면도, 횡단면도) / Generate SVG drawings |
| 11 | `civilplan_get_applicable_guidelines` | 적용 기준/지침 조회 / Get applicable guidelines |
| 12 | `civilplan_fetch_guideline_summary` | 기준/지침 요약 조회 / Fetch guideline summaries |
| 13 | `civilplan_select_bid_type` | 발주 방식 선정 / Select bid type |
| 14 | `civilplan_estimate_waste_disposal` | 건설폐기물 처리비 산출 / Estimate waste disposal costs |
| 15 | `civilplan_query_land_info` | 토지 정보 조회 (PNU, 용도지역) / Query land info |
| 16 | `civilplan_analyze_feasibility` | 사업 타당성 분석 / Analyze project feasibility |
| 17 | `civilplan_validate_against_benchmark` | 유사 사업비 벤치마크 검증 / Validate against benchmarks |
| 18 | `civilplan_generate_budget_report` | 예산 보고서 생성 / Generate budget report |
| 19 | `civilplan_generate_dxf_drawing` | DXF 도면 생성 (CAD 호환) / Generate DXF drawings |

### 지원 사업 분야 | Supported Project Domains

- `건축` -- 건축물 (Buildings)
- `토목_도로` -- 도로 (Roads)
- `토목_상하수도` -- 상하수도 (Water & Sewerage)
- `토목_하천` -- 하천 (Rivers)
- `조경` -- 조경 (Landscaping)
- `복합` -- 복합 사업 (Mixed projects)

### 출력 형식 | Output Formats

- **Excel (.xlsx)**: 사업내역서(BOQ), 일정표, 예산 보고서
- **Word (.docx)**: 투자계획서(사업계획서)
- **SVG**: 평면도, 횡단면도, 종단면도
- **DXF**: CAD 호환 도면
- **JSON**: 모든 도구의 구조화된 응답 데이터

---

## 빠른 시작 가이드 | Quick Start Guide

### 1단계: 설치 | Step 1: Install

```bash
# 저장소 클론 | Clone the repository
git clone https://github.com/sinmb79/Construction-project-master.git
cd Construction-project-master

# 가상환경 생성 및 활성화 | Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 패키지 설치 | Install dependencies
pip install -r requirements.txt
```

### 2단계: API 키 설정 | Step 2: Configure API Keys

일부 도구(토지 정보 조회 등)는 공공 API 키가 필요합니다. 없어도 대부분의 기능은 동작합니다.

Some tools (land info queries, etc.) require public API keys. Most features work without them.

**방법 A: `.env` 파일 | Option A: `.env` file**

```bash
# .env.example을 복사하여 키를 입력합니다
# Copy .env.example and fill in your keys
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux
```

`.env` 파일을 편집하여 키를 입력하세요:

```env
# 공공데이터포털 (https://www.data.go.kr) 에서 발급
DATA_GO_KR_API_KEY=your_key_here

# 브이월드 (https://www.vworld.kr) 에서 발급
VWORLD_API_KEY=your_key_here
```

**방법 B: 암호화 저장 | Option B: Encrypted local storage**

```bash
# 대화형으로 키 입력 | Enter keys interactively
python setup_keys.py

# 또는 기존 .env 파일을 암호화 저장소로 가져오기
# Or import from existing .env file
python setup_keys.py --from-env-file .env
```

> Windows에서는 DPAPI를 사용하여 현재 사용자 프로필에 암호화 저장됩니다.
> On Windows, keys are encrypted with DPAPI under your user profile.

### 3단계: 서버 실행 | Step 3: Start the Server

```bash
python server.py
```

서버가 `http://127.0.0.1:8765/mcp`에서 시작됩니다.

The server starts at `http://127.0.0.1:8765/mcp`.

### 4단계: AI 클라이언트 연결 | Step 4: Connect Your AI Client

#### Claude Desktop

`claude_desktop_config.json` (또는 설정 파일)에 다음을 추가하세요:

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "civilplan": {
      "command": "mcp-remote",
      "args": ["http://127.0.0.1:8765/mcp"]
    }
  }
}
```

#### Claude Code (CLI)

```bash
claude mcp add civilplan http://127.0.0.1:8765/mcp
```

#### ChatGPT (Developer Mode)

ChatGPT는 localhost에 직접 연결할 수 없습니다. ngrok 또는 Cloudflare Tunnel을 사용하세요.

ChatGPT cannot connect to localhost directly. Use ngrok or Cloudflare Tunnel:

```bash
# ngrok으로 서버를 외부에 노출
ngrok http 8765
```

생성된 HTTPS URL을 ChatGPT 설정 -> Connectors -> Create에 입력합니다.

Use the generated HTTPS URL in ChatGPT Settings -> Connectors -> Create.

---

## 실전 사용 예시 | Real-World Usage Examples

### 예시 1: 소로 개설(신설) 공사 기획 | Example 1: Planning a New Local Road

아래는 실제로 CivilPlan MCP를 사용하여 생성한 예시입니다.

Below is a real example generated using CivilPlan MCP.

#### AI에게 이렇게 말하세요 | Say this to your AI:

```
소로 신설 L=890m B=6m 아스콘 2차선 상하수도 경기도 둔턱지역 2026~2028
```

#### CivilPlan이 자동으로 수행하는 작업 | What CivilPlan does automatically:

**1) 사업 정보 파싱 | Project Parsing** (`civilplan_parse_project`)

자연어 입력을 구조화된 데이터로 변환합니다:

```json
{
  "project_id": "PRJ-20260402-001",
  "project_type": ["도로", "상수도", "하수도"],
  "road": {
    "class": "소로",
    "length_m": 890,
    "width_m": 6.0,
    "lanes": 2,
    "pavement": "아스콘"
  },
  "terrain": "구릉(둔턱)",
  "terrain_factor": 1.4,
  "region": "경기도",
  "region_factor": 1.05,
  "year_start": 2026,
  "year_end": 2028,
  "utilities": ["상수도", "하수도"]
}
```

**2) 개략 물량 산출 | Quantity Estimation** (`civilplan_estimate_quantities`)

표준 횡단면 기준으로 주요 물량을 자동 산출합니다:

```
도로 포장: 아스콘 표층 523t, 기층 628t
토공:      절토 8,000m3, 성토 5,400m3
배수:      L형측구 1,780m, 횡단암거 60m
상수도:    PE관 DN100 890m, 소화전 3개소
하수도:    오수관 890m, 우수관 890m, 맨홀 37개소
```

**3) 사업비 산출 | Cost Estimation** (`civilplan_generate_boq_excel`)

6개 시트로 구성된 사업내역서 Excel 파일을 생성합니다:

| 시트 Sheet | 내용 Contents |
|-----------|--------------|
| 사업개요 | 프로젝트 정보, 면책문구 |
| 사업내역서(BOQ) | 8개 대공종별 수량 x 단가 = 금액 (수식 포함) |
| 물량산출근거 | 공종별 계산식 (예: 아스콘 표층 = 4,450m2 x 0.05m x 2.35t/m3) |
| 간접비산출 | 설계비 3.5%, 감리비 3.0%, 부대비 2.0%, 예비비 10% |
| 총사업비요약 | 직접공사비 + 간접비 = **약 10.67억원** |
| 연도별투자계획 | 2026: 30%, 2027: 50%, 2028: 20% |

**4) 법적 절차 확인 | Legal Procedures** (`civilplan_get_legal_procedures`)

18개 법적 절차를 자동으로 식별하고, 필수/선택 여부, 소요 기간, 근거 법령을 제공합니다:

```
필수 절차 12건, 선택 절차 6건
예상 인허가 소요: 약 18개월
핵심 경로: 도시계획시설결정 -> 개발행위허가 -> 실시계획인가
```

**5) 영향평가 판단 | Impact Assessments** (`civilplan_evaluate_impact_assessments`)

9종 영향평가 대상 여부를 자동 판단합니다:

| 평가 항목 | 대상 여부 | 근거 |
|----------|----------|------|
| 예비타당성조사 | 비대상 | 총사업비 500억 미만 |
| 지방재정투자심사 | **대상** | 총사업비 10.7억 > 10억 |
| 소규모환경영향평가 | **검토 필요** | 개발면적 5,340m2 |
| 재해영향평가 | **경계선** | 개발면적 5,000m2 이상 |
| 매장문화재 지표조사 | **검토 필요** | 개발면적 3,000m2 이상 |

**6) 도면 생성 | Drawing Generation** (`civilplan_generate_svg_drawing`)

평면도와 횡단면도를 SVG 형식으로 생성합니다:
- **평면도**: 도로 중심선, 측점, 관로 배치, 지형(둔턱) 표시, 구조물 위치
- **횡단면도**: 포장 단면(표층->기층->보조기층->동상방지층), 절토/성토 비탈면, 매설 관로

**7) 투자계획서 | Investment Document** (`civilplan_generate_investment_doc`)

위 모든 결과를 종합하여 Word 투자계획서를 자동 생성합니다:

```
표지
목차
제1장 사업 개요 (목적, 위치, 기간)
제2장 사업 규모 및 내용 (도로 현황, 부대시설, 지형)
제3장 사업비 산출 (BOQ 요약, 간접비, 연도별 투자계획)
제4장 법적 절차 및 추진 일정
제5장 기대 효과 및 결론
별첨: 위치도, 횡단면도
```

### 예시 2: 단가 조회 | Example 2: Unit Price Query

```
경기도 지역의 포장 관련 단가를 알려줘
```

AI가 `civilplan_get_unit_prices`를 호출하여 지역계수가 반영된 단가를 조회합니다:

```json
{
  "item": "아스콘표층(밀입도13mm)",
  "spec": "t=50mm",
  "unit": "t",
  "base_price": 96000,
  "region_factor": 1.05,
  "adjusted_price": 100800,
  "source": "조달청 표준시장단가 2026 상반기"
}
```

### 예시 3: 단계별 체크리스트 | Example 3: Phase Checklist

```
도로 공사 단계에서 해야 할 의무사항을 알려줘
```

AI가 `civilplan_get_phase_checklist`를 호출합니다:

```
[필수] 착공신고 -- 건설산업기본법 제39조, 착공 전
       미이행 시 500만원 이하 과태료
[필수] 품질시험계획 수립 -- 미제출 시 기성 지급 불가
[필수] 안전관리계획 수립/인가
...
```

---

## 시스템 아키텍처 | System Architecture

```
Claude / ChatGPT / AI Agent
      |  MCP Protocol (Streamable HTTP)
      v
+------------------------------------------+
|        CivilPlan MCP (FastMCP)           |
|                                          |
|  parse_project          -> JSON          |
|  get_legal_procedures   -> JSON          |
|  evaluate_impact        -> JSON          |
|  estimate_quantities    -> JSON          |
|  generate_boq_excel     -> .xlsx         |
|  generate_investment    -> .docx         |
|  generate_schedule      -> .xlsx         |
|  generate_svg_drawing   -> .svg          |
|  generate_dxf_drawing   -> .dxf          |
|  ... (19 tools total)                    |
+--------------------+---------------------+
                     |
              +------v------+     +--------------+
              |  SQLite DB  |     |  JSON Data   |
              | unit_prices |     | legal_procs  |
              | legal_procs |     | region_facts |
              | project_log |     | road_stds    |
              +-------------+     +--------------+
```

---

## 프로젝트 구조 | Project Structure

```
Construction-project-master/
|-- server.py                  # 메인 서버 진입점 | Main server entry point
|-- setup_keys.py              # API 키 설정 도구 | API key setup utility
|-- pyproject.toml             # 프로젝트 메타데이터 | Project metadata
|-- requirements.txt           # 의존성 목록 | Dependencies
|-- .env.example               # 환경변수 템플릿 | Environment template
|-- LICENSE                    # MIT 라이선스 | MIT License
|
|-- civilplan_mcp/             # 메인 패키지 | Main package
|   |-- server.py              # FastMCP 서버 정의 | FastMCP server definition
|   |-- config.py              # 설정, 경로, 상수 | Config, paths, constants
|   |-- models.py              # Pydantic 모델 | Pydantic models
|   |-- secure_store.py        # 암호화 키 저장 | Encrypted key storage
|   |-- tools/                 # 19개 MCP 도구 구현 | 19 MCP tool implementations
|   |-- data/                  # JSON 참조 데이터 | JSON reference data
|   |-- db/                    # SQLite 스키마 및 시드 | SQLite schema & seeds
|   +-- updater/               # 자동 데이터 갱신 | Automated data updaters
|
+-- tests/                     # 테스트 스위트 | Test suite
    |-- test_smoke.py          # 기본 동작 확인 | Basic smoke tests
    |-- test_parser.py         # 파서 테스트 | Parser tests
    |-- test_legal.py          # 법적 절차 테스트 | Legal procedure tests
    |-- test_quantities.py     # 물량 산출 테스트 | Quantity tests
    |-- test_generators.py     # 파일 생성 테스트 | Generator tests
    +-- ...                    # 기타 테스트 | Other tests
```

---

## 데이터 자동 갱신 | Automated Data Updates

CivilPlan은 단가/임금/폐기물 처리비 등 참조 데이터의 정기 갱신을 지원합니다:

CivilPlan supports scheduled updates for reference data (wages, prices, waste rates):

| 시기 Timing | 갱신 항목 Update Item |
|------------|---------------------|
| 1월 2일 09:00 | 상반기 임금, 폐기물 처리비, 간접비율 |
| 7월 10일 09:00 | 하반기 표준시장단가, 간접비율 |
| 9월 2일 09:00 | 하반기 임금 |

갱신 실패 시 `.update_required_*` 플래그 파일이 생성되고, 서버 시작 시 경고가 표시됩니다.

If an update fails, `.update_required_*` flag files are created and startup warnings are shown.

---

## 토지 정보 데이터 설정 | Land Price Data Setup

토지 가격 조회 기능을 사용하려면 수동으로 데이터를 다운로드해야 합니다:

To use land price lookup, manually download data files:

1. 국토교통부 또는 한국부동산원에서 공시지가 CSV/TSV 파일 다운로드
2. `civilplan_mcp/data/land_prices/` 폴더에 넣기
3. UTF-8, CP949, EUC-KR 인코딩 모두 지원

```
civilplan_mcp/data/land_prices/
  (여기에 CSV/TSV/ZIP 파일을 넣으세요)
  (Place your CSV/TSV/ZIP files here)
```

---

## 테스트 실행 | Running Tests

```bash
pytest tests -q
```

모든 테스트는 외부 API 키 없이도 실행 가능합니다 (로컬 폴백 사용).

All tests run without external API keys (using local fallbacks).

---

## 알려진 제한사항 | Known Limitations

- **개략 산출**: 모든 사업비/물량은 기획 단계용 개략 산출이며, 실시설계를 대체하지 않습니다 (+-20~30% 오차 가능).
  *All estimates are preliminary (+-20-30% variance) and do not replace detailed design.*

- **토지 용도 데이터**: 외부 서비스 불안정으로 일부 필지의 용도지역 정보가 불완전할 수 있습니다.
  *External land-use services can be unstable; some parcels may return partial zoning data.*

- **공시지가 조회**: 수동 다운로드 필요 (`civilplan_mcp/data/land_prices/`).
  *Land price lookup requires manually downloaded source files.*

- **나라장터 벤치마크**: 공공 API가 불안정하여 로컬 휴리스틱으로 폴백합니다.
  *Nara benchmark validation falls back to local heuristics when the public API is unavailable.*

- **조경 분야**: 법적 절차 데이터가 아직 완전하지 않습니다.
  *Landscape-specific legal/procedure data is not fully implemented yet.*

---

## 면책 조항 | Disclaimer

> 본 도구의 산출 결과는 **기획 단계 참고용**이며, 실시설계/시공을 위한 공식 문서로 사용할 수 없습니다.
> 실제 사업 집행 시에는 반드시 관련 분야 전문가의 검토를 받으시기 바랍니다.
>
> All outputs are for **preliminary planning reference only** and cannot be used as official documents for detailed design or construction.
> Please consult qualified professionals before executing any actual project.

---

## 라이선스 | License

MIT License -- 자유롭게 사용, 수정, 배포할 수 있습니다.

MIT License -- Free to use, modify, and distribute.

---

## 만든 사람 | Author

**22B Labs** (sinmb79)

문의사항이나 기여는 [Issues](https://github.com/sinmb79/Construction-project-master/issues)를 이용해 주세요.

For questions or contributions, please use [Issues](https://github.com/sinmb79/Construction-project-master/issues).
