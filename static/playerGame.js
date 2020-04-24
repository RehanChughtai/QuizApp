var socket = io();
var playerAnswered = false;
var correct = false;
var name;
var score = 0;
 
var params = jQuery.deparam(window.location.search); //Gets the id from url

socket.on('connect', function() {
    //Tell server that it is host connection from game view
    socket.emit('player-join-game', params);
    
    document.getElementById('answer1').style.visibility = "visible";
    document.getElementById('answer2').style.visibility = "visible";
    document.getElementById('answer3').style.visibility = "visible";
    document.getElementById('answer4').style.visibility = "visible";
    document.getElementById('backButton').style.visibility = "hidden";
});

socket.on('noGameFound', function(){
    window.location.href = 'quizjoinlobby';//Redirect user to 'join game' page 
});

function answerSubmitted(num){
    if(playerAnswered == false){
        playerAnswered = true;
        var data = {
            "num":num,
            "id":params.id
        }

        socket.emit('playerAnswer', data);//Sends player answer to server
        console.log(`sent: ${data}`)
        //Hiding buttons from user
        document.getElementById('answer1').style.visibility = "hidden";
        document.getElementById('answer2').style.visibility = "hidden";
        document.getElementById('answer3').style.visibility = "hidden";
        document.getElementById('answer4').style.visibility = "hidden";
        document.getElementById('message').style.display = "block";
        document.getElementById('message').innerHTML = "Answer Submitted! Waiting on other players...";
    
    }
}

//Get results on last question
socket.on('answerResult', function(data){
    console.log(data)
    if(data == true){
        correct = true;
    }
});

socket.on('questionOver', function(data){
    console.log("question overrrr")
    if(correct == true){
        document.body.style.backgroundColor = "#4CAF50";
        document.getElementById('message').style.display = "block";
        document.getElementById('message').innerHTML = "Correct!";
    }else{
        document.body.style.backgroundColor = "#f94a1e";
        document.getElementById('message').style.display = "block";
        document.getElementById('message').innerHTML = "Incorrect!";
    }
    document.getElementById('answer1').style.visibility = "hidden";
    document.getElementById('answer2').style.visibility = "hidden";
    document.getElementById('answer3').style.visibility = "hidden";
    document.getElementById('answer4').style.visibility = "hidden";
    socket.emit('getScore', {id : params.id});
});

socket.on('newScore', function(data){
    document.getElementById('scoreText').innerHTML = "Score: " + data;
});

socket.on('nextQuestionPlayer', function(){
    correct = false;
    playerAnswered = false;
    
    document.getElementById('answer1').style.visibility = "visible";
    document.getElementById('answer2').style.visibility = "visible";
    document.getElementById('answer3').style.visibility = "visible";
    document.getElementById('answer4').style.visibility = "visible";
    document.getElementById('message').style.display = "none";
    document.body.style.backgroundColor = "";
    
});

socket.on('hostDisconnect', function(){
    window.location.href = "quizmenu";
});

socket.on('playerGameData', function(data){
    var j = JSON.parse(data)
   for(var i = 0; i < j.players.length; i++){
       console.log(`comparing ${j.players[i].sid} with ${params.id}`)
       if(j.players[i].sid == params.id){
           document.getElementById('nameText').innerHTML = "Name: " + j.players[i].name;
           document.getElementById('scoreText').innerHTML = "Score: " + j.players[i].gamePlayerData.score;
       }
   }
});

socket.on('GameOver', function(data){
    console.log('GameOver!')
    console.log(data)
    document.body.style.backgroundColor = "";
    document.getElementById('answer1').style.visibility = "hidden";
    document.getElementById('answer2').style.visibility = "hidden";
    document.getElementById('answer3').style.visibility = "hidden";
    document.getElementById('answer4').style.visibility = "hidden";
    document.getElementById('message').style.display = "block";
    document.getElementById('message').innerHTML = "GAME OVER";
    document.getElementById('backButton').style.visibility = "visible";
    // add button here to return to playgame
});

