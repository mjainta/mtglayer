from normalizer import normalizeBuylistCardkingdom, getDataFrame

data = normalizeBuylistCardkingdom('pricelist.json', 'Cardkingdom')
df = getDataFrame(data)

df.to_json('normalized_buylists.json', orient='index')
