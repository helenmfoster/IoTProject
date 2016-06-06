from flask import Flask, render_template
import atRunTime as TruckRouter

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/truck_routes')
def truck_routes():
    ##routes = TruckRouter.get_routes()
    ## Code Goes Here for turning routes into an array of arrays of tuples:
    ##  a series of [lat, long]
    ## look at trash_nodes.db
    trucks = [[[42.0000, -87.6800], [42.0509, -87.6909]], [[42.0509, -87.6909], [42.0509, -87.6910], [42.0509, -87.6911]]]


    return render_template('truck_routes.html', trucks = trucks)


if __name__ == '__main__':
  app.run()
