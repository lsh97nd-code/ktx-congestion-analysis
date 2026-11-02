'use strict';

/*
 * KTX 예매난 위험도 분석 및 대체 이동수단 선택 AI 비서
 * frontend/js/app.js
 *
 * 연결 API
 * - POST /api/chat
 * - GET  /api/conversations
 */

const API_BASE_URL = 'http://127.0.0.1:8001';

const DATE_FORMATTER = new Intl.DateTimeFormat('ko-KR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

const elements = {
  chatForm: document.getElementById('chat-form'),
  messageInput: document.getElementById('message-input'),
  submitButton: document.getElementById('submit-button'),
  formMessage: document.getElementById('form-message'),

  loadingArea: document.getElementById('loading-area'),
  answerArea: document.getElementById('answer-area'),
  answerText: document.getElementById('answer-text'),
  conversationId: document.getElementById('conversation-id'),
  modelName: document.getElementById('model-name'),

  refreshButton: document.getElementById('refresh-conversations-button'),
  historyMessage: document.getElementById('history-message'),
  conversationList: document.getElementById('conversation-list'),
};

function setStatus(element, message = '', type = '') {
  element.textContent = message;
  element.classList.remove('error', 'success');

  if (type) {
    element.classList.add(type);
  }
}

function setChatLoading(isLoading) {
  elements.loadingArea.hidden = !isLoading;
  elements.submitButton.disabled = isLoading;
  elements.messageInput.disabled = isLoading;
  elements.submitButton.textContent = isLoading ? '분석 중...' : '질문하기';
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  return text ? { detail: text } : {};
}

function getErrorMessage(data, fallbackMessage) {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data.detail === 'string') {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => item?.msg || JSON.stringify(item))
      .join(' / ');
  }

  if (typeof data.message === 'string') {
    return data.message;
  }

  return fallbackMessage;
}

function getChatAnswer(data) {
  return (
    data.answer ??
    data.assistant_message ??
    data.response ??
    data.message ??
    'AI 답변을 받았지만 표시할 답변 필드를 찾지 못했습니다.'
  );
}

function getConversationId(data) {
  return data.conversation_id ?? data.id ?? '-';
}

function getModelName(data) {
  return data.model ?? data.model_name ?? '-';
}

async function submitChat(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `AI 요청에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

async function handleChatSubmit(event) {
  event.preventDefault();

  const message = elements.messageInput.value.trim();

  setStatus(elements.formMessage);
  elements.answerArea.hidden = true;

  if (!message) {
    setStatus(elements.formMessage, '질문을 입력해 주세요.', 'error');
    elements.messageInput.focus();
    return;
  }

  setChatLoading(true);

  try {
    const data = await submitChat(message);

    elements.answerText.textContent = getChatAnswer(data);
    elements.conversationId.textContent = getConversationId(data);
    elements.modelName.textContent = getModelName(data);
    elements.answerArea.hidden = false;

    setStatus(
      elements.formMessage,
      'AI 답변을 정상적으로 받았습니다.',
      'success'
    );

    /*
     * /api/chat이 Firestore에 대화를 자동 저장하므로,
     * 답변을 받은 뒤 최근 대화 목록도 자동으로 갱신합니다.
     */
    await loadConversations({ silent: true });
  } catch (error) {
    console.error('POST /api/chat 오류:', error);

    setStatus(
      elements.formMessage,
      `질문 처리 중 오류가 발생했습니다. ${error.message}`,
      'error'
    );
  } finally {
    setChatLoading(false);
  }
}

async function fetchConversations() {
  const response = await fetch(`${API_BASE_URL}/api/conversations`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `대화 목록 조회에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  /*
   * 현재 API가 배열을 직접 반환하는 경우를 기본으로 하되,
   * { conversations: [...] } 또는 { items: [...] } 형태도 허용합니다.
   */
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.conversations)) {
    return data.conversations;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  return [];
}

function formatDateTime(value) {
  if (!value) {
    return '시간 정보 없음';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return DATE_FORMATTER.format(date);
}

function createConversationCard(conversation) {
  const article = document.createElement('article');
  article.className = 'conversation-card';

  const question = document.createElement('p');
  question.className = 'conversation-question';
  question.textContent =
    conversation.user_message ??
    conversation.message ??
    '질문 내용 없음';

  const answer = document.createElement('p');
  answer.className = 'conversation-answer';
  answer.textContent =
    conversation.assistant_message ??
    conversation.answer ??
    conversation.response ??
    '답변 내용 없음';

  const meta = document.createElement('p');
  meta.className = 'conversation-meta';

  const id = conversation.id ?? conversation.conversation_id ?? '-';
  const createdAt = formatDateTime(conversation.created_at);

  meta.textContent = `대화 ID: ${id} · ${createdAt}`;

  article.append(question, answer, meta);

  return article;
}

function renderConversations(conversations) {
  elements.conversationList.replaceChildren();

  if (!conversations.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-message';
    empty.textContent = '저장된 대화가 없습니다.';
    elements.conversationList.appendChild(empty);
    return;
  }

  const getCreatedAtTime = (conversation) => {
    const time = new Date(conversation.created_at ?? 0).getTime();
    return Number.isNaN(time) ? Number.NEGATIVE_INFINITY : time;
  };

  const sorted = [...conversations].sort(
    (a, b) => getCreatedAtTime(b) - getCreatedAtTime(a)
  );

  const fragment = document.createDocumentFragment();

  sorted.forEach((conversation) => {
    fragment.appendChild(createConversationCard(conversation));
  });

  elements.conversationList.appendChild(fragment);
}

async function loadConversations({ silent = false } = {}) {
  elements.refreshButton.disabled = true;

  if (!silent) {
    setStatus(elements.historyMessage, '최근 대화를 불러오는 중입니다.');
  }

  try {
    const conversations = await fetchConversations();

    renderConversations(conversations);

    if (!silent) {
      const count = conversations.length;
      setStatus(
        elements.historyMessage,
        `최근 대화 ${count}건을 불러왔습니다.`,
        'success'
      );
    }
  } catch (error) {
    console.error('GET /api/conversations 오류:', error);

    setStatus(
      elements.historyMessage,
      `대화 목록을 불러오지 못했습니다. ${error.message}`,
      'error'
    );
  } finally {
    elements.refreshButton.disabled = false;
  }
}

function validateRequiredElements() {
  const missing = Object.entries(elements)
    .filter(([, element]) => !element)
    .map(([name]) => name);

  if (missing.length > 0) {
    const message = `필수 HTML 요소를 찾지 못했습니다: ${missing.join(', ')}`;
    console.error(message);

    const notice = document.createElement('p');
    notice.setAttribute('role', 'alert');
    notice.textContent =
      '화면 초기화 중 오류가 발생했습니다. 페이지를 새로고침해 주세요.';
    notice.style.cssText =
      'margin:16px;padding:12px;border:1px solid #c53b3b;border-radius:8px;color:#c53b3b;background:#fff0f0;';

    document.body.prepend(notice);
    return false;
  }

  return true;
}

function initializeApp() {
  if (!validateRequiredElements()) {
    return;
  }

  elements.chatForm.addEventListener('submit', handleChatSubmit);
  elements.refreshButton.addEventListener('click', () => {
    loadConversations();
  });

  /*
   * 페이지를 열면 Firestore 최근 대화 목록을 자동으로 한 번 조회합니다.
   */
  loadConversations();
}

document.addEventListener('DOMContentLoaded', initializeApp);
