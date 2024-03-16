$(document).on("submit", ".add_to_group", function (event) {
    event.preventDefault();
    $.ajax({
        url: 'quiz',
        method: 'PUT',
        headers: {'X-CSRFToken': $(this).find("input[name=csrfmiddlewaretoken]").val()},
        data: {
            'quiz_id': $(this).find('input[name=quiz_id]').val(),
            'quiz_group': 'true',
            'group': $('input[name=group]:checked').val()
        }
    })
})

function new_group(quiz_id) {
    let c = prompt("Create a new quiz group");
    if (c != null) {
        let label = $("<label for='group'></label>");
        let input = $("<input name='group' type='radio' value='"+c+"'>").html(c + "<br>");
        label.append(input);
        $("#addToGroup"+quiz_id+" form div a").before(label);
        $.ajax({
            url: 'user/quiz_group',
            type: 'POST',
            headers: {'X-CSRFToken': getCSRFToken()},
            data: {
                'name': c
            }, success: function () {
                let label = $("<label for='group'></label>");
                let input = $("<input name='group' type='radio' value='"+c+"'>").html(c + "<br>");
                label.append(input);
            }
        });
    } else {
        alert('If you want to create a new quiz-group, you need to provide a name');
    }
}
