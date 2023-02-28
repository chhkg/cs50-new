export function load_follow_button(request) { 
    
    // Create a button to follow or unfollow the user
    
    const follow_button = document.createElement("button");
    follow_button.setAttribute("class", "each_post_like_button btn btn-primary btn-sm");
    follow_button.setAttribute("id", "follow_button");
    follow_button.innerHTML = 'Follow';

    document.querySelector('#profile-post-count').appendChild(follow_button);

    // Follow or unfollow a user function
    document.querySelector('#follow_button').addEventListener('click', () => follow_user('follow_button'));

    return false;
}

// Function for follow and unfollow a user
export function follow_user(userid) {
    
    fetch("/follow/" + userid, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        const follow_button = document.getElementById("follow-button");
        var follower_count = Number(document.querySelector('#follower_count').innerHTML)

        if (follow_button.innerHTML == 'Follow') {
            follow_button.innerHTML = 'Following';
            follow_button.classList.remove('btn-primary');
            follow_button.classList.add('btn-secondary');
            follower_count++
        } else {
            follow_button.innerHTML = 'Follow';
            follow_button.classList.remove('btn-secondary');
            follow_button.classList.add('btn-primary');
            follower_count--
        }
        document.querySelector('#follower_count').innerHTML = follower_count
    })
}

// Function for like and unlike a post
export function like_post (like_button_parent_div, post_id) {
    const like_post_button = like_button_parent_div.querySelector('.each_post_like_button');

    fetch('/postlike/' + post_id, {
        method: "POST"
    })
    .then(response => response.json())
    .then(post => {
        var post_like_counter = Number(like_button_parent_div.querySelector('.post_like_count').innerHTML)
        if (like_post_button.classList.contains('bi-heart')) {
            like_post_button.classList.remove('bi-heart');
            like_post_button.classList.add('bi-heart-fill', 'icon-red');
            post_like_counter++
        } else {
            like_post_button.classList.remove('bi-heart-fill', 'icon-red');
            like_post_button.classList.add('bi-heart');
            post_like_counter--
        }
        like_button_parent_div.querySelector('.post_like_count').innerHTML = post_like_counter
    })
    .catch((error) => console.log(error));
}
    

// Function for editing a post
export function edit_post(edit_button_parent_div){
    // Get the post id
    const post_id = edit_button_parent_div.querySelector('.postid').innerHTML;
    
    // Replace the post body with a textarea
    edit_button_parent_div.querySelector('.post_body').style.display = 'none';

    const post_edit_textarea_div = document.createElement('div');
    const post_edit_textarea = document.createElement("textarea");
    post_edit_textarea.setAttribute("name", "edit_body");
    post_edit_textarea.innerHTML = edit_button_parent_div.querySelector('.post_body').innerHTML;
    post_edit_textarea.setAttribute("form", "form_edit_post");
    post_edit_textarea.setAttribute("class", "form-control element_margin_bottom");
    post_edit_textarea_div.appendChild(post_edit_textarea);
    edit_button_parent_div.querySelector('.post_body').after(post_edit_textarea_div);
    
    // Replace the edit button with a save change button and a cancel button
    edit_button_parent_div.querySelector('.post_edit_button').style.display = 'none';
    const save_change_button = document.createElement("button")
    save_change_button.innerHTML = "Save changes"
    save_change_button.setAttribute("class", "btn btn-primary btn-sm margin_right element_margin_bottom")

    const cancel_edit_button = document.createElement("button")
    cancel_edit_button.innerHTML = "Cancel"
    cancel_edit_button.setAttribute("class", "btn btn-outline-dark btn-sm element_margin_bottom")

    post_edit_textarea_div.after(save_change_button);
    save_change_button.after(cancel_edit_button);

    // Clicking the cancel button will resume the original post view
    cancel_edit_button.onclick = function() {
        edit_button_parent_div.querySelector('.post_edit_button').style.display = 'block';
        edit_button_parent_div.querySelector('.post_body').style.display = 'block';
        save_change_button.style.display = 'none';
        cancel_edit_button.style.display = 'none';
        post_edit_textarea_div.style.display = 'none';
    }

    // Save the changes
    save_change_button.addEventListener('click', () => {

        fetch('/post/' + post_id)
        .then(response => response.json())
        .then(data => {
            if(data.authorid==data.logged_in_user_id){
                fetch('/post/' + post_id, {
                    method: 'PUT',
                    body: JSON.stringify({
                        body: post_edit_textarea.value
                    })
                })
                .then(response => {
                    edit_button_parent_div.querySelector('.post_body').innerHTML = post_edit_textarea.value;
                    edit_button_parent_div.querySelector('.post_edit_button').style.display = 'block';
                    edit_button_parent_div.querySelector('.post_body').style.display = 'block';
                    save_change_button.style.display = 'none';
                    cancel_edit_button.style.display = 'none';
                    post_edit_textarea_div.style.display = 'none';
                })
                .catch((error) => console.log(error));
            } else {
                // Throw an error if a user tried to update another user's post
                alert('You are not allowed to edit this post!')
            }
        })
        .catch((error) => console.log(error));
    })
}


// Function for getting the post list for all posts and following
export function get_post_list(menu_item) {
    fetch('/posts/' + menu_item)
    .then(response => response.json())
    .then(posts => {
        console.log(posts);
        console.log("No. of post: " + posts.length)
        
        posts.forEach(post => {
            // Create the post div
            const current_user_id = JSON.parse(document.getElementById('user_id').textContent);
            
            const div_each_post = document.createElement("div");
            div_each_post.setAttribute("class", "card element_margin_top element_margin_bottom each_post");

            const div_each_post_cardbody = document.createElement("div");
            div_each_post_cardbody.setAttribute("class", "card-body")

            const post_id = document.createElement('p')
            post_id.innerHTML = post.id
            post_id.setAttribute('class', 'postid')
            post_id.hidden = true

            const post_your_post_badge = document.createElement("div")
            post_your_post_badge.innerHTML = "Your Post"
            post_your_post_badge.setAttribute('class', 'badge badge-success')
            
            const post_author = document.createElement("h5")
            post_author.innerHTML = post.username
            post_author.setAttribute('class', 'pointer_cursor min_content')
            post_author.addEventListener("click", () => window.location.href = "/profile/" + post.userid)

            const post_body = document.createElement("p")
            post_body.innerHTML = post.body
            post_body.setAttribute("class", "post_body")

            const post_timestamp = document.createElement("p")
            post_timestamp.setAttribute("class", "post_reduced_line_margin post_light_content")
            post_timestamp.innerHTML = post.timestamp

            const post_like_count_div = document.createElement('div')
            post_like_count_div.setAttribute('class', 'd-flex justify-content-start')
            const post_like_count_icon = document.createElement('i')
            post_like_count_icon.setAttribute('class', 'fa-xs bi bi-heart-fill icon-red post_like_count_icon')
            const post_like_count = document.createElement("p")
            if (!localStorage.getItem('post_like_counter')) {
                localStorage.setItem('post_like_counter', 0);
            }

            const post_like_number = localStorage.getItem('post_like_counter');
            post_like_count.setAttribute("class", "post_like_count post_light_content")
            post_like_count.setAttribute("id", "post_like_count")
            post_like_count.innerHTML = post_like_number
            post_like_count_div.append(post_like_count_icon)
            post_like_count_div.append(post_like_count)

            const post_like_button = document.createElement("i");
            post_like_button.setAttribute("class", "each_post_like_button bi bi-heart");
            post_like_button.setAttribute("id", "post_like_button");

            const post_edit_button = document.createElement("i");
            post_edit_button.setAttribute("class", "each_post_edit_button bi bi-pencil-square post_edit_button");
            //post_edit_button.setAttribute("id", "post_edit_button");

            div_each_post_cardbody.appendChild(post_id);
            if (post.userid == current_user_id) {
                div_each_post_cardbody.appendChild(post_edit_button);
                div_each_post_cardbody.appendChild(post_your_post_badge);
            }
            div_each_post_cardbody.appendChild(post_author);
            div_each_post_cardbody.appendChild(post_body);
            div_each_post_cardbody.appendChild(post_timestamp);
            div_each_post_cardbody.appendChild(post_like_count_div);
            div_each_post_cardbody.appendChild(post_like_button);
            
            div_each_post.appendChild(div_each_post_cardbody);

            if (menu_item == 'profile') {
                // Display my post div
                document.querySelector('#profile-my-post').appendChild(div_each_post);
            } else {
                // Display all/following post div
                document.querySelector('#div-post').appendChild(div_each_post);
            }

            // Edit post after clicking edit button        
            post_edit_button.addEventListener('click', () => edit_post(div_each_post_cardbody));

            // Like or unlike post
            post_like_button.addEventListener('click', () => like_post(div_each_post_cardbody));

        })     
    })
    .catch((error) => console.log(error));
}