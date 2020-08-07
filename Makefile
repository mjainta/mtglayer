build-lambda:
	docker run -ti -u $(shell id -u):$(shell id -g) -v $(shell pwd):/usr/src/app mtglayer /usr/src/app/build-lambda.sh

run-launcher:
	docker run -u $(shell id -u):$(shell id -g) -v $(shell pwd):/usr/src/app mtglayer python3 launcher.py
