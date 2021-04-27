function changeProfile() {
    $(".change-profile:first").toggle()
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
        // when game start and not end
        if (this.room_ready == true && this.game_end == false) {
            $('#exit_room_button').prop('disabled', true);

            // chat time
            if (this.phase == 'chat'){
                // console.log('chatting: ' + this.is_dead)
                // console.log('this.player_turn_username: ' + this.player_turn_username)
                $('#chat_block').show();
                $('#vote').hide()

                if (this.current_user_name == myUserName) {
                    if (this.player_turn_username == myUserName && this.is_dead == false) {
                        $('#send_msg_button').prop('disabled', false);
                        $("#game-messages").html(
                            '<h5 id="game-messages">Seconds left: ' + this.time_left + '</h5>');
                        $('#my_profile').show()
                    } else if (this.is_dead == true) {
                        $("#game-messages").html('<h5 id="game-messages">You are dead! ' +
                            this.player_turn_first_name + '&nbsp'
                            + this.player_turn_last_name + ' is typing... </h5>');
                        $('#my_profile').hide();
                    } else {
                        $('#send_msg_button').prop('disabled', true);
                        $("#game-messages").html(
                            '<h5 id="game-messages">' + this.player_turn_first_name +
                            '&nbsp' + this.player_turn_last_name + ' is typing... </h5>');
                        // console.log('chating...this player is dead')
                        $('#my_profile').show();
                    }
                }
            }
            // vote time
            else if (this.phase == 'vote') {

                if (this.current_user_name == myUserName && this.is_dead == false) {
                    $("#game-messages").html(
                        '<h5 id="game-messages">Voting...</h5>');
                    $('#vote').show()
                    $('#my_profile').hide()
                    // console.log('voting...this player is alive')
                } else if (this.current_user_name == myUserName && this.is_dead == true) {
                    $("#game-messages").html(
                        '<h5 id="game-messages">You are dead! The others are voting...</h5>');
                    $('#vote').hide()
                    $('#my_profile').hide()
                    // console.log('voting...this player is dead')
                }
            }
            // display time
            else if (this.phase == 'display') {
                $("#game-messages").html('<h5 id="game-messages">Display Voting Result...</h5>');
                $('#vote').hide()
                $('#my_profile').hide()
                // console.log('displaying...')
            }
        }
        // when game end or game not start
        else {
            $('#exit_room_button').attr('disabled', false);
            $('#vote').hide()
        }
    })
}


function validatePlayer(response) {
    if (Array.isArray(response)) {
        displayGameInfo(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function displayGameInfo(response) {
    $("#display_player").empty();
    $("#your_word").empty();
    $("#display_vote").empty();

    $(response).each(function () {
        if (this.phase == 'vote' && this.is_dead == false && document.getElementById("vote_" + this.id) == null) {
            // console.log("Inner Loop")
            $("#display_vote").append(
                '<p class="max-auto" id="vote_' + this.id + '">' + this.fname + ' ' + this.lname + ': ' +
                '<input type="radio" name="vote" value="' + this.id + '" onClick="getVote(' + this.id + ')"></p>'
            )
        }

        if (document.getElementById(this.id) == null) {
            if (this.room_ready == true) {
                $("#room_readiness").html(
                    '<span class = "text-capitalize"> Ready: &nbsp<span class=" text-success">' + this.room_ready +
                    '</span></span>');
                $('#invite_friends').hide()
            }
            if (this.room_ready == false) {
                $("#room_readiness").html(
                    '<span class = "text-capitalize"> Ready: &nbsp <span class=" text-danger">' + this.room_ready +
                    '</span></span>');
            }
            $("#display_player").append(
                '<h6 class="col-sm-12 d-flex"><a class="link-info text-info" ' +
                'href="/findspy/profile/' + this.id + '" id="' + this.id + '">' +
                this.fname + ' ' + this.lname + '</a></h6>'
            );
        }

        if (this.room_ready == true && this.username == myUserName) {
            $("#your_word").html('<span class = "text-capitalize"> Your Word: ' + this.word + '</span>');
        }

        if (this.room_ready == false && this.username == myUserName) {
            $("#your_word").html('<span class = "text-capitalize"> Your Word: None' + '</span>');
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
    input.val('')

    $.ajax({
        url: "/findspy/send-msg",
        type: "POST",
        data: "content=" + content + "&csrfmiddlewaretoken="
            + getCSRFToken() + '&room_id=' + room_id,
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
            $("#display_msg").prepend(
                '<p id="msg_' + this.id + '">' +' Name: ' + this.fname + ' ' + this.lname + ' Time: '
                + this.timestamp + '<br><span class = "text-primary">' + this.content + '</span> ' + '</p><br>'
            )
        }
    })
}

function getVote(player_id) {
    //console.log("voting...")
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

    $('#message').html("");
    $("#game-messages").html('<h5 id="game-messages">Voting End...</h5>');

    $(response).each(function () {
        if (this.username == myUserName) {
            if (this.game_end == true) {
                $("#game-messages").html('<h5 id="game-messages">Game End</h5>');
                if (this.winner == 'civilian') {
                    if (this.player_identity == 'civilian') {
                        $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>'
                            + '<h5 class=" text-success">' + "You are a " + this.player_identity
                            + ". Congratulation!! You Wins &#128522;"
                            + '</h5><br>'
                            + 'The spy word is ' + this.spy_word
                            + '; The civilian word is ' + this.civilian_word);
                    } else {
                        $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>'
                            + '<h5 class=" text-primary">' + "You are a " + this.player_identity
                            + ". Sorry, you Lose &#128557;" + '</h5><br>'
                            + 'The spy word is ' + this.spy_word
                            + '; The civilian word is ' + this.civilian_word);
                    }
                } else {
                    if (this.player_identity != 'civilian') {
                        $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>'
                            + '<h5 class=" text-success">' + ' You are a '
                            + this.player_identity + '. Congratulation!! You Wins &#128522;'
                            + '</h5><br>'
                            + 'The spy word is ' + this.spy_word
                            + '; The civilian word is ' + this.civilian_word);
                    } else {
                        $('#message').html(this.msg + '<br><br>' + '<b>Game End!</b><br>'
                            + '<h5 class=" text-primary">' + ' You are a '
                            + this.player_identity + '. You Lose &#128557;</h5><br>'
                            + 'The spy word is ' + this.spy_word
                            + '; The civilian word is ' + this.civilian_word);
                    }
                }
            } else {
                if (this.msg != null) {
                    $('#message').html(this.msg + '<br>');
                }
            }
        }
    })
}

function displayResult() {
    $.ajax({
        url: "/findspy/dump_result",
        dataType: "json",
        success: updateResult,
        error: updateError,
    });
}

function updateResult(response) {
    $(response).each(function () {
       if (this.username == myUserName) {
           displayVote(response);
       }
       $('#alive_users').html(
           '<h5 class="text-success d-flex align-items-end flex-column"> Alive users: ' + this.players_alive + '</h5>'
       )
    });
}

