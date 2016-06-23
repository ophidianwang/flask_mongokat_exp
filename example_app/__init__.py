# -*- coding: utf-8 -*-
from flask import Flask
from flask_mongokat import MongoKat

app = Flask(__name__)
app.config.from_object('websiteconfig')
m_interface = MongoKat(app)


@app.route('/')
def show_entries():
    query_instance = m_interface.proto.find_one({'name': 'proto_name'})
    return_msg = str(dict(query_instance))
    return return_msg


from example_app.views import proto
app.register_blueprint(proto.mod, url_prefix='/proto')


if __name__=='__main__':
  app.run()