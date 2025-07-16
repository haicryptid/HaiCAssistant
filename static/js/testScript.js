const micButton = document.getElementById("mic-button");
const micImg = document.getElementById("mic-img");
const answerBox = document.getElementById("answer");
const questionBox = document.getElementById("question");
const textInput = document.getElementById("text-input");    // 이 부분 꼭 추가!
const textSubmit = document.getElementById("text-submit");  // 이 부분 꼭 추가!

const recognition = new webkitSpeechRecognition(); // Chrome 기준
recognition.lang = "ko-KR";
recognition.interimResults = false;
recognition.continuous = false;

micButton.addEventListener("click", () => {
  recognition.start();
  micImg.src = "/static/assets/onMic.png";
  questionBox.textContent = "듣고 있어요...";
  answerBox.textContent = ""; // 답변 초기화
});

recognition.onresult = (event) => {
  const text = event.results[0][0].transcript;
  questionBox.textContent = `당신: ${text}`;

  micImg.src = "/static/assets/offMic.png";

  // Flask 서버에 질문 전송
  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: text })
  })
    .then((res) => res.json())
    .then((data) => {
      answerBox.textContent = `AI: ${data.answer}`;
      speak(data.answer);
    })
    .catch((err) => {
      console.error("서버 오류:", err);
      answerBox.textContent = "서버와 연결할 수 없어요.";
    });
};

recognition.onerror = (event) => {
  console.error("음성 인식 오류:", event.error);
  answerBox.textContent = "음성 인식에 실패했어요.";
  micImg.src = "/static/assets/offMic.png";
};

textSubmit.addEventListener("click", () => {
  const inputText = textInput.value.trim();
  if (!inputText) return;

  questionBox.textContent = `당신: ${inputText}`;
  answerBox.textContent = ""; // 이전 답변 초기화

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: inputText })
  })
    .then((res) => res.json())
    .then((data) => {
      answerBox.textContent = `AI: ${data.answer}`;
      speak(data.answer);
    })
    .catch((err) => {
      console.error("서버 오류:", err);
      answerBox.textContent = "서버와 연결할 수 없어요.";
    });
});

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "ko-KR";
  speechSynthesis.speak(utterance);
}
