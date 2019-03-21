function addComment(e) {
    console.log(e.data.id);
    var contentField = $("#" + "post_" + e.data.id).find("#new-comment");
    var postDiv = $("#" + "post_" + e.data.id);
    var list = postDiv.find("#comment-list");
    $.post("/add-comment/" + e.data.id, {comment: contentField.val()})
      .done(function(data) {
        $("#new-comment").val("").focus();
        list.html('');
        for (var i = 0; i < data.comments.length; i++) {
            comment = data.comments[i];
            var new_comment = $(comment.html);
            new_comment.data("comment-id", comment.id);
            list.prepend(new_comment);
        }
        getUpdatedPost();
      });
}

function addCommentToPost(post) {
    console.log(post.id)
    var postDiv = $("#" + "post_" + post.id);
    var list = postDiv.find("#comment-list");
    $.get("/get-comments/" + post.id).done(function(data) {
        list.data('max-time', data['max-time']);
        list.html('');
        for (var i = 0; i < data.comments.length; i++) {
            comment = data.comments[i];
            var new_comment = $(comment.html);
            new_comment.data("comment-id", comment.id);
            list.prepend(new_comment);
        }
    });
}

function populateList() {
    $.get("/get-global-stream-posts").done(function(data) {
        var list = $("#post-list");
        list.data('max-time', data['max-time']);
        list.html('')
        for (var i = 0; i < data.posts.length; i++) {
            post = data.posts[i];
            var new_post = $(post.html);
            new_post.data("post-id", post.id);
            new_post.find("#comment-btn").click(post, addComment);
            list.prepend(new_post);
            addCommentToPost(post);
        }
    });
}

function addPost() {
    var contentField = $("#new_post");
    $.post("/add-post", {post: contentField.val()}).done(function(data) {
            getUpdatedPost();
            contentField.val("").focus();
    });
}

function getUpdatedPost() {
    var list = $("#post-list")
    var max_time = list.data("max-time")
    $.get("/get-global-stream-changes/"+max_time)
      .done(function(data){
        list.data('max-time', data['max-time']);
        for (var i = 0; i < data.posts.length; i++) {
            var post = data.posts[i];
            var new_post = $(post.html);
            new_post.data("post-id", post.id);
            list.prepend(new_post);
            addCommentToPost(post);
        }
    });
}

$(document).ready(function () {
    $("#post-btn").click(addPost);
    populateList();

    window.setInterval(getUpdatedPost, 5000);

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
});
