document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  

  // Send email when the new email is submitted
  document.querySelector('#compose-form').onsubmit = () => {
    send_email();
    return false;
  };

  // By default, load the inbox
  load_mailbox('inbox');
  
});

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#emails-content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function reply_email(recipient, subject, timestamp, body) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#emails-content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Pre-fill the reply email
  const strip_body = strip_tags(body);
  
  document.querySelector('#compose-recipients').value = recipient;
  if (subject.slice(0, 4) === "Re: ") {
    document.querySelector('#compose-subject').value = subject;
  } else {
    document.querySelector('#compose-subject').value = 'Re: ' + subject;
  }
  document.querySelector('#compose-body').value = 'On ' + timestamp + ' ' + recipient + ' wrote: ' + '\n' + strip_body;
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#emails-content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  if (mailbox == "sent") {
    document.querySelector('#archive-div').style.display = 'none';
  } else {
    document.querySelector('#archive-div').style.display = 'block';
  }

  // Show the mailbox name
  const view = document.querySelector('#emails-view')
  view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  get_email_list(mailbox);
  
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {

    
    // generate div for each email
    emails.forEach(email => {
        let div = document.createElement('div');

        // add listener and append to DOM
        div.addEventListener('click', () => redirect_to_email_content(email['id']));
        view.appendChild(div);
    });
  });
  return false;
}



function redirect_to_email_content(email_id) {

  fetch('/emails/' + email_id)
  .then(response => response.json())
  .then(email => {
      // Print result
      console.log(email);

      // Show the email content and hide other views
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#emails-content-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';

      //const archive_checkbox_div = document.getElementById("archive-div");
      const view = document.querySelector('#emails-content-view');

      // Showing email content
      document.querySelector("#emails-content-from").innerHTML = (email.sender);
      document.querySelector("#emails-content-to").innerHTML = email.recipients;
      document.querySelector("#emails-content-date").innerHTML = email.timestamp;
      document.querySelector("#emails-content-subject").innerHTML = email.subject;
      document.querySelector("#emails-content-content").innerHTML = email.body;

      // Display the archive checkbox according to archive status
      const archive_checkbox = document.createElement("INPUT");
      archive_checkbox.classList.add('div_margin')
      const archive_label = document.createTextNode(" Archive this email");
      archive_checkbox.setAttribute("type", "checkbox");
      $('#archive-div').empty();
      document.querySelector('#archive-div').appendChild(archive_checkbox);
      document.querySelector('#archive-div').appendChild(archive_label);
      
      if (email.archived) {
        archive_checkbox.checked = true;
      } else {
        archive_checkbox.checked = false;
      }

      // Archive or unarchive email
      archive_checkbox.addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
          archive_email(email_id);
        } else {
          unarchive_email(email_id);
        }
        return false
      })

      // Display the reply button
      const reply_button = document.createElement("BUTTON");
      const reply_button_text = document.createTextNode("Reply");
      reply_button.appendChild(reply_button_text);
      reply_button.setAttribute("id", "reply-button")
      reply_button.classList.add('btn', 'btn-primary', 'btn-block', 'div_margin')
      $('#reply-div').empty();
      document.querySelector('#reply-div').appendChild(reply_button);

      // Redirect to compose view for replying
      reply_button.addEventListener('click', () => {reply_email(email.sender, email.subject, email.timestamp, email.body)});

      // Update the email as read
      fetch('/emails/' + email_id, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      })
      .then (console.log(email_id + " is read"))  
  })
  .catch((error) => console.log(error));
}

function archive_email(email_id) {
    fetch('/emails/' + email_id, {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        })
      })
    .then(response => {
      load_mailbox('inbox');
      console.log(email_id + " is archived");
    })
}

function unarchive_email(email_id) {
  fetch('/emails/' + email_id, {
      method: 'PUT',
      body: JSON.stringify({
        archived: false
      })
    })
  .then(response => {
    load_mailbox('inbox');
    console.log(email_id + " is unarchived");
  })
}

function send_email() {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
    const strip_body = strip_tags(body);

    // Post email content
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: recipients,
          subject: subject,
          body: strip_body,
      })
    })
    .then(response => response.json())
    .then(result => {
      load_mailbox('sent');
      // Print result
      console.log(result);
    })
    .catch((error) => console.log(error));
}

function strip_tags(str) {
  str = str.toString();
  return str.replace(/<\/?[^>]+>/gi, '');
}

function get_email_list(mailbox) {
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);
      console.log("Number of emails: " + emails.length)
  
      // Showing a table of email list in this mailbox
      const element = document.createElement('div');
      $(element).empty();
      
      if (!emails.length) { 
        // Showing no email in this mailbox
        element.innerHTML = 'There is no email in this mailbox';
        document.querySelector('#emails-view').append(element);
      
      } else {    
        var table = document.createElement("TABLE");
        table.setAttribute("id", "email_table");
        table.classList.add("table", "table-bordered", "table-hover");
        document.querySelector('#emails-view').appendChild(table);
        
        // Creating table header
        var table_row_header = document.createElement("TR");
        table_row_header.setAttribute("id", "email_table_row_header");
        document.getElementById("email_table").appendChild(table_row_header);
      
        var table_sender_header = document.createElement("TD");
        if (mailbox == "sent") {
          table_sender_header.innerHTML = ('Receiver');
        } else {
          table_sender_header.innerHTML = ('Sender');
        }
        
        var table_emailsubject_header = document.createElement("TD");
        table_emailsubject_header.innerHTML = ('Email Subject');
        var table_emaildate_header = document.createElement("TD");
        table_emaildate_header.innerHTML = ('Email Date');
        
        table_row_header.appendChild(table_sender_header);
        table_row_header.appendChild(table_emailsubject_header);
        table_row_header.appendChild(table_emaildate_header);
        
        // Creating table body
        for (let i=0; i< emails.length; i++) {
          var table_row_body = email_table.insertRow(-1);
          var table_sender_body = table_row_body.insertCell(0);
          var table_emailsubject_body = table_row_body.insertCell(1);
          var table_emaildate_body = table_row_body.insertCell(2);

          if (mailbox == "sent") {
            table_sender_body.innerHTML = emails[i].recipients;
          } else {
            table_sender_body.innerHTML = emails[i].sender;
          }

          table_emailsubject_body.innerHTML = emails[i].subject;
          table_emaildate_body.innerHTML = emails[i].timestamp;

          // set the email subject link to the email content
          table_emailsubject_body.classList.add("email_subject", "links");
          var email_subject_link = document.getElementsByClassName("email_subject");
          email_subject_link[i].addEventListener("click", redirect_to_email_content.bind(this, emails[i].id), false);
          // email_subject_link[i].addEventListener("click", () => redirect_to_email_content(emails[i].id));
          
          // background color change depends on the read parameter
          table_row_body.classList.add("table_row_body_background");
          var table_row_body_background = document.getElementsByClassName("table_row_body_background");
          if ((mailbox == "inbox" || mailbox == "archive") && emails[i].read) {
            table_row_body_background[i].style.backgroundColor = "#EFEFEF";
          } else {
            table_row_body_background[i].style.backgroundColor = "white";
          }
        }
      }
  });
}