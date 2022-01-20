# dex-arbitrage
Fintech Project 1 -- Arbitrage Opportunities On Decentralized Exchanges

### Usage

FYI: It'd be nice to setup the project as a installable python package, so the directory
structure mirrors one, but for now we can work directly in src and i'll add that later. 

goto the src directory
```bash
cd src
```
Create a python file named APIKEYS.py and open it in the editor.
```python
API_KEY = "YOUR CODE HERE"
```
close the python file.
#### Unit tests
You can ensure your setup is working by running any of the _tests.py files from within src.

#### Nomics
```python
from dextrader.nomics.utils import get_candles, format_query_as_dataframe, get_recent_trades
```
Nomics utils has the functions for scraping nomics data via their api, please see the nomics_test.py file for examples.