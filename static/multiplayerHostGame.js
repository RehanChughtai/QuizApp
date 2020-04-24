var socket = io();
var params = jQuery.deparam(window.location.search);

// Quiz Generation
const questions = generateQuestions()

function generateQuestions(){
  let qs = []
  // update number of questions in multiplayer mode here 
  for (let i = 0; i < 20; i++) {
    qs.push(getDynamicQuestion())    
  }
  return qs
}  

function getQuestion(a,b){
  switch(Math.floor(Math.random() * 4)) {
    case 0:
      return multiply(a,b)
    case 1:
      return subtract(a,b)
    case 2:
      return divide(a,b)
    default:
      return add(a,b)
  }
}

function add(a, b) {
  q = `What is ${a} + ${b}?`
  ans = a + b
  return [q, ans]
}

function subtract(a, b) {
  if (b > a) {
    const temp = b
    b = a
    a = temp
  }
  
  q = `What is ${a} - ${b}?`
  ans = a - b
  return [q, ans]
}

function multiply(aa, bb) {
  const a = Math.floor(Math.random() * 11)
  const b = Math.floor(Math.random() * 11)
  q = `What is ${a} * ${b}?`
  ans = a * b
  return [q, ans]
}

function divide(aa, bb) {
  const a = Math.floor(Math.random() * (150 - 50) + 50);
  const b = Math.floor(Math.random() * (30 - 1) + 1);
  
  q = `What is ${a} / ${b}? (to the nearest whole number)`
  ans = (a / b) - ((a / b) % 1)

  return [q, ans]
}

function getDynamicQuestion() {
  const a = Math.floor(Math.random() * 101)
  const b = Math.floor(Math.random() * 101)

  const genQues = getQuestion(a,b)
  const q = genQues[0]
  const ans = genQues[1]

  // options is an array of unique strings of numbers - excuding ans
  const options = anythingBut(ans)
  const answer = [ans, options[0], options[1], options[2]].sort(() => Math.random() - .5)  

  const generatedQuestion = {
    question: q,
    answers: answer,
    correct: answer.findIndex(x => x==ans)
  }

  console.log(`Generated Question: ${generatedQuestion}`)
  return generatedQuestion
}

function anythingBut(answer){
  let opts = []
  // generate 3 numbers
  for (let i = 0; i < 3; i++) {
    // make sure they are not same as answer
    let a = anyBut(answer)
    // make sure they are not same as each other
    let contains = opts.includes(a)
    while (contains) {
      a = anyBut(answer)
      contains = opts.includes(a)
    }
    // add to opts
    opts.push(a)
  }
  return opts
}

function anyBut(answer){
 let a = Math.floor(Math.random() * 101)
 let same = (a == answer)
 while(same){
  a = Math.floor(Math.random() * 101)
  same = (a == answer)
 }
 return a
}

function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
}

function multiplayerQuizInit(){
    quizPin = getRndInteger(1000, 9999);
    console.log("multplayer quiz init, getting questions: " + questions)
    var quiz = {pin: quizPin, "name": "Randomly generated multiplayer quiz", "questions": questions};
    socket.emit('newQuiz', quiz);
}

socket.on('startGameFromCreator', function(data){
    window.location.href = "/createlobby?pin=" + data + "&mode=multiplayer";
});