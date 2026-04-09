from utils.getProductsFromJSON import getProductsCategory

#Get the minimum price for every product.
def getBestOptions(categoria: str, subcategorias: list, ruta_json: str) -> dict:
    #loads products filtered by categoria and subcategoria.
    productos = getProductsCategory(categoria, subcategorias, ruta_json)

    #Initialize the values for the products filtered by subcategoria
    bestBySubcategory = {
        sub: {
            "minimumPrice": None,
            "minimumProduct": None,
        }
        for sub in subcategorias
    }

    #Get every product
    for product in productos:
        price = float(product["precio"].replace("$", "").replace(",", "").replace('\n/kg', '').strip())
        values = bestBySubcategory[product.get("subcategoria")]

        #initialize prices and products
        if values["minimumPrice"] is None:
            values["minimumPrice"] = price
            values["minimumProduct"] = product

        #compare and assign new values
        if price < values["minimumPrice"]:
            values["minimumPrice"] = price
            values["minimumProduct"] = product

    return {
        "bySubcategory": {
            sub: {
                "minimumProduct": values["minimumProduct"],
            }
            for sub, values in bestBySubcategory.items()
        }
    }