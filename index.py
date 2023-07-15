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
BASE_URL_LI = "https://api.awsli.com.br/v1/"
TOKEN_LI = "chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a"


def listarProdutoBling(codigo, TOKEN):
    data = requests.get(
        f"{BASE_URL}produtos?codigo={codigo}",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    # retorna produto especifico
    dados = data.json()["data"]

    return dados[0] if len(dados) > 0 else 0


def listarProdutoBlingGtin(codigo, TOKEN):
    data = requests.get(
        f"{BASE_URL}produtos?gtin={codigo}",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    # retorna produto especifico
    dados = data.json()["data"]

    return dados[0] if len(dados) > 0 else 0


def listarProdutoLI(codigo):
    data = requests.get(
        f"{BASE_URL_LI}produto?sku={codigo}",
        headers={
            "Authorization": TOKEN_LI
        }
    )

    dados = data.json()["objects"]

    return dados[0] if len(dados) > 0 else 0


def listarProdutoLIGtin(codigo):
    data = requests.get(
        f"{BASE_URL_LI}produto?gtin={codigo}",
        headers={
            "Authorization": TOKEN_LI
        }
    )

    dados = data.json()["objects"]

    return dados[0] if len(dados) > 0 else 0


def listarPrecoLI(codigo):
    return requests.get(
        f"{BASE_URL_LI}produto_preco/{codigo}",
        headers={
            "Authorization": TOKEN_LI
        }
    ).json()


def listarEspecificoBling(codigo, TOKEN):
    data = requests.get(
        f"{BASE_URL}produtos?codigo={codigo}",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    # retorna produto especifico
    return data.json()["data"][0]


def atualizarPrecoBling(dados, TOKEN):
    payload = json.dumps({
        "id": dados["id"],
        "nome": dados["nome"],
        "codigo": dados["codigo"],
        "preco": dados["preco"],
        "tipo": dados["tipo"],
        "situacao": dados["situacao"],
        "formato": dados["formato"],
        "descricaoCurta": dados["descricaoCurta"]
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'Cookie': 'PHPSESSID=l3eehmpec57laprti2qok9oemh'
    }

    return requests.request("PUT", f"{BASE_URL}produtos/{dados['id']}", headers=headers, data=payload).json()


def atualizarStatusLI(dados):
    url = f"https://api.awsli.com.br/v1/produto/{dados['id']}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN_LI
    }

    response = requests.request("PUT", url, headers=headers, data=json.dumps(dados))

    return response.json()


def atualizarPrecoLI(dados, id):
    url = f"https://api.awsli.com.br/v1/produto_preco/{id}"

    payload = json.dumps({
        "cheio": dados["cheio"],
        "custo": dados["custo"],
        "promocional": dados["promocional"]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN_LI
    }

    return requests.request("PUT", url, headers=headers, data=payload).json()


def getIdDeposito(TOKEN):
    data = requests.get(
        f"{BASE_URL}depositos",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    try:
        # retorna o id do primeiro deposito
        return data.json()["data"][0]["id"]
    except:
        return False


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
    response = requests.request("POST", url, headers=headers, data=payload, timeout=20)

    if response.status_code == 201:
        return True
    return False


@app.route("/order", methods=["POST"])
def new_order():
    code = 200
    count = 0

    if not (listaDeProdutosTabela := request.get_json().get("payload")):
        code = 400
        count = 0
    else:
        TOKEN = col_bling.find_one({"_id": 0}).get("token")

        idDeposito = getIdDeposito(TOKEN)

        if not idDeposito:
            return make_response(
                jsonify({"msg": "token error"}), 403
            )
        for produtoTabela in listaDeProdutosTabela:

            produtoBling = listarEspecificoBling(produtoTabela["SKU"], TOKEN)

            if produtoBling:
                result = criarEstoque(
                    idDeposito,
                    produtoBling["id"],
                    produtoTabela["qtdEstoque"],
                    produtoTabela["precoVenda"],
                    produtoTabela["precoCusto"],
                    TOKEN
                )

                if result:
                    count += 1

    return make_response(
        jsonify({
            "atualizacoes": count
        }), code
    )


@app.route("/token")
def get_token():
    return jsonify({"token": col_bling.find_one({"_id": 0}).get("token")})


@app.route("/deposito")
def get_deposito():
    return jsonify({"deposito": getIdDeposito(col_bling.find_one({"_id": 0}).get("token"))})


@app.route("/produto/<sku>")
def get_produto_epecifico(sku):
    produto = listarEspecificoBling(sku, col_bling.find_one({"_id": 0}).get("token"))
    return jsonify(
        {
            "sku": produto["codigo"],
            "id": produto["id"]
        }
    )


@app.route("/produto/bling/li/sku/<sku>/<gtin>")
def getprodutosku(sku, gtin):
    sku = sku.replace(" ", "")
    gtin = gtin.replace(" ", "")
    TOKEN = col_bling.find_one({"_id": 0}).get("token")

    produtoBling = listarProdutoBling(sku, TOKEN)

    if produtoBling == 0:
        produtoBling = listarProdutoBlingGtin(gtin, TOKEN)

    produtoLI = listarProdutoLI(produtoBling["codigo"])

    if produtoLI == 0:
        produtoLI = listarProdutoLIGtin(gtin)

    precos = listarPrecoLI(produtoLI["id"])

    if produtoBling != 0:
        payload = {
            "nome": produtoBling["nome"],
            "precoBling": produtoBling["preco"],
            "status": "ativo" if produtoLI["ativo"] else "bloqueado",
            "gtin": produtoLI["gtin"],
            "custo": precos["custo"],
            "precoLI": precos["cheio"],
            "promocional": precos["promocional"]
        }
        return jsonify(payload)
    return jsonify(produtoBling)


@app.route("/produto/bling/li/gtin/<gtin>")
def getprodutogtin(gtin):
    TOKEN = col_bling.find_one({"_id": 0}).get("token")

    produtoBling = listarProdutoBlingGtin(gtin, TOKEN)
    produtoLI = listarProdutoLIGtin(gtin)
    precos = listarPrecoLI(produtoLI["id"])

    if produtoBling != 0:
        payload = {
            "nome": produtoBling["nome"],
            "precoBling": produtoBling["preco"],
            "status": "ativo" if produtoLI["ativo"] else "bloqueado",
            "sku": produtoBling["codigo"],
            "gtin": gtin,
            "custo": precos["custo"],
            "precoLI": precos["cheio"],
            "promocional": precos["promocional"]
        }
        return jsonify(payload)
    return jsonify(produtoBling)


@app.route("/atualizar/preco/bling/gtin/<gtin>/<preco>")
def atualizar_preco_bling_gtin(gtin, preco):
    TOKEN = col_bling.find_one({"_id": 0}).get("token")

    produtoBling = listarProdutoBlingGtin(gtin, TOKEN)

    produtoBling["preco"] = preco

    return jsonify(atualizarPrecoBling(produtoBling, TOKEN))


@app.route("/atualizar/preco/li/gtin/<gtin>", methods=["POST"])
def atualizar_preco_li_sku(gtin):
    gtin = gtin.replace(" ", "")
    produtoLI = listarProdutoLIGtin(gtin)

    return atualizarPrecoLI(dados=request.get_json()["payload"], id=produtoLI["id"])


@app.route("/atualizar/preco/bling/sku/<sku>/<preco>")
def atualizar_preco_bling_sku(sku, preco):
    sku = sku.replace(" ", "")

    TOKEN = col_bling.find_one({"_id": 0}).get("token")
    produtoBling = listarProdutoBling(sku, TOKEN)

    produtoBling["preco"] = preco

    return jsonify(atualizarPrecoBling(produtoBling, TOKEN))


@app.route("/atualizar/preco/li/sku/<sku>/<gtin>", methods=["POST"])
def atualizar_preco_li_gtin(sku, gtin):
    sku = sku.replace(" ", "")
    gtin = gtin.replace(" ", "")

    produtoLI = listarProdutoLI(sku)
    if produtoLI == 0:
        produtoLI = listarProdutoLIGtin(gtin)

    return atualizarPrecoLI(dados=request.get_json()["payload"], id=produtoLI["id"])


@app.route("/atualizar/status/sku/<sku>/<gtin>/<status>")
def atualizar_status(sku, gtin, status):
    sku = sku.replace(" ", "")
    gtin = gtin.replace(" ", "")

    produtoLI = listarProdutoLI(sku)
    if produtoLI == 0:
        produtoLI = listarProdutoLIGtin(gtin)

    if status == "True":
        produtoLI["ativo"] = True
        produtoLI["bloqueado"] = False
    else:
        produtoLI["ativo"] = False
        produtoLI["bloqueado"] = True

    return atualizarStatusLI(dados=produtoLI)


@app.route("/atualizar/status/gtin/<gtin>/<status>")
def atualizar_status_gtin(gtin, status):
    gtin = gtin.replace(" ", "")
    produtoLI = listarProdutoLIGtin(gtin)

    if status == "True":
        produtoLI["ativo"] = True
        produtoLI["bloqueado"] = False
    else:
        produtoLI["ativo"] = False
        produtoLI["bloqueado"] = True

    return atualizarStatusLI(dados=produtoLI)


@app.route("/criarestoque", methods=["POST"])
def criar_estoque():
    payload = request.get_json()["payload"]
    return jsonify({"sucess": criarEstoque(
        payload["deposito"],
        payload["produtoId"],
        payload["qtdEstoque"],
        payload["preco"],
        payload["custo"],
        payload["token"]
    )})


@app.route("/pedidos/<date>")
def get_pedidos_hoje(date):
    # TOKEN = col_bling.find_one({"_id": 0}).get("token")
    TOKEN = "dcadc2dab5e754ff6178b1b502b81ecae04f417d"

    url = f"https://www.bling.com.br/Api/v3/pedidos/vendas?dataInicial={date}"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'Cookie': 'PHPSESSID=nopshr5oj2r2qh4jfk82e1v3tr'
    }
    response = requests.request("GET", url, headers=headers).json()["data"]
    payload = [{"id": data["id"],
                "cliente": data["contato"]["nome"]} for data in response]

    return payload


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
