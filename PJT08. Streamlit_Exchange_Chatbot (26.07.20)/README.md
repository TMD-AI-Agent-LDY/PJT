# LangChain 미니 프로젝트: 실시간 환율 챗봇 만들기

## 프로젝트 소개

이전에 만들었던 **Frankfurter 환율 조회 웹앱**을 대화형 챗봇으로 발전시키시오.

이번에는 사용자가 기준 통화와 금액을 직접 선택하지 않습니다.
`"100달러는 원화로 얼마야?"`처럼 자연어로 질문하면 챗봇이 통화와 금액을 파악하고, 필요한 환율을 조회한 뒤 결과를 알려줘야 합니다.

이 과정에서 LangChain의 도구(Tool), 에이전트(Agent), 대화 메모리를
활용하시오.

### 참고 문서

- Frankfurter: https://frankfurter.dev/
- API 기본 주소: `https://api.frankfurter.dev`
- 단일 환율 조회: `GET /v2/rate/{base}/{quote}`
- LangChain Agents: https://docs.langchain.com/oss/python/langchain/agents
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- LangChain Short-term memory:
  https://docs.langchain.com/oss/python/langchain/short-term-memory


## 제출 파일

`MiniPJT` 폴더에 다음 파일을 작성하세요.

```text
MiniPJT/
├── README.md
├── app.py
├── requirements.txt
└── .env.example
```

실제 API 키가 들어 있는 `.env` 파일은 제출하거나 Git에 올리면 안 됩니다.

## 필수 요구사항

### 1. 환경 변수와 모델 설정

`python-dotenv`의 `load_dotenv()`로 환경 변수를 불러옵니다.

```dotenv
OPENAI_API_KEY=your_openai_api_key_here
```

- API 키를 코드에 직접 적지 마세요.
- `OPENAI_API_KEY`가 없을 때는 오류 메시지를 보여주고 채팅 입력창을 비활성화합니다.

### 2. 채팅 화면 만들기

Streamlit으로 다음과 같은 채팅 화면을 만드세요.

- 화면 상단에 `실시간 환율 챗봇`이라는 제목을 표시합니다.
- `st.chat_message()`로 사용자와 AI의 메시지를 구분합니다.
- `st.chat_input()`으로 질문을 입력받습니다.

다음과 같이 질문할 수 있어야 합니다.

```text
100달러는 원화로 얼마야?
1유로는 엔화로 얼마야?
영국 파운드 50은 캐나다 달러로 얼마야?
```

### 3. 환율 조회 도구 만들기

`@tool` 데코레이터를 사용해 환율 조회 도구를 만드세요. 

함수에는 타입 힌트와 docstring을 반드시 작성하세요. 에이전트는 함수 이름과 타입 힌트, docstring을 보고 이 도구를 언제 어떻게 사용할지 판단합니다.

환율은 다음 주소에서 조회합니다.

```text
https://api.frankfurter.dev/v2/rate/{base_currency}/{quote_currency}
```


### 4. 앞선 대화 기억하기

사용자가 짧게 이어서 질문해도 앞선 대화의 통화 정보를 기억하도록 만드세요.

완성된 챗봇에서는 아래와 같이 대화할 수 있습니다.

```text
사용자: 100달러는 원화로 얼마야?
AI: ...
사용자: 그럼 250달러는?
AI: 앞에서 이야기한 달러와 원화의 환율을 다시 조회해 답변
```

## 완성 후 확인하기

- [ ] 질문과 답변이 채팅 형태로 표시되는가?
- [ ] API 키가 코드에 노출되지 않았는가?
- [ ] 환율 조회 도구에 타입 힌트와 docstring을 작성했는가?
- [ ] 환율 질문을 받을 때마다 Frankfurter API를 호출하는가?
- [ ] 한국어와 영어 통화 이름을 올바른 통화 코드로 바꾸는가?
- [ ] 답변에 환율, 환산 금액, 통화 코드, 기준일이 포함되는가?
- [ ] `"그럼 250달러는?"`과 같은 후속 질문을 이해하는가?
- [ ] 같은 통화, 음수 금액, 잘못된 통화, API 오류를 처리하는가?

## 추가 도전

필수 기능을 모두 완성했다면 아래 기능도 구현해 보세요.

- `st.write_stream()`을 이용한 답변 스트리밍
- 여러 대화방 만들기와 대화방 전환
- 사용자가 지정한 과거 날짜의 환율 조회
- LangSmith를 이용한 도구 호출 과정 추적
