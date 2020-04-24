var socket = io();
var params = jQuery.deparam(window.location.search);

//When player connects to server
socket.on('connect', function() {
    console.log("Lobby")
    //Tell server that it is player connection
    data = {
        "pin":params.pin,
        "name":params.name
    }
    socket.emit('player-join', data);
});

//Boot player back to join screen if game pin has no match
socket.on('noGameFound', function(){
    window.location.href = 'playgame';
});
//If the host disconnects, then the player is booted to main screen
socket.on('hostDisconnect', function(){
    window.location.href = 'playgame';
});

//When the host clicks start game, the player screen changes
socket.on('gameStartedPlayer', function(){
    console.log("gameStarted")
    window.location.href="playerview" + "?id=" + socket.id;
});

socket.on('gameStartedMultiplayer', function(){
    console.log('Multiplayer Game Started!');
    window.location.href="multiplayergameboard" + "?id=" + socket.id + "&pin=" + data.pin;
});

