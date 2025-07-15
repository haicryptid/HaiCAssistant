const micButton = document.getElementById("mic-button");
const micImg = document.getElementById("mic-img");
const resultBox = document.getElementById("result");

const recognition = new webkitSpeechRecognition(); // Chrome 기준
recognition.lang = "ko-KR";
recognition.interimResults = false;
recognition.continuous = false;

micButton.addEventListener("click", () => {
  recognition.start();
  micImg.src = "/static/assets/onMic.png"; // 불 켜짐 상태로 변경
  resultBox.textContent = "듣고 있어요...";
});

recognition.onresult = (event) => {
  const text = event.results[0][0].transcript;
  resultBox.textContent = `당신: ${text}`;
  speak("네, 지금은 예시 응답이에요!");

  // 마이크 상태 끄기
  micImg.src = "/static/assets/offMic.png";
};

recognition.onerror = (event) => {
  console.error("음성 인식 오류:", event.error);
  resultBox.textContent = "음성 인식에 실패했어요.";
  micImg.src = "/static/assets/offMic.png";
};

recognition.onend = () => {
  micImg.src = "/static/assets/offMic.png"; // 인식 끝났을 때도 꺼짐
};

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "ko-KR";
  speechSynthesis.speak(utterance);
}
