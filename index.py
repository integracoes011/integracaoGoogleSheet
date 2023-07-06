from flask import Flask, jsonify, make_response, request
import xml.etree.ElementTree as ET

app = Flask(__name__)


@app.route("/order", methods=["POST"])
def new_order():
    code = 200
    msg = "ok"

    payload = request.get_json()

    if not (data_order := payload.get("xml_order")):
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


if __name__ == "__main__":
    app.run(debug=True)
