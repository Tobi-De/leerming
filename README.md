## Leerming


Let's plan the UX of the application, I will describe the user flows I have in mind right now, you make some suggestions and improvement and then add details (step by step description, including which button the user clicks on) to each process / flow. If you think there any missing important scenario, add them.
A quick update, there is no Planning class anymore, but a Profile that handle user preferences and plannning.

Flow 1: New user
- access the landing page
- click on signup, only email and password is required, short_name and full_name are optional
- after signup, verify email and then login
- On the first connection, the user is ask to setup his profile, only two fields, review_days (choose a list of days for the review) and review_time (the time to notify for the session)
- Then the user send to his dashboard, the dashbord list all his cards, for a new user the list is empty

Flow 2: Create new cards
- The user access his dashboard and click on a butter to create a new card
- The form is simple, he can either create a front/back or FillIntheGap card, so based on the one he select the form change,
- He can fill in the fields for the form and then save his card (there is a button that says "save and comeback to add another one")
- on the form to create the form (of maybe it is a selection before he sees the form) the user is offered the option to create cards from a document, he can upload a document and generade cards from it (later in future versions he can even only select a part of the document to generate cards)
- When the cards are created the user can navigate between them (at this point he can see the answers and has to option to edit (them) 

Flow 3: Edit cards

- On his dashboard the user can search between cards, select one and edit it, based on the type (Fill in gap or front / back ) he can update the data and change the rank of the card

Flow4: Review Session

- based on the user planning / scheduled when the time for a session arrive the user receive a notification on his phone (web push, email, whatsapp, etc, he can configure his option in his preferences)
- when he click on the notification the session start and he start going through the cards
- when on a card he try to answer the question himself, he report to the app if he was correct or not after reading the answer, at some point I was thinking the user would need to type the answer but it might feels slow and  annoy the users, so he will report himself if he right or wrong by clicking on buttons
- after the users finish the current review session, meaning he complete all the card for today, he receive a global score and the session is ended
- at the end the user also see a list of all the cards he just mastered in the last session if any and get small felicitation message pour all the cards he mastered