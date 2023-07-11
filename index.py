from flask import Flask, jsonify, make_response, request
import requests
import json
from pymongo import MongoClient
from decouple import config

client = MongoClient(
    config("URL_CONNECT")
)

db = client["tokens"]
col_bling = db["bling"]

app = Flask(__name__)
BASE_URL = "https://www.bling.com.br/Api/v3/"


def listarProdutosBling():
    TOKEN = col_bling.find_one({"_id": 0}).get("token")
    data = requests.get(
        f"{BASE_URL}produtos",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    # retorna a lista de produtos
    return data.json()["data"]


def getIdDeposito():
    TOKEN = col_bling.find_one({"_id": 0}).get("token")
    data = requests.get(
        f"{BASE_URL}depositos",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )

    # retorna o id do primeiro deposito
    return data.json()["data"][0]["id"]


def criarEstoque(idDeposito,
                 idProduto,
                 quantidade,
                 precoVenda,
                 precoCusto,
                 TOKEN):
    payload = json.dumps({
        "deposito": {
            "id": idDeposito
        },
        "operacao": "B",
        "produto": {
            "id": idProduto
        },
        "quantidade": quantidade,
        "preco": precoVenda,
        "custo": precoCusto,
        "observacoes": "Sem"
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'Cookie': 'PHPSESSID=78t62q51t4ue3tp9f367ll6b3m'
    }
    url = f"{BASE_URL}estoques"
    requests.request("POST", url, headers=headers, data=payload)


def subNull(dado):
    if not dado["qtdEstoque"]:
        dado.update({"qtdEstoque": 0})
    return dado


@app.route("/order", methods=["POST"])
def new_order():
    code = 200
    count = 0

    if not (payload := request.get_json().get("payload")):
        code = 400
        count = 0
    else:
        # lista de produtos vindo da tabela
        listaDeProdutosTabela = [i for i in payload]

        # lista de produtos vindo do bling
        listaDeProdutosBling = listarProdutosBling()

        idDeposito = getIdDeposito()

        TOKEN = col_bling.find_one({"_id": 0}).get("token")

        for produtoBling in listaDeProdutosBling:
            for produtoTabela in listaDeProdutosTabela:
                if str(produtoTabela["SKU"]).lower() == str(produtoBling["codigo"]).lower():
                    count += 1
                    criarEstoque(
                        idDeposito,
                        produtoBling["id"],
                        produtoTabela["qtdEstoque"],
                        produtoTabela["precoVenda"],
                        produtoTabela["precoCusto"],
                        TOKEN
                    )
                    break

    return make_response(
        jsonify({
            "atualizacoes": count
        }), code
    )


@app.route("/produtos")
def getprodutos():
    listaPrudutosBling = listarProdutosBling()

    return jsonify({"payload": listaPrudutosBling})


@app.route("/callback")
def callback():
    payload = request.args
    code = payload.get("code")

    payload = json.dumps({
        "grant_type": "authorization_code",
        "code": code
    })
    headers = {
        'Authorization': 'Basic ' + config('BASIC_AUTHENTICATION'),
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=f4aa8gc0a6kr70ag2qfbi8iu1k'
    }
    response = requests.request("POST", f"{BASE_URL}oauth/token", headers=headers, data=payload)

    if not col_bling.find_one({"_id": 0}):
        col_bling.insert_one(
            {
                "_id": 0,
                "token": response.json()["access_token"]
            }
        )
    else:
        col_bling.update_one(
            {"_id": 0},
            {"$set": {"token": response.json()["access_token"]}}
        )
    return jsonify(
        {
            "msg": "token gerado com sucesso!",
            "token": response.json()["access_token"]
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
