#pip install flask-pydantic-spec
#pip install tinydb

"""
códigos de retorno:
200 = sucesso
201 = criado (post)
204 = sem conteúdo (deletado com sucesso, por exemplo)
400 = não encontrado
500 = erro de servidor
"""


from itertools import count
from typing import Optional, List
from flask import Flask, request, Response, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query #um banco bem simples, só para testes
from tinydb.storages import MemoryStorage

server = Flask(__name__)
spec = FlaskPydanticSpec('flask',Title="Live de python")
spec.register(server)
database = TinyDB('database.json')
c = count()


class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]

class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=next(c))
    nome: str
    idade: int

class Pessoas(BaseModel):
    pessoas: List[Pessoa]
    count: int


@server.route('/pessoas', methods=['GET'])
@spec.validate(resp = Response(HTTP_200 = Pessoas ))
def buscar_pessoas():
    """Retorna todas as Pessoas da base de dados."""
    
    #return jsonify(database().all())
    query = request.context.query
    
    todas_as_pessoas = database.search(
        Query().fragment(query)
    )

    return jsonify(
        Pessoas(
            pessoas = todas_as_pessoas,
            count=len(todas_as_pessoas)
        ).dict()
    )

@server.route('/pessoa/<int:id>', methods=['GET'])
@spec.validate(resp = Response(HTTP_200 = Pessoa))
def buscar_pessoa(id):
    """Retorna dados da pessoa"""
    
    pessoa = database.search(Query().id == id)[0]
    return jsonify(pessoa)

@server.route('/pessoas', methods=['POST'])
@spec.validate(body=Pessoa, resp=Response(HTTP_201 = Pessoa))
def inserir_pessoa():
    """Insere uma pessoa no banco de dados"""
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.route('/pessoas/<int:id>',methods=['PUT'])
@spec.validate(body=Pessoa, resp=Response(HTTP_200=Pessoa))
def altera_pessoa(id):
    """Altera uma pessoa do banco"""
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)

@server.route('/pessoas/<int:id>',methods=['DELETE'])
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """Remove uma pessoa do banco"""

    Pessoa = Query()
    database.remove(Pessoa.id == id)
    return jsonify({})

server.run()