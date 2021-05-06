import flask
import json
app = flask.Flask(__name__)

@app.route('/algo/v1/video/saveVideo', methods=['GET', 'POST'])
def receive():
    print('get')
    data = json.loads(flask.request.get_data(as_text=True))
    scenicId = data['scenicId']
    touristId = data['touristId']
    path = data['path']
    print('scenicId',scenicId, 'touristId',touristId, 'path',path)
    return flask.jsonify({'status': '0', 'errmsg': '登录成功！'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8084, debug=True,
        threaded=True, use_reloader=False)
