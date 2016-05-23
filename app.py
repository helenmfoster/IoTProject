from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/truck_routes')
def truck_routes():
    return render_template('truck_routes.html')

if __name__ == '__main__':
  app.run()
