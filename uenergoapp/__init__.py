from flask import Flask

# app = Flask(__name__, instance_relative_config=False)
app = Flask(__name__)
# app.config.from_object('config')
# Views must be imported after app object created due Flask developers recommendation


from uenergoapp import viewst
