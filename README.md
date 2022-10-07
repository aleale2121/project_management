### Built With

The following are list of any major frameworks/libraries used to bootstrap our project. 
* [Python](https://python.org/)
* [React.js](https://reactjs.org/)
*  [Cypress](https://cypress.io/)


## Getting Started

This is a guidline of how you setting up ourfinal project called SiTE repository management system locally in your machine.
To get a local copy up and running follow the following steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

### Installation


Below is an steps of how you install and setting up our app.
#### Back End Steps
1. Check first our project source code is stored  anywhere in your local machine window,linux or mac. 
2. Install editor for react js and python recommended is vscode                 check on terminal if python is successfully installed in your local machine     for linux os use this command ```$ python3 -V ``` then install pip      linux command   ```$ apt-get install pip```  check version of pip  ```$ pip -V``` 
3. Download and install postgresql database managment system to your localmacine 
3. Open our the backend source code in vs code and open new terminal            linux command os use  ```    $ pwd ``` 
4. Check the terminal absolute path is on the root project path using the step 3 outputs
5. Create a virtual environment for this specific project and activate the virtual env                                                            ```execute the following  commans for linux os users```                       ```$ python3 pip install python3-dev```                                     ```$ python3 -m venv ourvenv```                                                ```$ source ourvenv/bin/activate ``` 
6. Install all necessary packages for the backend server to run successfully.     for linux users use all of the following commands. For window and mac users convert the command to your own os type (match linux command to window or mac command).
    ```sh
   $ pip install -r requirements.txt
   ```
7. Execute migrations and migrate models
    ``` $ python3 app/manage.py makemigrations ```
     ```python3 app/manage.py migrate ```
 
8. Create a super user using the following commands.                             ```$ python3  app/manage.py createsuperuser ```
9.Run the server .                                                              ```$ python3 app/manage.py  runserver ``` 
10. Then you can check api calls on postman or swagger doc
11. Finished
#### Front End Steps
1. Check first our project source code is stored  anywhere in your local machine window,linux or mac. 
2. Download and Install vscode editor for reactjs recommended.
3.Download and Install NodeJS
4. Open our reactjs source code on your own os vscode editor 
5. Open new terminal and check absolute path is on the root project directory 
 check on linux  ```$ pwd ```
6. type below command                                                        for linux os use ```$ npm install ``` 
7. Run the project
8. ```$ npm run```     
9. project will open in the browser and see the project first page 
10. login as a super user you created in the previous backend step
11. do all tasks of admin
12. Finished 



