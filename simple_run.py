# -*- coding: utf-8 -*-
from flask import Flask
from flask_mongokat import MongoKat
from proto import proto

app = Flask(__name__)
m_interface = MongoKat(app)
m_interface.register([proto])  # interface.register(proto) also works
# I think I would register using model in each view module

@app.route('/')
def show_entries():
    return_msg = "show entries</br>"

    proto_instance = m_interface.proto()  # create a document_class we just assign to protoCol
    proto_instance['name'] = 'Ophidian Wang'
    proto_instance['email'] = 'aa000017@gmail.com'
    proto_instance.save(uuid=True)  # use uuid=True will assign _id a uuid_v4 instead of native ObjectId
    return_msg += "save success</br>"

    query_instance = m_interface.proto.find_one({'name': 'Ophidian Wang'})
    return_msg += str(dict(query_instance))

    return return_msg


if __name__ == '__main__':
    app.run()
