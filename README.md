# My Health Website
### Video Demo: <url>
https://www.youtube.com/watch?v=9iLKe-E0oV0
### Description:

For my final project, I decided to make a health website. I work for the NHS and I thought it would be useful if people could have information about their health conditions and medications in one place. This website was made using flask with python, HTML, CSS Javascript and jinja.

The main page of my website in the index HTML. Here the user will be able to see and overview of their health. They will be able to see a graph of their BMI over time, I will also have information about their age, weight, height, Creatinine clearance and smoking status. They will also be able to see a table of their medications and health conditions.

The information that is used for my index page was collected from forms submitted when the user registered and inputted on other pages. I stored this information in a number of tables in my project data base and used jinja to access the information in the tables.

My app.py file is where I used python to gather information that was submitted by form and store the data into tables in my project database.

I had multiple pages that would post forms  to be stored in my project database. These pages included account.html, login.html, meds.html, pms.html, register.html and test.html.

In my med and pms pages, I would allow the user to submit information about their medications and past medical history respectively. They were also able to remove information if these detail changed.

In accounts and tests pages. The user is able to input results such as height, weight, full blood count etc. In real life, you don’t get all these results at the same time so if the user did not fill in one of the fields, the database will be updated with the new information only and pull through the old information.

In accounts, I also allowed the user to change their password if they wanted.

For the BMI graph, I decided to only represent changes in BMI each day. If the users BMI changed in the same day, the graph would not add a new data point and it is unlikely that a person’s BMI should change a lot within a day. They graph with update with the latest BMI that is calculated for that day.

For my register page, the user had to enter their date of birth and a unique username. The password would then be hashed to remain confidential. Once registered, I prompt the user to fill in their ethnicity, height and weight. They won’t be able to access the rest of the website unless this has been done as some pages require this information to work properly. It is also pretty easy to know or find out a person height, weight or ethnicity in the real world.

For my login page, once the form ins submitted, the app.py checks the hashed version of the password against the password in the table associated with the username. If these match, then the user will be logged in. Their session id will correlate with their unique id number in the users table. This will be how the website knows who’s information to access in the various tables as I have linked everyone’s information to their session id.

If the user did not enter the correct information, then the will be redirected to my apology html which will explained the error they made. No information will be submitted to the database and they will be able to return to the previous page and enter information correctly.
