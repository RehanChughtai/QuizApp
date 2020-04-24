var socket = io();
var params = jQuery.deparam(window.location.search);

var startButton = document.getElementById('start-btn')
var nextButton = document.getElementById('next-btn')
var finishButton = document.getElementById('finish-btn')
var backButton = document.getElementById('backButton') 
// var scoreBorder = document.getElementById('stats')
const questionContainerElement = document.getElementById('question-container')
const resultsElement = document.getElementById('results')
const questionElement = document.getElementById('question')
const answerButtonsElement = document.getElementById('answer-buttons')
const scoreFieldElement = document.getElementById('score')
const initialTime = 30

//When host connects to server
socket.on('connect', function() {
  //Tell server that it is host connection from game view
  socket.emit('getMyQuiz', params);
  backButton.classList.add('hide')
  scoreFieldElement.classList.remove('hide')
});

socket.on('initQuiz', function(data) {
  console.log(`initialising quiz: ${data}`)
  shuffledQuestions = data;
  startGame();
});


/**
 * Time up button - used to pass along to the select answer, to mimick a wrong answer selected
 */
const timeUpButtonElement = document.createElement('button')
timeUpButtonElement.innerText = "TimeIsUp"
timeUpButtonElement.classList.add('btn')
timeUpButtonElement.dataset.correct = false

let shuffledQuestions, currentQuestionIndex, x
var score = 0

/**
 * Count down bar controller
 */
function progress(timeleft, timetotal, $element) {
  var progressBarWidth = timeleft * $element.width() / timetotal;
  $element.find('div').animate({ width: progressBarWidth }, 500).html(Math.floor(timeleft/60) + ":"+ timeleft%60);
  if(timeleft > 0) {
      x = setTimeout(function() {
          progress(timeleft - 1, timetotal, $element);
      }, 1000);
  } else {
    console.log(`Time is up!`)
    doStuff(timeUpButtonElement)
  }
};

// This is where you can configure total time etc 
progress(initialTime, initialTime, $('#progressBar'));

startButton.addEventListener('click', startGame)
nextButton.addEventListener('click', () => {
  currentQuestionIndex++
  setNextQuestion()
  // this is also where you need to configure total time etc
  progress(initialTime, initialTime, $('#progressBar'));
})

finishButton.addEventListener('click', () => {
  socket.emit('playerFinishedMultiplayer', params)
  // unhide results div
  questionContainerElement.classList.add('hide')
  resultsElement.classList.remove('hide')
  finishButton.classList.add('hide')
  backButton.classList.remove('hide')
  scoreFieldElement.classList.add('hide')
  clearStatusClass(document.body)

  console.log(`Finished. Final Score: ${score}!`)
})

socket.on('updateResults', (data) => {
  console.log(`Received data: ${data}`)
  resultsElement.textContent=""
  var r = document.createElement("h2");
  var t = document.createTextNode(`Results!`);
  r.appendChild(t)
  resultsElement.appendChild(r)

  data.sort((a,b) => (a.score > b.score) ? -1 : ((b.score > a.score) ? 1 : 0))

  for (let i = 0; i < data.length; i++) {
    const p = data[i];
    var finishStatus = p.finished? "Finished":"Waiting for player to finish...";
    var para = document.createElement("p");
    var node = document.createTextNode(`${i+1}. Name: ${p.name}, Score: ${p.score}, Status: ${finishStatus}`);
    para.appendChild(node);
    resultsElement.appendChild(para)
  }
})

// this needs to be called on "Start"
function startGame() {
  startButton.classList.add('hide')
  // shuffledQuestions = questions
  currentQuestionIndex = 0
  score = 0
  questionContainerElement.classList.remove('hide')
  setNextQuestion()
}

function setNextQuestion() {
  resetState()
  showQuestion(shuffledQuestions[currentQuestionIndex])
}

function showQuestion(question) {
  questionElement.innerText = question.question
  console.log(question)
  for (let i = 0; i < question.answers.length; i++) {
    // creates new button for each answer option
    const button = document.createElement('button')
    button.classList.add('btn')
    button.innerText = question.answers[i]
    if (question.correct == i) {
      button.dataset.correct = true
    }
    button.addEventListener('click', selectAnswer)
    answerButtonsElement.appendChild(button)
  }
}

function resetState() {
  clearStatusClass(document.body)
  nextButton.classList.add('hide')
  while (answerButtonsElement.firstChild) {
    answerButtonsElement.removeChild(answerButtonsElement.firstChild)
  }
}

function selectAnswer(e) {
  clearInterval(x)
  const selectedButton = e.target
  doStuff(selectedButton)
}

function doStuff(btn) {
  const correct = (btn.dataset.correct == 'true');
  if (correct) {
    incrementScoreBy(10)
  }
  console.log(`Current score: ${score}`)

  setStatusClass(document.body, correct)
  Array.from(answerButtonsElement.children).forEach(button => {
    setStatusClass(button, button.dataset.correct)
  })
  if (shuffledQuestions.length > currentQuestionIndex + 1) {
    nextButton.classList.remove('hide')
  } else {
    finishButton.classList.remove('hide')
  }
  var data = {"id":params.id, "pin":params.pin, "score":score}
  socket.emit('updateMultiplayerScore', data)
}

function incrementScoreBy(points) {
  score+=points
  scoreFieldElement.innerText = score
}

function setStatusClass(element, correct) {
  clearStatusClass(element)
  if (correct) {
    element.classList.add('correct')
  } else {
    element.classList.add('wrong')
  }
}

function clearStatusClass(element) {
  element.classList.remove('correct')
  element.classList.remove('wrong')
}