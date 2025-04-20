alias storyworld="docker run --rm -it -v $(pwd):/app -w /app/src storyworld python3 main.py"
alias storyshell="docker run --env-file .env --rm -it -v $(pwd):/app -w /app/src storyworld /bin/bash"
alias storyapp="docker run --env-file .env --rm -p 5001:5000 -it -v $(pwd):/app -w /app/src storyworld python3 app.py DEBUG"