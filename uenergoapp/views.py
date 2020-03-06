from flask import request, render_template, url_for, jsonify

from uenergoapp.tasks import parse_html_tags
from uenergoapp import app, database, Tags


@app.route('/')
def index() -> object:
    """
    Render the main page
    @return: response object for main page
    """
    return render_template('ue_bootstrap.j2', title='UENERGO TAGS')


@app.route('/start', methods=['POST'])
def start():
    """
    Take URL for task and start background task
    Return the HTTP response object with background task id, response code, and URL
    for task state in Location HTTP header
    @rtype: object
    """
    url = request.form['url']
    tag_task = parse_html_tags.delay(url)
    return jsonify({'taskid': tag_task.id}), 202, {'Location': url_for('task_state', task_id=tag_task.id)}


@app.route('/task_state/<task_id>', methods=['POST', 'GET'])
def task_state(task_id):
    """
    Take the task id
    Return the HTTP response object with task result status
    @rtype: object
    """
    tag_task = parse_html_tags.AsyncResult(task_id)
    return jsonify({'task_id': task_id, 'task_state': tag_task.state,
                    'result_url': url_for('task_result', task_id=tag_task.id)}), 202, {}


@app.route('/task_result/<task_id>', methods=['POST', 'GET'])
def task_result(task_id):
    """
    Take the task id
    Return the HTTP response object with task result
    @rtype: object
    """
    tag_task = parse_html_tags.AsyncResult(task_id)
    return jsonify(tag_task.get())
