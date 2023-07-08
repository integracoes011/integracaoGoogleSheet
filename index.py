from flask import Flask, jsonify, make_response, request
import xml.etree.ElementTree as ET

app = Flask(__name__)


@app.route("/order", methods=["POST"])
def new_order():
    code = 200
    msg = "ok"

    if not (data_order := request.get_json().get("xml_order")):
        code = 400
        msg = "datas not found"
    else:
        root = ET.Element("pedido")

        for key, value in data_order.items():
            ET.SubElement(root, key).text = value

        # msg = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(
        #     ET.tostring(
        #         ET.ElementTree(root).getroot(),
        #         encoding="utf-8",
        #         method="xml").decode()
        # )

        msg = ET.tostring(
            ET.ElementTree(root).getroot(),
            encoding="utf-8",
            method="xml").decode()

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
    app.run()
