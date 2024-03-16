$(document).on("submit", ".edit_user", function (event){
    event.preventDefault();
    let username = $(this).find('input[name=username]').val();
    let email = $(this).find('input[name=email]').val();
    let pwd = $(this).find('input[name=pwd]').val();
    alert($(this).find('input[name=csrfmiddlewaretoken]').val());
    $.ajax({
        url: 'signup/',
        type: 'PUT',
        headers: {'X-CSRFToken': $(this).find('input[name=csrfmiddlewaretoken]').val()},
        contentType: 'application/JSON',
        data: {
            'username': username,
            'email': email,
            'pwd': pwd
        },
        success: function (data) {
            $("div.details div p.username").text(username);
            $("#username").val(username);
            $("div.details div p.email").text(email);
            $("#email").val(email);
            let user_pwd = "";
            for (let i = 0; i<pwd.length; i++) {
                user_pwd += "*";
            }
            $("div.details div p.pwd").text(user_pwd);
            $("#pwd").val(user_pwd);
        }
    })
})

$(document).on("click", ".edit", function () {
    $(this).parent().next().css("display", "block");
})

$(document).on("click", ".cancel", function () {
    $(this).parent().parent().css("display", "none");
})

function save(type) {
    $(".invalid").remove()
    let data = {};
    let new_val = "";
    let id = "edit_"+type;
    if (type == 'username') {
        data = {'username': $("#username").val()};
        new_val = $("#username").val();
    } else if (type == 'email') {
        data = {
            'pwd': $("#pwd").val(),
            'email': $("#email").val()
        };
        new_val = $("#email").val();
    } else if (type == 'pwd') {
        data = {
            'old_pwd': $("#old_pwd").val(),
            'new_pwd': $("#new_pwd").val(),
            'confirm_pwd': $("#confirm_pwd").val()
        };
        new_val = $("#new_pwd").val();
    }
    $.ajax({
            url: 'signup/',
            type: 'PUT',
            headers: {'X-CSRFToken': getCSRFToken()},
            data: data,
            success: function (data) {
                if (data.hasOwnProperty('errors')) {
                    for (let i = 0; i<data.errors.length; i++) {
                        $("#"+id+" div.row-in-between").before("<p class='invalid'>"+data.errors[i]+"</p>");
                    }
                } else {
                    $(".invalid").remove();
                    $(".user input").empty();
                    $("#"+id).css("display", "none");
                    $("p."+type).text(new_val);
                }
            }
        })
}