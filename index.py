from flask import Flask, jsonify, make_response, request
import requests
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)
BASE_URL = "https://www.bling.com.br/Api/v3/"
TOKEN = "9a511464249295dca71dcac5da8c799ed144c84c"


def listarProdutos():
    data = requests.get(
        f"{BASE_URL}produtos",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    # retorna a lista de produtos
    return data.json()["data"]


def getIdDeposito():
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
                 precoCusto):

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
    msg = "ok"

    if not (payload := request.get_json().get("payload")):
        code = 400
        msg = "datas not found"
    else:
        # lista de produtos vindo da tabela
        listaDeProdutosTabela = [subNull(i) for i in payload]

        # lista de produtos vindo do bling
        listaDeProdutosBling = listarProdutos()

        idDeposito = getIdDeposito()

        for produtoBling in listaDeProdutosBling:
            for produtoTabela in listaDeProdutosTabela:
                if produtoTabela["SKU"] == produtoBling["codigo"]:
                    criarEstoque(
                        idDeposito,
                        produtoBling["id"],
                        produtoTabela["qtdEstoque"],
                        produtoTabela["precoVenda"],
                        produtoTabela["precoCusto"]
                    )
                    break


    # if not (data_order := request.get_json().get("xml_order")):
    #     code = 400
    #     msg = "datas not found"
    # else:
    #     root = ET.Element("pedido")
    #
    #     for key, value in data_order.items():
    #         ET.SubElement(root, key).text = value

    # msg = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(
    #     ET.tostring(
    #         ET.ElementTree(root).getroot(),
    #         encoding="utf-8",
    #         method="xml").decode()
    # )

    # msg = ET.tostring(
    #     ET.ElementTree(root).getroot(),
    #     encoding="utf-8",
    #     method="xml").decode()

    return make_response(
        jsonify({
            "msg": msg
        }), code
    )


@app.route("/callback")
def callback():
    payload = {}
    try:
        payload.update({"body": request.get_json()})
    except Exception:
        payload.update({"body": "void"})

    try:
        payload.update({"args": request.args})
    except Exception:
        payload.update({"args": "void"})

    return jsonify(payload)


if __name__ == "__main__":
    app.run(debug=True)
