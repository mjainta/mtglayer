# mtgcrawler

## Setup

```bash
docker build -t mtgcrawler:latest .
```

You never need this, just for documentation about how to setup a new project:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtgcrawler scrapy startproject mtgcrawler
```

## Run a spider

```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtgcrawler scrapy crawl -o buylist.json ckbl
```

Connect to the container and run stuff there buy yourself:
```bash
docker run -ti -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtgcrawler bash
$ scrapy crawl -o buylist.json ckbl
```
