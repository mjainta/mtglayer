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

```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer scrapy crawl -o buylist.json ckbl
```

Connect to the container and run stuff there by yourself:
```bash
docker run -ti -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer bash
$ scrapy crawl -o buylist.json ckbl
```
