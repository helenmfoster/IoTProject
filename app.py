from flask import Flask, render_template
import atRunTime as TruckRouter

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/truck_routes')
def truck_routes():
    ## routes = TruckRouter.get_routes()
    ## Code Goes Here for turning routes into an array of arrays of tuples:
    ##  a series of [lat, long]
    #trucks = [[(42.0006, -87.6850), (42.0500, -87.6900)], [(82.0445, -87.6870), (42.0006, -87.6850), (42.0500, -87.6900)]]

    trucks = [1, 2, 3, 4, 5]

    return render_template('truck_routes.html', trucks = trucks)


if __name__ == '__main__':
  app.run()
