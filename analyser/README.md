# analyser

## Setup

```bash
docker build -t mtglayer-analyser:latest .
```

## Run a spider

To run the analyser use:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer-analyser python match_prices.py
# In the root dir above
docker run -u $(id -u):$(id -g) -v $(pwd)/analyser:/usr/src/app mtglayer-analyser python match_prices.py
```

Connect to the container and run stuff there by yourself:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer-analyser bash
$ python match_prices.py
```
