$(document).on("submit", ".add_to_group", function (event) {
    event.preventDefault();
    let groups = [];
    $('input[name=group]:checked').each(function() {
        groups.push(this.value);
    });
    $.ajax({
        url: 'quiz_group',
        method: 'PUT',
        headers: {
            'X-CSRFToken': $(this).find("input[name=csrfmiddlewaretoken]").val(),
            'Content-Type': 'application/JSON'
        },
        contentType: 'application/JSON',
        data: {
            "quiz_id": $(this).find('input[name=quiz_id]').val(),
            "groups": groups,
            "type": "add"
        },
        error: function(xhr) {
            alert(JSON.parse(xhr.responseText).msg);
        }
    })
})

function new_group(quiz_id) {
    let c = prompt("Create a new quiz group");
    if (c != null) {
        $.ajax({
            url: 'quiz_group',
            type: 'POST',
            headers: {'X-CSRFToken': getCSRFToken()},
            data: {
                'name': c
            }, success: function () {
                let label = $("<label for='group'> </label>").text(c);
                let input = $("<input name='group' type='radio' value='"+c+"'>");
                $("#addToGroup"+quiz_id+" form div a").before(input, label, "<br>");
            }
        });
    } else {
        alert('If you want to create a new quiz-group, you need to provide a name');
    }
}

$(document).on("click", ".btn-create", function (event) {
    event.preventDefault();
    let this_ = $(this);
    let group_name = $(this).parent().parent().find("input[name=new_group_name]").val();
    $.ajax({
        url: 'quiz_group',
        method: 'POST',
        headers: {'X-CSRFToken': getCSRFToken()},
        data: {
            //'quiz_id': quiz_id,
            'group': group_name
        },
        success: function (data) {
            alert(data.group_id);
            alert(data.group_name);
            let new_checkbox = $("<input type='checkbox' id='group"+data.group_id+"' name='group' value='"+data.group_name+"'>");
            let label = $("<label for='"+data.group_name+">"+data.group_name+"</label>");
            new_checkbox.after(label, "<br>");
            alert(new_checkbox.html());
            let group_nr = this_.closest("div.new-group").parent().find("div.group-list").find("input[name=group]").length;
            this_.closest("div.new-group").parent().find("div.group-list").find("label").eq(group_nr-1).after("<br>", new_checkbox);
        }
    })
})

$(document).on("submit", ".edit_group", function (event) {
    event.preventDefault();
    let new_name_val = $(this).find("input[name=g_name]").val();
    let old_val = $(this).closest("tr.group_header").find("h3").first();
    $.ajax({
        url: 'quiz_group',
        method: 'PUT',
        headers: {'X-CSRFToken': getCSRFToken()},
        data: {
            'old_name': old_val.text(),
            'new_name': new_name_val,
            'type': 'name'
        }, success: function (data) {
            old_val.text(new_name_val);
        }
    })
})

$(document).on("click", ".delete-quizgroup", function(event) {
    event.preventDefault();
    let this_ = $(this);
    $.ajax({
        url: 'quiz_group',
        method: 'DELETE',
        headers: {'X-CSRFToken': getCSRFToken()},
        data: {'group_id': $(this).attr('id')},
        success: function (data) {
            this_.closest("table").remove();
            this_.closest("table").remove();
        }
    })

})