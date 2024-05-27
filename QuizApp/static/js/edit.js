let answer_nr = 2;

$(document).on("submit", ".edit_title", function (event) {
    event.preventDefault();
    $.ajax({
        url: '../quiz/'+$('[name=quiz_id]').val(),
        type: 'PUT',
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()},
        contentType: 'application/JSON',
        data: {
            'title': $('[name=title]').val(),
            'theme': $('[name=theme]').val(),
            'description': $('[name=description]').val(),
            'quiz_id': $('[name=quiz_id]').val()
        },
        success: function (data) {
            $('#title_val').text($('[name=title]').val());
            $('#theme_val').text($('[name=theme]').val());
            $('#desc_val').text($('[name=description]').val());
        },
        error: function (data) {
            alert(JSON.parse(data.responseText)['msg']);
        }
    })
})

$(document).on("submit", ".edit_answer", function (event) {
    event.preventDefault();
    let type = $(this).closest("table").parent().prev().prev().text();
    let old_answer = $(this).closest('tr').children().eq(0);
    let new_answer = $(this).find('textarea[name=answer]').val();
    let old_correct = $(this).closest('tr').children().eq(1);
    let new_correct = $(this).find('select').val();
    let old_points = $(this).closest('tr').children().eq(2);
    let new_points_val = $(this).find("[name = points]").val();
    let old_question_points = $(this).closest("table").closest("tr").children().eq(2);
    let true_answers = 0;
    if(type != 'TY') {
        for (let i = 1; i<$(this).closest("table").find("tr").length-1; i++) {
            let correct_val = $(this).closest("tbody").children().eq(i).children().eq(1).text();
            if(correct_val == "True") {
                true_answers++;
            }
        }
        if (new_correct == "True" && old_correct.val() == "False") {
            true_answers++;
        } else if (new_correct == "False" && old_correct.val() == "True") {
            true_answers--;
        }
    }
    if(type == 'TY' && new_correct == 'False') {
        alert('The answer provided must be true for this question type.');
    } else if (type == 'SC' && true_answers != 1) {
        alert('You must provide only 1 true answer to this question type');
    } else if(type == 'MC' && true_answers<1) {
        alert('You must provide at least 1 true answer for this question type');
    } else {
        $.ajax({
            url: '../answer',
            type: 'POST',
            headers: {'X-CSRFToken': $(this).find("input[name=csrfmiddlewaretoken]").val()},
            contentType: 'application/JSON',
            data: {
                'answer_id': $(this).find('input[name=answer_id]').val(),
                'answer': new_answer,
                'correct': new_correct,
                'points': new_points_val,
                'type': 'put'
            },
            success: function (data) {
                if (parseInt(old_points.text()) < parseInt(new_points_val) && new_correct == 'True') {
                    old_question_points.text(parseInt(old_question_points.text())+parseInt(new_points_val)-parseInt(old_points.text()));
                } else if (parseInt(old_points.text()) > parseInt(new_points_val) && new_correct == 'True') {
                    old_question_points.text(parseInt(old_question_points.text()) - parseInt(old_points.text()) + parseInt(new_points_val));
                }
                old_answer.text(new_answer);
                old_correct.text(new_correct);
                old_points.text(new_points_val);
            }
        })
    }
})

$(document).on("submit", ".edit_question", function (event) {
    event.preventDefault();
    let old_question = $(this).closest('tr').children().eq(0);
    let new_question = $(this).find('textarea').val();
    let old_type = $(this).closest('tr').children().eq(1);
    let new_type = $(this).find('select').val();
    if (old_type.val() != new_type && new_type == 'TY' && $(this).closest('tr').find('tr').length != 2) {
        alert('You should have only one answer');
    } else if (old_type.val() != new_type && (new_type == 'SC' || new_type == 'MC') && $(this).closest('tr').find('tr').length < 4) {
        alert('You should provide at least 3 answers');
    } else {
        $.ajax({
            url: '../question',
            type: 'POST',
            headers: {'X-CSRFToken': getCSRFToken()},
            contentType: 'application/JSON',
            data: {
                'question_id': $(this).find('input[name=question_id]').val(),
                'question': new_question,
                'type': new_type,
                'method_type': 'put'
            },
            success: function (data) {
                old_question.text(new_question);
                old_type.text(new_type);
            }
        })
    }
})

$(document).on('submit', '.add_answer', function (event) {
    event.preventDefault();
    let answer = $(this).find('textarea[name=answer]').val();
    let correct = $(this).find('select[name=correct]').val();
    let this_ = $(this);
    let points = $(this).find('input[name = points]').val();
    let old_question_points = $(this).closest("table").closest("tr").children().eq(2);
    $.ajax({
        url: '../answer',
        type: 'POST',
        headers: {'X-CSRFToken': getCSRFToken()},
        data: {
            'question_id': parseInt($(this).find('input[name=question_id]').val()),
            'answer': answer,
            'correct': correct,
            'points': points
        },
        success: function (data) {
            if (data.hasOwnProperty("answer_id")) {
                this_.closest('tr').before(append_answer(answer, correct, points, data.answer_id));
                old_question_points.text(old_question_points.val()+points);
            } else if(data.hasOwnProperty("msg")) {
                alert(data.msg);
            }
        }
    })
})

$(document).on('submit', '.add_question', function (event) {
    event.preventDefault();
    $(".error").remove();
    let answers = [];
    let true_ = 'false';
    if($("#type").val() == 'TY' && answer_nr > 2) {
        alert("If you want to provide more than 2 answer options, change the question type");
    } else if ($("#type").val() == 'TY' && $("[name = correct1]").val() != 'True') {
        alert("The answer provided for this question type must be true.")
    } else if ($("#type").val() == 'TY' && answer_nr == 2 && $("[name = correct1]").val() == 'True') {
        let answer = {
            'answer': $("[name = answer1]").val(),
            'correct': $("[name = correct1]").val()
        };
        answers.push(answer);
        true_ = 'ok';
    } else if(answer_nr <= 3 && $("#type").val() != 'TY'){
        alert("You must provide at least 3 answers for this question type");
    } else {
        let _true = 0;
        for (let i = 1; i < answer_nr; i++) {
            let answer = {
                'answer': $(this).find("[name = answer" + i +"]").val(),
                'correct': $(this).find("[name = correct" + i + "]").val()
            };
            answers.push(answer);
            if (answer['correct'] == 'True') {
                _true = _true+1;
            }
        }
        if ($("#type").val() == 'SC' && _true != 1) {
            alert("For this question type you must have only one correct answer.");
        } else if ($("#type").val() == 'MC' && _true < 1){
            alert("At least one of the answers must be correct.");
        } else {
            true_ = 'ok';
        }
    }
    if (answers.length > 0 && true_ == 'ok') {
        $.ajax({
            url: '../question',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            data: {
                'quiz_id': $(this).find("#quiz_id").val(),
                'question': $("#question").val(),
                'type': $("#type").val(),
                'finish': 'false'
            },
            success: function (data) {
                if(Object.hasOwn(data, "msg")) {
                    alert(data.msg)
                } else if (Object.hasOwn(data, "question_id")) {
                    let row = $("<tr></tr>")
                    let question_cell = $("<td></td>").text($("#question").val());
                    let type_cell = $("<td></td>").text($("#type").val());
                    let answers_cell = $("<td id='answers'><tabel><tr><th>Answer</th><th>Correct</th><th>Points</th><th></th><th></th></tr></tabel></td>");
                    let edit_cell = $('<td><button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#editQuestion' + data.question_id + '">Edit</button>\n' +
                        '<div class="modal" id="editQuestion' + data.question_id + '"><div class="modal-dialog"><div class="modal-content">\n' +
                        '<div class="modal-header"><h4 class="modal-title">Edit Question</h4><button type="button" class="btn-close" data-bs-dismiss="modal"></button>\n' +
                        '</div><form class="edit_question"><div class="modal-body">\n' +
                        '<label for="question_id"><input type="number" hidden="hidden" id="question_id" name="question_id" value="' + data.question_id + '"></label>' +
                        '<label for="question">Question: </label><br><textarea id="question' + data.question_id + '" name="question" value="' + $("#question").val() + '"></textarea><br>\n' +
                        '<label for="type">Question type:</label><br>' +
                        '<select name="type" id="points'+data.question_id+'"><option value="TY">Typing</option><option value="SC">Single Choice</option><option value="MC">Multiple Choice</option></option></select><br>' +
                        '</div><div class="modal-footer">\n' +
                        '<button type="submit" class="btn btn-danger" data-bs-dismiss="modal">Save</button></div></form>\n' +
                        '</div></div></div></td>');
                    let delete_cell = $('<td><button type="button" class="btn btn-primary delete-question" id="'+data.question_id+'">Delete</button></td>');
                    row.append(question_cell, type_cell, "<td>0</td>", answers_cell, edit_cell, delete_cell);
                    $("#questions").append(row);
                    for (let i = 1; i < answer_nr; i++) {
                        let answer_val = $(this).find("[name = answer" + i + "]").val();
                        let correct_val = $(this).find("[name = correct" + i + "]").val();
                        let points_val = $(this).find("[name = points" + i + "]").val();
                        $.ajax({
                            url: '../answer',
                            type: 'POST',
                            headers: {
                                'X-CSRFToken': getCSRFToken()
                            },
                            data: {
                                'question_id': parseInt(data.question_id),
                                'answer': answer_val,
                                'correct': correct_val,
                                'points': points_val
                            },
                            success: function (data) {
                                if (data.hasOwnProperty("msg")) {
                                    alert(data.msg);
                                } else {
                                    answers_cell.append(append_answer(answer_val, correct_val, points_val, data.answer_id));
                                }
                            }
                        })
                    }
                }
            }
        });
    }


})

//when adding answers from the Add Question button
$(document).on('click', '#add_answer', function (event) {
    let label_answer = $('<label for="answer'+answer_nr+'">Answer '+answer_nr+':</label><br>');
    let answer_textarea = $('<textarea name="answer'+answer_nr+'"></textarea><br>');
    let label_correct = $('<label for="correct'+answer_nr+'">Correct: </label><br>');
    let select_correct = $('<select name="correct'+answer_nr+'"><option value="False">False</option><option value="True">True</option></select><br>');
    let label_points = $('<label for="points'+answer_nr+'">Points:</label><br>');
    let input_points = $('<input type="number" name="points'+answer_nr+'" id="points'+answer_nr+'">')
    $('#add_answer').before(label_answer, answer_textarea, label_correct, select_correct, label_points, input_points);
    answer_nr++;
})

$(document).on("click", ".delete-answer", function (event) {
    let this_ = $(this);
    $.ajax({
        url:'../answer',
        type: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        data: {
            'answer_id': $(this).attr('id')
        },
        success: function (data) {
            this_.closest("tr").remove();
        }
    })
})

$(document).on("click", ".delete-question", function (event) {
    let this_ = $(this);
    $.ajax({
        url:'../question',
        type: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        data: {
            'question_id': $(this).attr('id')
        },
        success: function (data) {
            this_.closest("tr").remove();
        }
    })
})

function append_answer(answer, correct, points, answer_id) {
    let row = $("<tr></tr>");
    let cell_answer = $("<td></td>").text(answer);
    let cell_correct = $("<td></td>").text(correct);
    let cell_points = $("<td></td>").text(points)
    let cellEdit = $('<td><img src="/static/images/edit4.png" class="icon" data-bs-toggle="modal" data-bs-target="#editAnswer' + answer_id + '">\n' +
        '<div class="modal" id="editAnswer' + answer_id + '"><div class="modal-dialog"><div class="modal-content">\n' +
        '<div class="modal-header"><h4 class="modal-title">Edit Answer</h4><button type="button" class="btn-close" data-bs-dismiss="modal"></button>\n' +
        '</div><form class="edit_answer"><div class="modal-body">\n' +
        '<label for="answer_id"><input type="number" hidden="hidden" id="answer_id" name="answer_id" value="' + answer_id + '"></label>' +
        '<label for="answer">Answer: </label><br><textarea id="answer' + answer_id + '" name="answer" placeholder="Answer" value="' + answer_id + '"></textarea><br>\n' +
        '<label for="points">Points:</label><br><input type="number" name="points" id="points'+answer_id+'"><br>' +
        '</div><div class="modal-footer">\n' +
        '<button type="submit" class="btn btn-danger" data-bs-dismiss="modal">Save</button></div></form>\n' +
        '</div></div></div></td>');
    let cellDelete = $('<td><img src="/static/images/delete.png" class="delete-answer icon" id="'+answer_id+'"></td>')
    row.append(cell_answer, cell_correct, cell_points, cellEdit, cellDelete);
    return row;
}