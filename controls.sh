#!/bin/sh

function show_help (){
	printf "This is the control script, the following commands are supported\n"
	printf "  start : builds and starts the docker containers\n" 
	printf "  goto_server: executes the server script and provides the user with the ability to interact with the system\n"
	printf "  stop : terminates the containers\n"
	printf "  cleanup : removes the client and server images\n" 
	printf "  help : show this message\n" 
}

TASK="$1"

if [[ "$TASK" == "help" ]]; then
	show_help
elif [[ "$TASK" == "start" ]]; then
	docker-compose up --detach --build
elif [[ "$TASK" == "goto_server" ]]; then
	docker exec -it datapane-challenge-server python main.py
elif [[ "$TASK" == "stop" ]]; then
	docker-compose down
elif [[ "$TASK" == "cleanup" ]]; then
	docker image rm datapane-challenge-server:latest
	docker image rm datapane-challenge-client:latest
else 
	echo "Incorrect input provided"
	show_help
fi
