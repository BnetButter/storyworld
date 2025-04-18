alias storyworld="docker run -it -v $(pwd):/app -w /app/src storyworld python3 main.py"
alias storyshell="docker run -it -v $(pwd):/app -w /app/src storyworld /bin/bash"
alias storyapp="docker run -p 5000:5000 -it -v $(pwd):/app -w /app/src storyworld python3 app.py"