function add_question(data) {
    let quiz = $('[name=quiz]');
    quiz.empty();
    let question = $("<label for='question'></label>").text('Question');
    let input_question = $("<input type='text' maxlength='255' name='question' id='question' required='true'><br>");
    question.append("<br>", input_question);
    let type = $("<label for='type'></label>").text('Choose question type');
    let input_type = $("<select name='type' id='type'><option value='SC'>Single Choice</option><option value='MC'>Multi-choice</option><option value='TY'>Typing</option></select>");
    type.append("<br>", input_type, "<br>");
    quiz.append(question, "<br>", type);
    let answer_nr = 1;
    quiz.append(add_answer(answer_nr, data));
    answer_nr++;
    let add_answer_button = $("<button id='add-answer' class='button' onclick='add_answer("+answer_nr+","+data+")'></button>").text('Add answer');
    let add_question_button = $("<button id='add-question' class='button' onclick='send_question("+data+","+"false,"+answer_nr+")'>Add Question</button>");
    let finish = $("<button id='finish' class='button' onclick='send_question("+data+","+"true,"+answer_nr+")'>Finish</button>");
    let cancel = "<button id='cancel' class='button' onclick='cancel_quiz("+data+")'>Cancel</button>";
    quiz.append("<br>", add_answer_button, "<br>", add_question_button, "<br>", finish, cancel);

}

function add_answer(answer_nr, data) {
    if ($("#type").val() == 'TY') {
        $("#add-answer").before("<p class='invalid error'>If you want to add more answers, change the question type</p>")
    } else {
        let answer = $("<br><label for='answer" + answer_nr + "'></label><br>").text('Answer ' + answer_nr + ' ');
        let input_answer = $("<textarea cols=\"30\" rows=\"4\" name='answer" + answer_nr + "' id='answer" + answer_nr + "' required='true'></textarea><br>");
        let correct = $("<label for='correct" + answer_nr + "' class='sub'></label>").text("Correctness: ");
        let select_correct = "<select name='correct" + answer_nr + "' id='correct" + answer_nr + "'><option value='False'>False</option><option value='True'>True</option></select>";
        let points = $("<label for='points"+answer_nr+"' class='sub'></label>").text("Points: ");
        let input_points = $("<input type='number' name='points"+answer_nr+"' value='0'>")
        if (answer_nr == 1) {
            $("[name='quiz']").append(answer, input_answer, correct, select_correct, "<br>", points, input_points);
        } else {
            let last_answer_nr = answer_nr - 1;
            let last_answer_correctness = "#correct" + last_answer_nr;
            if($(".invalid").length > 0) {
                $(".invalid").remove();
            }
            $("#add-answer").before(answer, input_answer, correct, select_correct, "<br>", points, input_points, "<br>");
            answer_nr++;
            $('#add-answer').attr('onclick', 'add_answer(' + answer_nr + ',' + data + ')');
            $('#add-question').attr('onclick', 'send_question(' + data + ',' + false + ',' + answer_nr + ')');
            $('#finish').attr('onclick', 'send_question(' + data + ',' + true + ',' + answer_nr + ')');
        }
    }
}

function send_question(quiz_id, last, answer_nr) {
    $(".error").remove();
    let answers = [];
    let true_ = 'false';
    if ($("#question").val().length < 1) {
        $("label[for='answer1']").before("<p class='invalid error'>Please fill in the question</p>")
    }
    if($("#type").val() == 'TY' && answer_nr > 2) {
        $("#add-answer").before("<p class='invalid error'>If you want to provide more than 2 answer options, change the question type</p>");
    } else if ($("#type").val() == 'TY' && $("#correct1").val() != 'True') {
        $("#add-answer").before("<p class='invalid error'>The answer provided for this question type must be true.</p>")
    } else if ($("#type").val() == 'TY' && answer_nr == 2 && $("#correct1").val() == 'True') {
        let answer = {
            'answer': $("#answer1").val(),
            'correct': $("#correct1").val()
        };
        if ($("#answer1").val().length < 1) {
            true_ = 'not ok';
        } else {
            true_ = 'ok';
        }
        answers.push(answer);
    } else if(answer_nr <= 3 && $("#type").val() != 'TY'){
        $("#add-answer").before("<p class='invalid error'>You must provide at least 3 answers for this question type</p>");
    } else {
        let _true = 0;
        for (let i = 1; i < answer_nr; i++) {
            let answer = {
                'answer': $("#answer" + i).val(),
                'correct': $("#correct" + i).val()
            };
            if (answer['answer'].length < 1) {
                $("#answer"+i).after("<p class='invalid error'>Please fill in this answer</p>");
                true_ = 'not ok';
            }
            answers.push(answer);
            if (answer['correct'] == 'True') {
                _true = _true+1;
            }
        }
        if ($("#type").val() == 'SC' && _true != 1) {
            $("#add-answer").before("<p class='invalid error'>For this question type you must have only one correct answer.</p>");
        } else if ($("#type").val() == 'MC' && _true < 1){
            $("#add-answer").before("<p class='invalid error'>At least one of the answers must be correct.</p>");
        } else if(true_ == 'false') {
            true_ = 'ok';
        }
    }
    if (answers.length > 0 && true_ == 'ok') {
        $.ajax({
            url: '../../question',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            data: {
                'csrftoken': getCSRFToken(),
                'quiz_id': quiz_id,
                'question': $("#question").val(),
                'type': $("#type").val(),
                'finish': last
            },
            success: function (data) {
                if(Object.hasOwn(data, "msg")) {
                    $("#add-answer").before("<p class='invalid error'>"+data.msg+"</p>")
                } else if (Object.hasOwn(data, "question_id")) {
                    for (let i = 1; i < answer_nr; i++) {
                        $.ajax({
                            url: '../../answer',
                            type: 'POST',

                            headers: {
                                'X-CSRFToken': getCSRFToken()
                            },
                            data: {
                                'question_id': parseInt(data.question_id),
                                'answer': $("#answer" + i).val(),
                                'correct': $("#correct" + i).val(),
                                'points': $("input[name=points" + i+"]").val()
                            },
                            success: function (data) {
                                if (data.hasOwnProperty("msg")) {
                                    $("#add-answer").before("<p class='invalid error'>"+data.msg+"</p>");
                                }
                            }
                        })
                    }
                    if (!last) {
                        add_question(quiz_id);
                    } else {
                        window.location.replace('../../quiz/'+data['quiz_id']);
                    }
                }
            }
        });
    }
}
function cancel_quiz(quiz){
    $.ajax({
        type:'DELETE',
        url: '../../delete_quiz/'+quiz,
        headers: {
            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function (data) {
            window.location.replace('../../../home');
        }
    })
}
