This project is a capstone project for ICS at K-State.
<img width="1687" height="645" alt="Screenshot 2026-05-15 232944" src="https://github.com/user-attachments/assets/6bebfc09-320c-4065-8d13-17eadabd4a9e" />


Rec_manage is a management and scheduling system designed for building dynamic map based work zones from custom drawn polygons on real world locations, then easily assigning team members to these job zones with drag and drop features. 
The application is web based with a Flask framework for the glue, javascript and python scripting for the back end and connections, sqlite for the database and a combination of basic html and css for the front end.

To set up: download files, install requirments (only requires python, flask and flask-classful as libraries non native to most machines). Configure the .flaskenv (set a secret code)
then run.

To use: First make an organization, 
<img width="1492" height="738" alt="Screenshot 2026-05-15 233141" src="https://github.com/user-attachments/assets/fcecdbef-075d-4e5d-9f3e-5d4b988191d8" />

Then build custom zones for what ever dynamic work environment you want to scheduel out (from parks and rec, camp, life guarding zones or agriculture work zones)
<img width="1887" height="858" alt="Screenshot 2026-05-15 234138" src="https://github.com/user-attachments/assets/2c720243-de7b-44d9-8981-97dabb96cd7d" />
<img width="1903" height="727" alt="Screenshot 2026-05-15 230947" src="https://github.com/user-attachments/assets/d55ce278-1aa9-43dd-b7c8-b791fd01bfd5" />
Then generate an invite key and invite employees or team members. Finally drag and drop members from the hud on a selected day and time slot to assign.
