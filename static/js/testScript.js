const micButton = document.getElementById("mic-button");
const micImg = document.getElementById("mic-img");
const resultBox = document.getElementById("result");

const recognition = new webkitSpeechRecognition(); // Chrome 기준
recognition.lang = "ko-KR";
recognition.interimResults = false;
recognition.continuous = false;

micButton.addEventListener("click", () => {
  recognition.start();
  micImg.src = "/static/assets/onMic.png";
  resultBox.textContent = "듣고 있어요...";
});

recognition.onresult = (event) => {
  const text = event.results[0][0].transcript;
  resultBox.textContent = `당신: ${text}`;
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
      const answer = data.answer;
      resultBox.textContent += `\nAI: ${answer}`;
      speak(answer);
    })
    .catch((err) => {
      console.error("서버 오류:", err);
      resultBox.textContent = "서버와 연결할 수 없어요.";
    });
};

recognition.onerror = (event) => {
  console.error("음성 인식 오류:", event.error);
  resultBox.textContent = "음성 인식에 실패했어요.";
  micImg.src = "/static/assets/offMic.png";
};

recognition.onend = () => {
  micImg.src = "/static/assets/offMic.png";
};

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "ko-KR";
  speechSynthesis.speak(utterance);
}
const textInput = document.getElementById("text-input");
const textSubmit = document.getElementById("text-submit");

textSubmit.addEventListener("click", () => {
  const inputText = textInput.value.trim();
  if (!inputText) return;

  resultBox.textContent = `당신: ${inputText}`;

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: inputText })
  })
    .then((res) => res.json())
    .then((data) => {
      const answer = data.answer;
      resultBox.textContent += `\nAI: ${answer}`;
      speak(answer);
    })
    .catch((err) => {
      console.error("서버 오류:", err);
      resultBox.textContent = "서버와 연결할 수 없어요.";
    });
});
