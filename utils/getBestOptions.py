from utils.getProductsFromJSON import getProductsCategory

#Get the minimum and maximum price for every product.
def getBestOptions(categoria: str, subcategorias: list, ruta_json: str) -> dict:
    #loads products filtered by categoria and subcategoria.
    productos = getProductsCategory(categoria, subcategorias, ruta_json)

    #Initialize the values for the products filtered by subcategoria
    bestBySubcategory = {
        sub: {
            "minimumPrice": None,
            "maximumPrice": None,
            "minimumProduct": None,
            "maximumProduct": None,
        }
        for sub in subcategorias
    }

    #Get every product
    for product in productos:
        price = float(product["precio"].replace("$", "").replace(",", "").strip())
        values = bestBySubcategory[product.get("subcategoria")]

        #initialize prices and products
        if values["minimumPrice"] is None:
            values["minimumPrice"] = price
            values["minimumProduct"] = product

        if values["maximumPrice"] is None:
            values["maximumPrice"] = price
            values["maximumProduct"] = product

        #compare and assign new values
        if price < values["minimumPrice"]:
            values["minimumPrice"] = price
            values["minimumProduct"] = product

        if price > values["maximumPrice"]:
            values["maximumPrice"] = price
            values["maximumProduct"] = product

    return {
        "bySubcategory": {
            sub: {
                "minimumProduct": values["minimumProduct"],
                "maximumProduct": values["maximumProduct"],
            }
            for sub, values in bestBySubcategory.items()
        }
    }