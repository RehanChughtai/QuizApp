var countDownDate = new Date(Date.now() + 60000).getTime();
var username;
var game_mode;
var score = 0;
var answered = 0;
var wrong = 0;
var correct = 0;
var curr_question_index = 0;
var questions;
var curr_question;
var max_questions;

function initialiseGame(duration, questions, mode, uname) {
    username = uname;
    game_mode = mode;
    console.log(`game mode: ${game_mode}`);
    console.log(`questions raw:  ${questions}`)
    setDuration(duration);
    setQuestions(JSON.parse(questions));
    getNextQuestion(curr_question_index);
    updateScore(score);
    updateAnswered(answered);
    updateWrong(wrong);
    updateCorrect(correct);
    //updateUserScore(username);
}

// todo: send from server
function setQuestions(qs) {
  // temp until reading from database via server
  // questions = [
  //   {question : "This is the first question?", answer : "first"}, 
  //   {question: 'This is the second question?', answer: 'second'},
  //   {question: 'This is the third question?', answer: 'third'},
  //   {question: 'This is the fourth question?', answer: 'fourth'},
  //   {question: 'This is the fifth question?', answer: 'fifth'},
  //   {question: 'This is the sixth question?', answer: 'sixth'},
  //   {question: 'This is the seventh question?', answer: 'seventh'},
  //   {question: 'This is the eighth question?', answer: 'eighth'},
  //   {question: 'This is the ninth question?', answer: 'ninth'}
  // ]
  // after getting from server:

  console.log(`Setting questions to: ${qs}`)
  questions = qs
}

// sets duration to user input
function setDuration(duration) {
  if (game_mode === 'timed') {
    countDownDate = new Date(Date.now() + (duration * 1000)).getTime();
    max_questions = Number.MAX_SAFE_INTEGER;
  } else {
    countDownDate = new Date(Date.now()).getTime();
    max_questions = duration;
  }
}

// Update the timer
var x = setInterval(function() {
  var timeLeft;

  // Find the distance between now and the count down date
  if (game_mode === 'timed') {
    timeLeft = countDownDate - new Date().getTime();
  } else {
    timeLeft = Math.abs(countDownDate - new Date().getTime());
  }

  // Time calculations minutes and seconds
  var minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
    
  // Output the result in an element with id="timer"
  document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";
    
  // If less than 10 seconds, turn timer red
  if (game_mode === 'timed' && timeLeft < 10000) {
    document.getElementById("timer").style.color = 'RED';
  }
  // If the count down is over, update time and finish game
  if (timeLeft < 0) {
    clearInterval(x);
    document.getElementById("timer").innerHTML = "GAME OVER!";
    finishGame();
  }
}, 1000);

function finishGame() {
  console.log(`final score: ${score}`)
  
  // stop time and change to green colour
  document.getElementById("timer").style.color = 'GREEN';
  clearInterval(x);
  // hide submit and return buttons, and unhide finish button
  document.getElementById("submit").style.visibility = "hidden";
  document.getElementById("return").style.visibility = "hidden";
  document.getElementById("finish").removeAttribute("hidden");

}

function updateScore(n) {
  score = n;
  document.getElementById('score').innerHTML = score;
}

function updateAnswered(n) {
  answered = n;
  document.getElementById('answered').innerHTML = answered;
}

function updateCorrect(n) {
  correct = n;
  document.getElementById('correct').innerHTML = correct;
}

function updateWrong(n) {
  wrong = n;
  document.getElementById('wrong').innerHTML = wrong;
}

function updateQuestion(q) {
  curr_question = q;
  document.getElementById('question').innerHTML = q.question;
  document.getElementById('ans').value = "";
}

function submitAnswer(){
  user_answer = document.getElementById('ans').value;
  actual_answer = curr_question.answer;
  // validate lowercase and spaces here
  if (user_answer === actual_answer) {
    updateScore(score+=10);
    updateAnswered(answered+=1);
    updateCorrect(correct+=1);
  } else {
    updateAnswered(answered+=1);
    updateWrong(wrong+=1);
  }
  getNextQuestion(curr_question_index);
}

function getNextQuestion(i) {
  const more_qs_available = curr_question_index + 1 < questions.length;
  console.log("Fetching next question...");
  if (curr_question_index >= max_questions || !more_qs_available) {
    finishGame();
  } else {
    updateQuestion(questions[i]);
    curr_question_index++;
  }
}

function submitScoreAndFinish(){
  /*
   post to server to update player score
   Need to create server endpoint: POST /users/:username
   This will update the user score and last played time in the database, 
  */
  console.log(`Score sent to server: ${score}`)
  console.log(`Current username: ${username}`)
  updateUserScore(username);
  // redirect to game selections screen
  window.location.href = 'playgame';
}

function updateUserScore(uname) {
  // console.log(`Score sent to server: ${score}`)

  var toSend = {
    username : uname,
    mode : game_mode,
    score : score
  }
  console.log(toSend)

  $.ajax({
    type : "POST",
    url : '/user',
    dataType: "json",
    data: JSON.stringify(toSend),
    contentType: 'application/json;charset=UTF-8',
    async: false,
    success: function (data) {
      console.log(data);
      // window.location.href = '/playgame.html';
      }
    });   

}
