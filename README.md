# mtglayer

## Setup

```bash
docker build -t mtglayer:latest .
```

You never need this, just for documentation about how to setup a new project:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer scrapy startproject mtglayer
```

## Run a spider

To run on AWS lambda we created launcher.py and crawl.py
To use them, change the spidername in crawl.py and then run
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer python launcher.py
```

or use `make`

```bash
make run-launcher
```

It will create a new file for the json output in the `feed/` directory.

To run a spider directly use:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer scrapy crawl -o buylist.json ckbl
```

Connect to the container and run stuff there buy yourself:
```bash
docker run -ti -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer bash
$ python launcher.py
$ scrapy crawl -o buylist.json ckbl
```

## Build an AWS Lambda .zip

```bash
make build-lambda
```
