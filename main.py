from dataset.produtos import dict_produtos
from flask import Flask, jsonify, request
from datetime import datetime, timedelta, timezone
from prog_jwt.token import verificar_token
from dotenv import load_dotenv
import jwt
import os


load_dotenv()


app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify(message="Dados de login não fornecidos!"), 400
    if "username" not in data or "password" not in data:
        return jsonify(message="Campos 'username' e 'password' são obrigatórios!"), 400
    if data["username"] == "admin" and data["password"] == "123":
        token = jwt.encode(
            {"user": data["username"], "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify(token=token)
    return jsonify(message="Credenciais inválidas!"), 401

@app.route('/produtos', methods=['GET'])
def produtos():
    auth_header = request.headers.get("Authorization")
    match verificar_token(auth_header, SECRET_KEY):
        case 403:
            return jsonify(message="Token é Invalido!"), 403
        case 401:
            return jsonify(message="Cabeçalho de autorização malformado!"), 401
        case _:
            pass

    filtro_asc = request.args.get('preco_asc', '')
    filtro_desc = request.args.get('preco_desc', '')
    filtro_description = request.args.get('description_part', '')


    dict_filtro = []

    if filtro_description:
        dict_filtro = [
            product for product in dict_produtos if filtro_description and filtro_description in product['product_description']
        ]


    if filtro_asc:
        if dict_filtro:
            dict_filtro = sorted(dict_filtro, key=lambda k: k['product_price'])
        else:
            dict_filtro = sorted(dict_produtos, key=lambda k: k['product_price'])
    elif filtro_desc:
        if dict_filtro:
            dict_filtro = sorted(dict_filtro, key=lambda k: k['product_price'], reverse=True)
        else:
            dict_filtro = sorted(dict_produtos, key=lambda k: k['product_price'], reverse=True)


    if dict_filtro:
        return jsonify(dict_filtro)
    return jsonify(dict_produtos)


@app.route('/produtos/<int:product_id>', methods=['GET'])
def produto(product_id):

    auth_header = request.headers.get("Authorization")
    match verificar_token(auth_header, SECRET_KEY):
        case 403:
            return jsonify(message="Token é Invalido!"), 403
        case 401:
            return jsonify(message="Cabeçalho de autorização malformado!"), 401
        case _:
            pass

    for product in dict_produtos:
        if product['id'] == product_id:
            return jsonify(product)

    return jsonify({'message': 'Produto não encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True)