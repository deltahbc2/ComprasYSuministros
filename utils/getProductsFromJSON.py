import json
import argparse

#Carga el json y lo devuelve como un diccionario
def loadData(ruta_json: str) -> dict:
    with open(ruta_json, encoding="utf-8") as f:
        return json.load(f)

#Filtra el JSON por categoria y subcategoria, devuelve una lista de bloques con los productos filtrados
def getByCategory(data: dict, categoria: str, subcategorias: list) -> list:
    dataCategory = data.get(categoria, [])

    #Convierte en set por rapidez. set = O(1), list = O(n)
    subcategorias_set = set(subcategorias)
    filtered = []

    for block in dataCategory:
        #Crea un nuevo diccionario solo con las nuevas categorias.
        filteredBlock = {
            subcategoria: lista_productos
            for subcategoria, lista_productos in block.items()
            if subcategoria in subcategorias_set
        }
        if filteredBlock:
            filtered.append(filteredBlock)

    return filtered

def getProducts(categoryData: list) -> list:
    productos = []
    for block in categoryData:
        if isinstance(block, dict):
            for subcategoria, lista_productos in block.items():
                for producto in lista_productos:
                    item = dict(producto)
                    item["subcategoria"] = subcategoria
                    productos.append(item)
    
    return productos


def getProductsCategory(categoria: str, subcategorias: list, ruta_json: str) -> list:
    data = loadData(ruta_json)  #carga el JSON completo
    dataCategory = getByCategory(data, categoria, subcategorias)   #Obtiene los productos por categoria
    return getProducts(dataCategory)


def _main()-> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--categoria", required=True)
    parser.add_argument("--subcategorias", required=True, nargs="+")
    parser.add_argument("--ruta", required=True)
    args = parser.parse_args()

    getProductsCategory(args.categoria, args.subcategorias, args.ruta)

if __name__ == "__main__":
    _main()