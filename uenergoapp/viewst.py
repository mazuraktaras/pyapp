from flask import request, render_template, url_for, jsonify

from uenergoapp.tasks import mess, parse_html_tags
from uenergoapp import app


@app.route('/')
def index():
    return render_template('ue_ajax.j2')


@app.route('/s')
def indexs():
    return render_template('ue_canvasjs.j2')


@app.route('/start', methods=['POST', 'GET'])
def start():
    url = request.form['url']
    tag_task = parse_html_tags.delay(url)
    return jsonify({'taskid': tag_task.id}), 202, {'Location': url_for('task_state', task_id=tag_task.id)}


@app.route('/task_state/<task_id>', methods=['POST', 'GET'])
def task_state(task_id):
    tag_task = parse_html_tags.AsyncResult(task_id)
    return jsonify({'task_id': task_id, 'task_state': tag_task.state,
                    'result_url': url_for('task_result', task_id=tag_task.id)}), 202, {}


@app.route('/task_result/<task_id>', methods=['POST', 'GET'])
def task_result(task_id):
    tag_task = parse_html_tags.AsyncResult(task_id)
    return jsonify(tag_task.get())


if __name__ == '__main__':
    pass
