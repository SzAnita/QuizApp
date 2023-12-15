function create_quiz() {
    $.ajax({
        url: 'create_quiz',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken':$("[name=csrfmiddlewaretoken]").val(),
            'title': $("#title").val(),
            'theme': $("#theme").val(),
            'description': $("#description").val()
        },
        success: function (data) {
            add_question(data);
        }
      });
}

function add_question(data) {
    let quiz = $('[name=quiz]');
    quiz.empty();
    let question = $("<label for='question'></label>").text('Question');
    let input_question = $("<input type='text' maxlength='255' name='question' id='question' required='true'>");
    question.append("<br>", input_question, "<br>");
    let type = $("<label for='type'></label>").text('Choose question type');
    let input_type = $("<select name='type' id='type'>");
    let option_typing = $("<option value='TY'></option>").text('Typing');
    let option_radio = $("<option value='SC'></option>").text('Single choice');
    let option_checkbox = $("<option value='MC'></option>").text('Multiple choice');
    input_type.append(option_typing, option_radio, option_checkbox);
    type.append("<br>", input_type, "<br>");
    quiz.append(question, type);
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
    let answer = $("<br><label for='answer"+answer_nr+"'></label>").text('Answer '+answer_nr+' ');
    let input_answer = $("<input type='text' maxlength='255' name='answer"+answer_nr+"' id='answer"+answer_nr+"' required='true'>");
    let correct = $("<label for='correct"+answer_nr+"'></label>");
    let select_correct = "<select name='correct"+answer_nr+"' id='correct"+answer_nr+"'><option value='False'>False</option><option value='True'>True</option></select>";
    if(answer_nr == 1) {
        $("[name='quiz']").append(answer, input_answer, correct, select_correct);
    } else {
        let last_answer_nr = answer_nr-1;
        let last_answer_correctness = "#correct"+last_answer_nr;
        $("#add-answer").before(answer, input_answer, correct, select_correct, "<br>");
        answer_nr++;
        $('#add-answer').attr('onclick','add_answer('+answer_nr+','+data+')');
        $('#add-question').attr('onclick','send_question('+data+','+false+','+answer_nr+')');
        $('#finish').attr('onclick','send_question('+data+','+true+','+answer_nr+')');
    }
}

function send_question(quiz_id, last, answer_nr) {
    let answers = [];
    for (let i = 1; i<answer_nr; i++) {
        let answer = {
            'answer': $("#answer"+i).val(),
            'correct': $("#correct"+i).val()
        };
        answers.push(answer);
    }
    $.ajax({
        url: 'add_question',
        type: 'GET',
        contentType: 'application/JSON',
        data: {
            'quiz_id': quiz_id,
            'question': $("#question").val(),
            'type': $('#type').val(),
            'answers[]': JSON.stringify(answers),
            'finish': last
        },
        success: function (data) {
            if(!last) {
                add_question(quiz_id);
            } else if(last) {
                alert('Quiz created');
                data = JSON.parse(data);
                $(".container").empty();
                let title = $("<h3>Title: "+data['title']+"</h3>")
                let theme= $("<h5>Theme: "+data['theme']+"</h5>")
                let description = $("<p>Description: "+data['description']+"</p>")
                $('.container').append(title, theme, description);
                for (let q in data['questions']) {
                    let question = "<div class='quiz'></div><p>"+q['question']+"</p></div>";
                    let answers = "<ul></ul>"
                    for (let a in q['answers']) {
                        let answer = "<li>"+a['answer']+" - "+a['correct']+"</li>"
                        $(answers).append(answer);
                    }
                    $(question).append(answers);
                    $('.container').append(question);
                }
            }
        }
    })
}

function cancel_quiz(quiz){
    //bootstrap modal
    $.ajax({
        type:'GET',
        url: 'cancel_quiz',
        data: {
            'quiz':quiz
        },
        success: function (data) {
            window.location.replace('../');
        }
    })
}