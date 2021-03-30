function changeProfile() {
    $(".change-profile:first").toggle()
}

// doesn't work b/c onload does not apply to div tag, has to be applied to body tag
function userVisitCount() {
    console.log('blahblahblah')
    console.log(Storage, localStorage.visitCount)
    if (typeof (Storage) !== "undefined") {
        if (localStorage.visitCount === "undefined" || localStorage.visitCount === "NaN") {
            localStorage.visitCount = 0;
        }
        if (localStorage.visitCount <= 3) {
            displayRule()
        }
        console.log('current visit count: ', localStorage.visitCount)
        localStorage.visitCount++;
    } else {
        displayRule()
    }
}

function displayRule() {
    if (document.getElementById('game-intro') == null) {
        $("#game-rules").html(
            '<h2 id="game-intro">Game Intro</h2><br>' +
            '<h5>You will be randomly assigned with a word</h5><br>' +
            '<p style="color: #90adc6">If the word you got is the same for the majority of the others, then you are a civilian and ' +
            'your job is to find the players whose word is not the same with you and eliminate him/her via the polling.</p>' +
            '<p style="color: #887bb0">If the word you got is different from the majority of the others, then you are a spy and ' +
            'your job is to hide your identity and avoid being eliminated from the others.</p>' +
            '<p style="color: #887bb0">If you got a blank word, then you are a Mr.White and ' +
            'your job is to guess what is the word the civilians got, hide your identity ' +
            'and avoid being eliminated from the others.</p><br>' +
            '<h5>Winning Conditions</h5><br>' +
            '<p style="color: #90adc6">For civilians, the winning condition is to eliminate the spy and the Mr.White.</p>' +
            '<p style="color: #887bb0">For spy and Mr.White, the winning condition is when there are more undercover and Mr. White than civilians.</p>' +
            '<i style="color: #f4b9b8">Notice that all players identities will only be released after the end of the game.</i><br>'
        );
    } else {
        $("#game-rules").html('');
    }
}

