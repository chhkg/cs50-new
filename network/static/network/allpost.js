import {edit_post, like_post} from './module.js'

document.addEventListener('DOMContentLoaded', function() {

    // Edit post after clicking edit button      
    const post_edit_button = document.getElementsByClassName('each_post_edit_button') 
    for (var i = 0; i < post_edit_button.length; i++) {
        const post_edit_button_parent = post_edit_button[i].parentNode;
        post_edit_button[i].addEventListener('click', () => edit_post(post_edit_button_parent));
    }

    // Like or unlike post
    const post_like_button = document.getElementsByClassName('each_post_like_button')
    for (var i = 0; i < post_like_button.length; i++) {
        const post_like_button_parent = post_like_button[i].parentNode;
        const postid = post_like_button_parent.querySelector('#postid').innerHTML
        post_like_button[i].addEventListener('click', () => like_post(post_like_button_parent, postid));
    }
});

