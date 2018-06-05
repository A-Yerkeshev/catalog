# The web catalog app
This is an application, that stores data about different kinds of items and displays it in a way of web catalog, that is easy for browsing and interacting.
### Required software
This application runs on Linux Ubuntu OS and the instructions below describe how to run it on this OS. Theoretically it is possible to run the application on different systems, but different bugs and errors might occur.
1. Download [Python](https://www.python.org/downloads/) of version 2.X or 3.X
2. Open the Linux terminal and move into the folder where you downloaded the application files. If you are working on different OS than Linux you will need to download and install the terminal, suitable for operating Linux, for example [Git](https://git-scm.com/downloads)
3. Download all necessary Python modules either by typing command `sudo apt-get install`, either by `sudo pip install`, both followed by name of the module. Here is the list of modules you will need:
	* sqlalchemy
	* flask-login
	* flask
	* flask-uploads
	* passlib
### Running the app
After all necessary modules are present run the `database_setup.py` file by typing command `python database_setup.py`. This will initialize an empty database on your computer.  
Finally type `python catalog.py` to run the application. It is now available on `localhost:5000` address.
### Possible issues
After you execute the last step you must to see a message that app is running on `127.0.0.1:5000` in your terminal. If you see an error message in your terminal it might be the case that you did not download the necessary modules, or something failed during the installation.
If everything fine in your terminal, but your browser throws an error it might be an issue with ports. Check out your firewall configurations. If you are using Vagrant virtual machine add this lines:  
`config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"`  
`config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"`
into your Vagrantfileand reload the Vagrant.
### Resources
Catalog app utilizes Google Sign In for authentification of the users
