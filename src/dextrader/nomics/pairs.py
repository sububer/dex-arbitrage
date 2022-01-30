nomics = {"chain": {}}

nomics["chain"]["bsc"] = {"exchanges": {}}
nomics["chain"]["avalanche"] = {"exchanges": {}}
nomics["chain"]["polygon"] = {"exchanges": {}}

nomics["chain"]["bsc"]["exchanges"]["pancakeswapv2"] = {"markets": {}}
nomics["chain"]["bsc"]["exchanges"]["apeswap"] = {"markets": {}}

nomics["chain"]["avalanche"]["exchanges"]["sushiswap_avalanche"] = {"markets": {}}
nomics["chain"]["avalanche"]["exchanges"]["traderjoe"] = {"markets": {}}
nomics["chain"]["avalanche"]["exchanges"]["pangolin"] = {"markets": {}}

nomics["chain"]["polygon"]["exchanges"]["uniswapv3_polygon"] = {"markets": {}}
nomics["chain"]["polygon"]["exchanges"]["sushiswap_polygon"] = {"markets": {}}
nomics["chain"]["polygon"]["exchanges"]["balancerv2_polygon"] = {"markets": {}}
nomics["chain"]["polygon"]["exchanges"]["dodo_polygon"] = {"markets": {}}

nomics["chain"]["bsc"]["exchanges"]["pancakeswapv2"]["markets"]["BNBBUSD"] = "0x58f876857a02d6762e0101bb5c46a8c1ed44dc16"
#nomics["chain"]["bsc"]["exchanges"]["pancakeswapv2"]["markets"]["USDCBUSD"] = "0xd99c7f6c65857ac913a8f880a4cb84032ab2fc5b"
#nomics["chain"]["bsc"]["exchanges"]["pancakeswapv2"]["markets"]["USDTBUSD"] = "0x7efaef62fddcca950418312c6c91aef321375a00"
nomics["chain"]["bsc"]["exchanges"]["apeswap"]["markets"]["BNBBUSD"] = "0x51e6d27fa57373d8d4c256231241053a70cb1d93"
#nomics["chain"]["bsc"]["exchanges"]["apeswap"]["markets"]["USDCBUSD"] = "0xc087c78abac4a0e900a327444193dbf9ba69058e"
#nomics["chain"]["bsc"]["exchanges"]["apeswap"]["markets"]["USDTBUSD"] = "0x2e707261d086687470b515b320478eb1c88d49bb"

nomics["chain"]["avalanche"]["exchanges"]["sushiswap_avalanche"]["markets"]["AVAXUSDT"] = "0x09657b445df5bf0141e3ef0f5276a329fc01de01"
nomics["chain"]["avalanche"]["exchanges"]["traderjoe"]["markets"]["AVAXUSDT"] = "0xed8cbd9f0ce3c6986b22002f03c6475ceb7a6256"
nomics["chain"]["avalanche"]["exchanges"]["pangolin"]["markets"]["AVAXUSDT"] = "0xe28984e1ee8d431346d32bec9ec800efb643eef4"

nomics["chain"]["polygon"]["exchanges"]["uniswapv3_polygon"]["markets"]["MATICUSDC"] = "0xa374094527e1673a86de625aa59517c5de346d32"
nomics["chain"]["polygon"]["exchanges"]["sushiswap_polygon"]["markets"]["MATICUSDC"] = "0xcd353f79d9fade311fc3119b841e1f456b54e858"
nomics["chain"]["polygon"]["exchanges"]["dodo_polygon"]["markets"]["MATICUSDC"] = "0x10dd6d8a29d489bede472cc1b22dc695c144c5c7"
nomics["chain"]["polygon"]["exchanges"]["balancerv2_polygon"]["markets"]["MATICUSDC"] = "0x0297e37f1873d2dab4487aa67cd56b58e2f27875000100000000000000000002-0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270-0x2791bca1f2de4661ed88a30c99a7a9449aa84174"



def get_chains() -> list:
    ''' Returns list of available chains.'''
    chains = list()

    for chain in nomics["chain"].keys():
        chains.append(chain)
    
    return chains


def get_exchanges(chain_id: str) -> list:
    '''Returns list of exchanges available for a chain.

    input: chain_id -- eg 'bsc', 'avalanche', etc.
    '''
    exchanges = list()
    
    for exchange_id in nomics["chain"][chain_id]['exchanges'].keys():
        exchanges.append(exchange_id)

    return exchanges


def get_market_pairs(chain_id: str) -> list:
    '''Returns list of unique market pairs available to analyze for a given chain

    input: chain_id -- eg 'bsc', 'avalanche', etc.
    '''
    market_pairs = set()

    for exchange_id in nomics["chain"][chain_id]['exchanges'].keys():
        for pair_id in nomics["chain"][chain_id]['exchanges'][exchange_id]['markets'].keys():
            market_pairs.add(pair_id)

    return market_pairs



def get_market_query_data_for_pair(chain_id: str,pair: str) -> dict:
    '''returns dict of all supported exchange, market_hash data for any given pair

    input:
        chain_id -- eg 'bsc', 'avalanche', etc.
        pair -- pair string, eg 'BNBBUSD', 'USDCBUSD'

    output:
     dict:
       { pair_id : [list of tuples (exchange, markethash), ...]}
       eg:
       {'BNBBUSD' : [('pancakeswapv2', '0x58f876857a02d6762e0101bb5c46a8c1ed44dc16'), ...] }
    '''
    pair_market_info = dict()
    pair_market_info[pair] = list()
    
    for exchange_id in nomics["chain"][chain_id]['exchanges'].keys():
        for pair_id in nomics["chain"][chain_id]['exchanges'][exchange_id]['markets'].keys():
            if pair_id == pair:
                pair_market_info[pair].append((exchange_id, nomics["chain"][chain_id]['exchanges'][exchange_id]['markets'][pair_id] ))

    return pair_market_info