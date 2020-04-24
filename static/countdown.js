// function progress(timeleft, timetotal, $element) {
//     var progressBarWidth = timeleft * $element.width() / timetotal;
//     // var buttonPressed =  document.getElementById('next-btn').innerHTML;    ;
//     $element.find('div').animate({ width: progressBarWidth }, 500).html(Math.floor(timeleft/60) + ":"+ timeleft%60);
//     if(timeleft > 0) {
//         setTimeout(function() {
//             progress(timeleft - 1, timetotal, $element);
//         }, 1000);
//     }
//     // else if(buttonPressed = true){
//     //     timeleft.stop();
//     // }
// };

// progress(600, 600, $('#progressBar'));

function progress(timeleft, timetotal, $element) {
    var progressBarWidth = timeleft * $element.width() / timetotal;
    $element.find('div').animate({ width: progressBarWidth }, 500).html(Math.floor(timeleft/60) + ":"+ timeleft%60);
    if(timeleft > 0) {
        setTimeout(function() {
            progress(timeleft - 1, timetotal, $element);
        }, 1000);
    }
};

progress(30, 30, $('#progressBar'));