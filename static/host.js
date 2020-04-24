var socket = io();
var params = jQuery.deparam(window.location.search);

//When host connects to server
socket.on('connect', function() {
    // reset players to empty
    document.getElementById('players').value = "";
    //Tell server that it is host connection
    data = {
        "pin":params.pin,
        "name":socket.id,
        "mode":params.mode || "multiplayer"
    }
    socket.emit('host-join', data);
});

socket.on('showGamePin', function(data){
   document.getElementById('gamePinText').innerHTML = data.pin;
   socket.emit('message', `Game pin updated to: ${data.pin}`)
});

//Adds player's name to screen and updates player count
socket.on('updatePlayerLobbyNOW', function(data){
    console.log("recieved updatePlayerLobby")
    document.getElementById('players').value = "";
    console.log(data)
    for(var i = 0; i < data.length; i++){
        console.log(data[i])
        document.getElementById('players').value += data[i] + "\n";
    }
});

//Tell server to start game if button is clicked
function startGame(){
    console.log("starting game...")
    console.log(`socket: ${socket}`)
    pin = document.getElementById('gamePinText').innerHTML
    var data = {
        "pin": pin,
        "name":socket.id,
        "mode":params.mode || "multiplayer"
    }
    socket.emit('startGame', data);
}

function endGame(){
    window.location.href = "quizmenu";
}

//When server starts interactive game
socket.on('gameStarted', function(data){
    console.log('Interactive Game Started!');
    window.location.href="hostview" + "?id=" + data.id + "&pin=" + data.pin;
});

//When server starts multiplayer game
socket.on('gameStartedMultiplayer', function(data){
    console.log('Multiplayer Game Started!');
    window.location.href="multiplayergameboard" + "?id=" + data.id + "&pin=" + data.pin;
});

socket.on('noGameFound', function(){
   window.location.href = 'quizmenu';//Redirect user to 'join game' page
});

function back() {
    if (params.mode == "multiplayer") {
        window.location.href = 'multiplayermenu'
    } else {
        window.location.href = 'quizmenu'
    }
}