datapane_pb2.py datapane_pb2_grpc.py: .make.venv datapane.proto
	poetry run python -m grpc_tools.protoc --proto_path . --python_out=. --grpc_python_out=. datapane.proto

requirements.txt: poetry.lock
	# Deprecated
	poetry export --format requirements.txt --output requirements.tmp.txt
	echo '# Generated from poetry.lock by `make requirements.txt`' > requirements.txt
	echo '' >> requirements.txt
	cat requirements.tmp.txt >> requirements.txt
	rm requirements.tmp.txt

poetry.lock: pyproject.toml
	poetry update --lock
	# Touch it even if it wasn't modified for make
	touch poetry.lock

.make.venv: poetry.lock
	poetry install --no-root
	touch .make.venv

.PHONY: format
format: .make.venv
	poetry run isort .
	poetry run black .

.PHONY: clean
clean:
	rm -f .make.*
	rm -rf .venv __pycache__ .pytest_cache .vscode

.PHONY: server
server: .make.venv
	HOST=localhost PORT=50031 poetry run python datapane_server.py

.PHONY: client
client: .make.venv
	HOST=localhost PORT=50031 poetry run python datapane_client.py

.PHONY: client-docker
client-docker:
	# Requires "datapane" docker network:
	# docker network create --driver bridge datapane
	docker build -f Dockerfile.client -t datapane-client .
	docker run \
	-p 50032:50032 \
	--expose 50032 --network datapane --hostname datapane-client \
	--env HOST=0.0.0.0 --env PORT=50032 \
	--name datapane-client \
	-it --rm \
	datapane-client

.PHONY: server-docker
server-docker:
	docker build -f Dockerfile.server -t datapane-server .
	docker run \
	--network datapane \
	--env HOST=datapane-client --env PORT=50032 \
	-it --rm \
	datapane-server
