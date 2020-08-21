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

## Compare ck to mcm prices

First run a spider for ck and put it into `analyser/ckbl-www.cardkingdom.com.json`.

Connect to the container and run stuff there:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/usr/src/app mtglayer-analyser bash
$ python controller.py
$ python process_normalized_buylist.py
```

This will create a file called `analyser/buylists_results.json` with the results.
