from cuckoo_filter import CuckooFilter

blocks = ['79872755123434274321615766485584132702875335247720016234105800003839997609729766912110847701312784587051823814087941829582114905067127808900647517231351962018715647018818077777403359292874722821666030565778251150668325204134723545304504145454118842781751959749969083394281936535033641512501257740948305084061', '78905260868906855591689552088177810654265740474978294349684300207119424178365552437291516100152254128986021234563799684809772065204067021336225290286099331709247645180991726987309127733737713441114240360255570856465046302595978933175415187225578143827319282525722186095873815534644506069052135833965068442460', '69961801585852680361040083112202816925306118577809152951740554638377272829560704464460041973995456286076347346724413270053573081789329650176773868069429733925861602497233418649373176532893945959685678638250666200353206448402639089069796078704641145155108212392590358909793662152472786212648094515825408351506']

def check_cuckoo(blocks,token):
    # Create a filter with a capacity of 100000 items
    cf = CuckooFilter(table_size=100000)

    for i in blocks:
        cf.insert(i)
    
    return cf.__contains__(str(token))

''''
    # Remove an item from the filter
    cf.delete("item2")

    # Check if an item is in the filter
    print(cf.contains("item2")) # False
'''