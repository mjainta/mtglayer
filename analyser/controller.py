from normalizer import normalizeBuylistCardkingdom, getDataFrame

data = normalizeBuylistCardkingdom('ckbl-www.cardkingdom.com.json', 'Cardkingdom')
df = getDataFrame(data)

df.to_json('normalized_buylists.json', orient='index')
