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
        $("#game_rule_button").html('Close');
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
        $("#game_rule_button").html('Game Rules');

    }
}

function exitRoom() {
    alert("Are you sure that you want to exit the room?")
}

function displayPlayer(room_id) {
    $.ajax({
        url: "/findspy/get-player/" + room_id,
        dataType: "json",
        success: validatePlayer,
        error: updateError,
    });
}

function updateGame(response) {
    $.ajax({
        url: "/findspy/update_game",
        dataType: "json",
        success: displayGame,
        error: updateError,
    });
    console.log('getMessage')
}

function displayGame(response) {

    $(response).each(function () {
        if (this.room_ready == true && this.username == myUserName){
            $('#send_msg_button').prop('disabled', false);
                
        }
        else{
            $('#send_msg_button').prop('disabled', true);
        }
    })
}


function validatePlayer(response) {
    if (Array.isArray(response)) {
        displayName(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function displayName(response) {
    $("#display_player").empty();
    $("#your_word").empty();

    $(response).each(function () {
        if (document.getElementById(this.id) == null) {
            if (this.room_ready == true){
                $("#room_readiness").html(
                 '<span class = "text-capitalize"> Ready: &nbsp<span class=" text-success">' + this.room_ready +
                 '</span></span>');
                $('#exit_room_button').prop('disabled', true);

            }
            if (this.room_ready == false){
                $("#room_readiness").html(
                 '<span class = "text-capitalize"> Ready: &nbsp <span class=" text-danger">' + this.room_ready +
                 '</span></span>');
            }
            $("#display_player").append(
                '<h6 class="col-sm-12 d-flex"><a class="link-info text-info" ' +
                'href="/findspy/profile/' + this.id + '" id="' + this.id + '">' +
                this.fname + ' ' + this.lname + '</a></h6>'
            );}
            if (this.room_ready == true && this.username == myUserName){
                $("#your_word").html('<span class = "text-capitalize"> Your Word: ' + this.word +'</span>'); 
                $('#send_msg_button').prop('disabled', true);
             
            }
            if (this.room_ready == false && this.username == myUserName) {
                $("#your_word").html('<span class = "text-capitalize"> Your Word: None' + '</span>');
                $('#send_msg_button').prop('disabled', true);

            }
    })
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}

function sendMessage(room_id) {
    var input = $('#send_msg')
    var content = sanitize(input.val())
    // console.log(content)
    input.val('')

    $.ajax({
        url: "/findspy/send-msg",
        type: "POST",
        data: "content=" + content + "&csrfmiddlewaretoken=" 
        + getCSRFToken() +'&room_id=' + room_id,
        dataType: "json",
        success: getMessage,
        error: updateError,
    });
}

function getMessage() {
    $.ajax({
        url: "/findspy/get-msg",
        dataType: "json",
        success: validateMsg,
        error: updateError,
    });
    console.log('getMessage')
}

function validateMsg(response) {
    if (Array.isArray(response)) {
        updateMsg(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateMsg(response) {
    $(response).each(function () {
        if (document.getElementById("msg_" + this.id) == null) {
            $("#testing").append(
                '<p id="msg_' + this.id + '">' + ' ID: ' + this.id  + ' Content: ' +  this.content
                + ' GameID: ' +  this.gameID  + ' Name: ' +
                this.fname + this.lname  + ' Time: ' +  this.timestamp + '</p><br>'
            )
        }
    })
}

function startTiming(response) {
    var sec = 30
    var timer = setInterval(function() {
       $('#time span').text(sec--);
        if (sec < 0) {
          $('#time').fadeOut('fast');
          clearInterval(timer);
       }
    }, 1000);
}