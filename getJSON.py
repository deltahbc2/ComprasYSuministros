import json
import argparse
from pathlib import Path

def loadData(ruta_json: str) -> dict:
    with open(ruta_json, encoding="utf-8") as f:
        return json.load(f)

def getByCategory(data: dict, categoria: str) -> list:
    return data.get(categoria, [])

def getProducts(categoryData: list) -> list:
    productos = []
    for bloque in categoryData:
        if isinstance(bloque, dict):
            for subcategoria, lista_productos in bloque.items():
                for producto in lista_productos:
                    item = dict(producto)
                    item["subcategoria"] = subcategoria
                    productos.append(item)
    return productos


def getProductsCategory(categoria: str, ruta_json: str) -> list:
    data = loadData(ruta_json)  #carga el JSON completo
    dataCategory = getByCategory(data, categoria)   #Obtiene los productos por categoria
    return getProducts(dataCategory)


def _main()-> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--categoria", required=True)
    parser.add_argument("--ruta", required=True)
    args = parser.parse_args()

    getProductsCategory(args.categoria, args.ruta)

if __name__ == "__main__":
    _main()