# Expense Splitter Backend (graphql api)  
GraphQL api to send data to the frontend of the webapp
## Installation  
These instructions are aimed for users of all OS, but if it lacks something or you are stuck in some step, refer <a href="https://github.com/KIRA009/expense-splitter-backend/issues/1"> this issue </a>  
- <a href="https://help.github.com/en/github/getting-started-with-github/fork-a-repo">Fork</a> the repo, and then <a href="https://www.git-scm.com/docs/git-clone">clone</a> it  
- Go to the directory  
- Check out how to create a virtual environment for python <a href="https://virtualenv.pypa.io/en/stable/installation/"> here</a>, and activate it  
- Install the requirements  
  
   `pip3 install requirements.txt`  
- Have a pgsql database ready, with whatever name you want  
- Set environment variables  
     
   - For linux users  
        
      `cp .bashrc.example .bashrc`  

		And put appropriate values in `.bashrc` file  
		
		`source .bashrc`  
  - For windows users  

	`copy .bashrc.example .bashrc`

	And put appropriate values in `.bashrc` file  

	Run shell inside the virtual environment

	`python3 manage.py shell`
	
	```
	from dotenv import load_dotenv
	load_dotenv('.bashrc')
	```
- Apply migrations  
  
   `python3 manage.py migrate`  
- Run the django server  
  
   `python3 manage.py runserver`  
## Contributing
- Please begin contributing by looking into unsolved <a href="https://github.com/KIRA009/expense-splitter-backend/issues">issues</a> and <a href="https://github.com/KIRA009/expense-splitter-backend/projects">projects</a>. 
- If you find something not listed in the issues or projects, please <a href="https://github.com/KIRA009/expense-splitter-backend/issues/new">create</a> a new issue, and tag the mentor
- For contributing, please <a href="https://help.github.com/en/github/getting-started-with-github/fork-a-repo">fork</a> the repo, make a new branch with a name relevant to the feature/fix, and then make a <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request">pull request</a> after the changes have been applied to your fork
## License  
[MIT](https://choosealicense.com/licenses/mit/)