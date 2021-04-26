function changeProfile() {
    $(".change-profile:first").toggle()
}

// doesn't work b/c onload does not apply to div tag, has to be applied to body tag
function userVisitCount() {
    //console.log(Storage, localStorage.visitCount)
    if (typeof (Storage) !== "undefined") {
        if (localStorage.visitCount === "undefined" || localStorage.visitCount === "NaN") {
            localStorage.visitCount = 0;
        }
        if (localStorage.visitCount <= 3) {
            displayRule()
        }
        //console.log('current visit count: ', localStorage.visitCount)
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

function displayPlayer() {
    $.ajax({
        url: "/findspy/get-player",
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
}

function displayGame(response) {
    $(response).each(function () {
        if(this.room_ready == true) {
            if (this.room_chat_time == true){
            //console.log(this.player_turn_username)
            //console.log(this.room_timeEnd)
            //console.log(this.current_time)
            //console.log(myUserName)
                if (this.player_turn_username == myUserName){
                    $('#send_msg_button').prop('disabled', false);
                    $("#game-messages").html(
                    '<h5 id="game-messages">Seconds left: ' + this.time_left +'</h5>');
                }else{
                    $('#send_msg_button').prop('disabled', true);
                    $("#game-messages").html(
                    '<h5 id="game-messages">' + this.player_turn_first_name +
                    '&nbsp'+ this.player_turn_last_name + ' is typing... </h5>');
                }
            } else if (this.phase == 'vote' && this.is_dead == false) {
                //vote time
                $("#game-messages").html(
                    '<h5 id="game-messages">Voting...</h5>');
                $('#vote').show()
                $('#my_profile').hide()
            } else if (this.phase == 'display') {
                $("#game-messages").html(
                    '<h5 id="game-messages">Display Voting Result...</h5>');
                $('#vote').hide()
                $('#my_profile').hide()
            } else if (this.game_end == true ) {
                console.log(1111111);
                $('#exit_room_button').attr('disabled', false);
            }
        }else{
            // do nothing
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
        // console.log(this.fname, this.lname, this.is_dead == false)
        // console.log("Chat time == False", this.chat_time == false)
        // console.log("get elm by id: ", document.getElementById("vote_"+this.id) == null)
        if (this.phase == 'vote' && this.is_dead == false && document.getElementById("vote_" + this.id) == null) {
            console.log("Inner Loop")
            $("#display_vote").append(
                '<p class="max-auto" id="vote_' + this.id + '">' + this.fname + ' ' + this.lname + ': ' +
                '<input type="radio" name="vote" value="' + this.id + '" onClick="getVote(' + this.id + ')"></p>'
            )
        }

        if (document.getElementById(this.id) == null) {
            if (this.room_ready == true){
                $("#room_readiness").html(
                 '<span class = "text-capitalize"> Ready: &nbsp<span class=" text-success">' + this.room_ready +
                 '</span></span>');
                $('#exit_room_button').prop('disabled', true);
                $('#chat_block').show();
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
                $('#chat_block').show();
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

// function startTiming(response) {
//     var sec = 30
//     var timer = setInterval(function() {
//        $('#time span').text(sec--);
//         if (sec < 0) {
//           $('#time').fadeOut('fast');
//           clearInterval(timer);
//        }
//     }, 1000);
// }

function getVote(player_id) {
    console.log("voting...")
    $.ajax({
        url: "/findspy/get-vote",
        type: "POST",
        data: "vote=" + player_id + "&csrfmiddlewaretoken="
        + getCSRFToken(),
        dataType: "json",
        success: displayVote,
        error: updateError,
    });
}

function displayVote(response) {
    //console.log("Voting Result:");
    //console.log("room id: " + response[0].room_id);
    //console.log("msg: " + response[0].msg);
    //console.log("winner: " + response[0].winner);
    // console.log(response[0].game_end);
    $('#message').html("");
    console.log(1111111);

    $(response).each(function () {
        console.log("Game end: ", this.game_end === true)
        if (this.game_end == true && this.username== myUserName) {
            $('#msg').show();
            if (this.winner == 'civilian'){
                //console.log(222222222)
                if (this.player_identity == 'civilian'){
                    $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>' 
                    + '<h5 class=" text-success">' + "Congratulation!! You Wins &#128522;" 
                    + '</h5><br><br>' 
                    + 'The spy word is ' + this.spy 
                    + '; The civilian word is ' + this.civilian_word);
                }else{
                    $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>' 
                    + '<h5 class=" text-primary">' + "You Lose &#128557;" + '</h5><br><br>' 
                    + 'The spy word is ' + this.spy 
                    + '; The civilian word is ' + this.civilian_word);
                }
            }else{
                //console.log(333333)
                if (this.player_identity == 'spy'){
                    $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>' 
                    + '<h5 class=" text-success">' + "Congratulation!! You Wins &#128522;" 
                    + '</h5><br><br>' 
                    + 'The spy word is ' + this.spy 
                    + '; The civilian word is ' + this.civilian_word);
                }else{
                    $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>' 
                    + '<h5 class=" text-primary">' + "You Lose &#128557;" + '</h5><br><br>' 
                    + 'The spy word is ' + this.spy 
                    + '; The civilian word is ' + this.civilian_word);
                }
            }
        }else{
            console.log(44444)
            $('#message').html(
            this.msg + '<br><br>' + 'User alived: ' + this.players_alive + '<br><br>'
            );
        }
        $('#vote').hide();
    })

}