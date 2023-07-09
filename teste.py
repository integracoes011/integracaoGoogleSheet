import json
import secrets

import requests

from flask import Flask, request, redirect

BASE_URL = "https://www.bling.com.br/Api/v3/"
CLIENT_ID = "06c32f870671fa3746343e06a8d64ab4ff711847"
TOKEN = "9a511464249295dca71dcac5da8c799ed144c84c"

app_teste = Flask(__name__)


# def listarProdutos():
#     data = requests.get(
#         f"{BASE_URL}produtos",
#         headers={
#             "Authorization": f"Bearer {TOKEN}"
#         }
#     )
#
#     print(data.json()["data"])
#
#
# def get_id_deposito():
#     data = requests.get(
#         f"{BASE_URL}depositos",
#         headers={
#             "Authorization": f"Bearer {TOKEN}"
#         }
#     )
#
#     print(data.json()["data"][0]["id"])
#
#
# def criarEstoque():
#     import requests
#     import json
#
#     url = "https://www.bling.com.br/Api/v3/estoques"
#
#     payload = json.dumps({
#         "deposito": {
#             "id": 14887244296
#         },
#         "operacao": "B",
#         "produto": {
#             "id": 16093935409
#         },
#         "quantidade": 22,
#         "preco": 12,
#         "custo": 200,
#         "observacoes": "teste "
#     })
#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'Authorization': 'Bearer 3532879aaeb49a30cb3ae9f7867974af05255650',
#         'Cookie': 'PHPSESSID=78t62q51t4ue3tp9f367ll6b3m'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     print(response.text)


@app_teste.route("/")
def gerarCode():
    data = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "state": secrets.token_hex(40)
    }

    response = requests.get(f"{BASE_URL}oauth/authorize", params=data)
    return redirect("/token?code={k}")


@app_teste("/token")
def gerarToken():
    code = request.args.get("code")
    payload = json.dumps({
        "grant_type": "authorization_code",
        "code": code
    })
    headers = {
        'Authorization': 'Basic MDZjMzJmODcwNjcxZmEzNzQ2MzQzZTA2YThkNjRhYjRmZjcxMTg0NzpmOWNiYmFjNzJlODhiNmFlYzkwY2U2NjVlZTlmNTI0Y2E4ZTcxNGU2MzlmMjkwNjg2ODg1NjIxZjFhMmQ=',
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=f4aa8gc0a6kr70ag2qfbi8iu1k'
    }
    response = requests.request("POST",  f"{BASE_URL}oauth/token", headers=headers, data=payload)

    return response.json()["access_token"]


# gerarToken()

if __name__ == "__main__":
    app_teste.run(debug=True)

lista = [
    {
        "GTIn": 7896451918604,
        "SKU": "SDC1003",
        "nomeProduto": "Bala de Goma Sortido DOCILE 432g - c/ 24 un",
        "precoCusto": 8.75,
        "precoVenda": 12.25,
        "qtdEstoque": 0
    },
    {
        "GTIn": 7622300988524,
        "SKU": "SCD1002",
        "nomeProduto": "Barra de Chocolate branco com wafer BIS XTRA OREO - 45g c/ 24 un",
        "precoCusto": 47.10714285714286,
        "precoVenda": 65.95,
        "qtdEstoque": 0
    },
    {
        "GTIn": 7891000321201,
        "SKU": "SCD1001",
        "nomeProduto": "BONO DOCE DE LEITE 109g",
        "precoCusto": 4.642857142857143,
        "precoVenda": 6.5,
        "qtdEstoque": 0
    }
]
