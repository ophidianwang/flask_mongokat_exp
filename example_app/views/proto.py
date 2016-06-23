# -*- coding: utf-8 -*-
from bson import ObjectId
from flask import Blueprint
from example_app import m_interface
from example_app.models.proto import proto


mod = Blueprint('proto', __name__)
m_interface.register([proto])


@mod.route('/')
@mod.route('/proto')
def proto():
    return_msg = "/script/proto:</br>"
    query_instance = m_interface.proto.find_one({'name': 'proto_name'})
    if query_instance is not None:
        return_msg += str(dict(query_instance))
    return return_msg


@mod.route('/create')
def create():
    return_msg = ""
    proto_instance = m_interface.proto()  # create a document_class we just assign to protoCol
    proto_instance['name'] = 'Ophidian Wang'
    proto_instance['email'] = 'aa000017@gmail.com'
    proto_instance.save(uuid=True)  # use uuid=True will assign _id a uuid_v4 instead of native ObjectId
    return_msg += "save success</br>"

    query_instance = m_interface.proto.find_one({'name': 'Ophidian Wang'})
    return_msg += str(dict(query_instance))

    return return_msg


@mod.route('/query/<ObjectId:query_id>')
def query(query_id):
    """
    """
    queried_proto = m_interface.proto.find_by_id(query_id)
    return str(dict(queried_proto))