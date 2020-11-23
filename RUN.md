1. `docker-compose up --detach` to spin up compose stack.  (Will build images if necessary.)
1. `docker-compose logs --follow` to see output from both containers.
1. `docker attach datapane-server` to enter server cli.
1. `docker-compose down` to remove containers and docker network.

`Makefile` is very rough around the edges, but `make server` and `make client` should work as well.  (In case `poetry` is available.)
That way one can test the project without docker.