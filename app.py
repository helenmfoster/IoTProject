from flask import Flask, render_template
import atRunTime as TruckRouter
import sqlite3 as sql

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/truck_routes')
def truck_routes():
    routes = TruckRouter.get_routes()
    ##print routes

    trucks = []

    con = sql.connect('trash_nodes.db')
    with con:
        cur = con.cursor()
        for r in routes:
            nodes = []
            for node in r:
                cur.execute("SELECT * FROM nodes WHERE id = ?", (node,));
                result = cur.fetchall()
                if len(nodes) < 8:
                    nodes.append([result[0][1], result[0][2]])
            print len(nodes)
            trucks.append(nodes)




    #test data
    #trucks = [[[42.0000, -87.6800], [42.0509, -87.6909]], [[42.0509, -87.6909], [42.0509, -87.6910], [42.0509, -87.6911]]]


    return render_template('truck_routes.html', trucks = trucks)


if __name__ == '__main__':
  app.run()
  ##truck_routes()
