# mtgcrawler

## Setup

```bash
docker build -t mtgcrawler:latest .
```

You never need this, just for documentation about how to setup a new project:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtgcrawler scrapy startproject mtgcrawler
```
