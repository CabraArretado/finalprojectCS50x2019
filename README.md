FINAL PROJECT FOR CS50x 2019
Felipe Moura

English is my second language, forgive me for my grammar

My project is an event planner where you can make a presence list for your event.
It has the same technology used on the Finance project. The Finance was used as base for that project, but code were made again by scratch, anyway little parts of that were used here.
I used Python (Flask), SQL (SQLite), JavaScript(JQuery, Bootstrap) and HTML&CSS (Bootstrap).

It's a small project without all the functionalities that I would wish, but it shows some of the most important knowledges that I have learned in the CS50x. I intend to still working in this project for learning proposes overtime.



/register
The users can create an account where they have besides to provide usual information for login (username, email and password), to answer the input type radar about if they intend to create an event or check presence in one pre-existent.
In the first case once the form is submitted the user is redirected for the /register_event.
In the second a new form input will appear (using JQuery) where the user has to provide a 6 digits unique code. This code is called EVENT CODE. It’s created by the creator of the event in the moment of event register. The code is unique per event. If the user cannot provide this code they won’t be registered.
The username and email must be original otherwise the user won’t be registered. And the password and its confirmation must be equal or the user won’t be registered.

/register_event
In this page the user can create his own event. The only part of the form that must contain original data is the EVENT CODE. If the user does not provide an original EVENT CODE the event won’t be registered.

/index
The index page changes according to the situation of the user, having 4 versions:
User registered as creator of event but without event registered: In this case a button will appear to the user to complete the event’s register
User registered as creator of event and with event registered: The information of the event will appear and a button that allows the view of the guest list with the other users who have currently checked presence.
User registered as a guest but presence not checked: The user will see the event information and a button to check presence in the event
User registered as a guest and checked presence: The user will see the event information and a button that gives an option to mark off their presence in the event.