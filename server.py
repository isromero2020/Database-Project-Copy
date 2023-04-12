
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import random
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://yt2749:8572@34.75.94.195/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#


# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
# );""")


'''
engine.execute(
    """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
'''


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("We ran out of steam :/")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def start():
    return render_template('start.html')


@app.route('/main')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """

    # DEBUG: this is debugging code to see what request looks like
    # print(request.args)

    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT line_name FROM lines")
    names = []
    for result in cursor:
        # can also be accessed using result[0]
        names.append(result['line_name'])
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


@app.route('/booking/')
def booking():
    return render_template("booking.html")


@app.route("/ticketLookup/", methods=['GET'])
def ticketLookup():
    origin = request.args['origin-select']
    dest = request.args['dest-select']
    requestedTime = request.args['departtime']
    cursor = g.conn.execute(
        'SELECT * FROM tickets WHERE origin_id=%s AND destination_id=%s AND userid is NULL AND departtime > %s',origin, dest, requestedTime)
    tickets = []
    for result in cursor:
        tickets.append(result)
    cursor.close()
    if len(tickets) == 0:
        tickets = ["There are no tickets that match your criteria :/. Please try again."]
        context = dict(data=tickets)
        return render_template("booking.html", **context)
    context = dict(data=tickets)
    return render_template("ticketLookup.html", **context)


'''
@app.route('/ticketConfirmation', methods=['GET'])
def ticketConfirmation():
    #if request.method == 'POST':    
        #ticketId = request.args['ticketID']
        return render_template('another.html')
        ticket = []
        ticket.append(ticketId)
        context = dict(data=ticket)
        app.logger.debug(context)
        return render_template("ticketConfirmation.html", **context)
    #else:
        return redirect('/booking')
'''

@app.route('/confirmation', methods=['GET','POST'])
def confirmation():
    if request.method=="POST":
        ticketId = request.form['ticketId']
        ticketPrice = request.form['price']
        #check if user has proper balance to pay
        query1 = ("SELECT balance FROM users WHERE userid = '{}'".format(userid))
        cursor = g.conn.execute(query1)
        balance = cursor.fetchone()
        currBalance = float(balance[0])-float(ticketPrice)
        currBalance = round(currBalance,2)
        if currBalance < 0:
            img = "https://media2.giphy.com/media/kSRDfrzN3yDK/giphy.gif"
            msg = "Insufficient Funds! Log out and get yo money up homie"
            return render_template("ticketLookup.html", msg=msg, img=img)
        #if they do then we update their ticket balance
        query2 = ("UPDATE users SET balance='{}' WHERE userid = '{}'".format(currBalance,userid))
        g.conn.execute(query2)
        # update ticket userid in tickets
        query3 = ("UPDATE tickets SET userid = '{}' WHERE ticket_id = '{}'".format(userid, ticketId))
        g.conn.execute(query3)
        # update reserved_by table
        query4 = ("INSERT INTO reserved_by VALUES('{}','{}')".format(ticketId,userid))
        g.conn.execute(query4)
        # add to users ticket count
        query5 = ("SELECT ticket_count FROM users WHERE userid='{}'".format(userid))
        cursor = g.conn.execute(query5)
        count = cursor.fetchone()
        newCount = int(count[0])+1
        query6 = ("UPDATE users SET ticket_count = '{}' WHERE userid = '{}'".format(newCount, userid))
        g.conn.execute(query6)
        cursor.close()
        return render_template("confirmation.html", ticketid=ticketId, balance=currBalance)

@app.route('/another')
def another():
    return render_template("another.html")


@app.route('/search')
def search():
    """
    cursor = g.conn.execute("SELECT ticket_id FROM Tickets")
    ticket_ids = []
    for result in cursor:
        # can also be accessed using result[0]
        ticket_ids.append(result['ticket_id'])
    cursor.close()
    context = dict(data=ticket_ids)
    """
    return render_template("search.html")


# Example of adding new data to the database
@app.route('/log_in', methods=['GET'])
def log_in():
    global userid 
    userid = request.args['login']
    cursor_1 = g.conn.execute("SELECT * FROM users WHERE userid = %s", userid)
    user = cursor_1.fetchone()
    if user:
        balance = user['balance']
        cursor_1.close()
        tickets = []
        cursor_2 = g.conn.execute(
            "SELECT * FROM tickets WHERE userid = %s", userid)
        for result in cursor_2:
            tickets.append(result)
        cursor_2.close()
        if len(tickets) == 0:
            msg = "No tickets for you... yet!"
            context = dict(data=[])
            return render_template('index.html', **context, msg=msg, balance=balance)
        context = dict(data=tickets)
        return render_template('index.html', **context, balance=balance)
    else:
        cursor_1.close()
        msg = ["Looks like you're not a user:(", 'Register using the form!']
        context = dict(data=msg)
        return render_template('start.html', **context)
    # g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
    return redirect('/')


@ app.route('/register', methods=['GET', 'POST'])
def register():
    userid = request.form['register']
    cursor = g.conn.execute("SELECT * FROM users WHERE userid = %s", userid)
    if cursor.fetchone():
        cursor.close()
        msg = [
            "Username is already taken :(", 'Register with a different id!']
        context = dict(data=msg)
        return render_template('start.html', **context)
    else:
        if len(userid) <= 20:
            g.conn.execute(
                "INSERT INTO users (userid, balance, ticket_count) VALUES (%s, 100, 0)", userid)
            cursor.close()
            msg = ["Successfully registered!",
                   "You're ready to start planning your trip!"]
            context = dict(data=msg)
            return render_template('start.html', **context)
        else:
            #flash("Username is too long :(")
            msg = ["Username is too long :(", "Try under 20 characters!"]
            context = dict(data=msg)
            return render_template('start.html', **context)


@ app.route("/lookup", methods=['GET'])
def lookup():

    userid = request.args['userid']
    tickets = []
    cursor = g.conn.execute(
        'SELECT ticket_id, origin_id, destination_id, price FROM tickets WHERE userid = %s', userid)
    for result in cursor:
        tickets.append(
            (result["ticket_id"], result["origin_id"], result["destination_id"], result["price"]))
    cursor.close()
    if len(tickets) == 0:
        message = ["No tickets were found for you!",
                   "Let's book a trip now!"]
        context = dict(data=message)
        return render_template("booking.html", **context)

    else:
        context = dict(data=tickets)
        return render_template("search.html", **context)


@app.route('/pay', methods=['POST'])
def pay():
    amount = request.form['amount']
    amount = round(float(amount),2)
    userid = request.form['userid']
    cursor_1 = g.conn.execute(
        'SELECT balance FROM users WHERE userid = %s', userid)
    if cursor_1.rowcount == 0:
        errorMsg = "Please put a valid username for pay system"
        return render_template("start.html", msg=errorMsg)
    curr_balance = cursor_1.fetchone()[0]
    cursor = g.conn.execute(
        'UPDATE users SET balance = %s WHERE userid = %s', amount+curr_balance, userid)
    cursor.close()
    msg = "Successfully Added ${} to {}'s account!".format(amount,userid)
    # return redirect("/log_in?login=%s", userid)
    return render_template("start.html", msg=msg)
    
@app.route('/cancelBooking', methods = ['GET','POST'])
def cancelBooking():
    if request.method=='POST':
        ticketId = request.form['ticketId']
        ticketPrice = request.form['price']
        #delete name from tickets
        query1 = ("UPDATE tickets SET userid = NULL WHERE ticket_id = '{}'".format(ticketId))
        g.conn.execute(query1)
        #decrement ticket count by one
        query2 = ("SELECT balance,ticket_count FROM users WHERE userid = '{}'".format(userid))
        cursor = g.conn.execute(query2)
        tmp = cursor.fetchone()
        ticketCount = int(tmp[1])-1
        query3 = ("UPDATE users SET ticket_count = {} WHERE userid = '{}'".format(ticketCount,userid))
        g.conn.execute(query3)
        #add ticket price to users balance
        newBalance = float(tmp[0])+float(ticketPrice)
        newBalance = round(newBalance,2)
        query4 = ("UPDATE users SET balance='{}' WHERE userid='{}'".format(newBalance,userid))
        g.conn.execute(query4)
        #delete from reserved by table
        query5 = ("DELETE FROM reserved_by WHERE ticket_id='{}'".format(ticketId))
        g.conn.execute(query5)
        cursor.close()
        return render_template("cancelBooking.html", balance=newBalance)

@ app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @ click.command()
    @ click.option('--debug', is_flag=True)
    @ click.option('--threaded', is_flag=True)
    @ click.argument('HOST', default='0.0.0.0')
    @ click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python3 server.py

        Show the help text using:

            python3 server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

    run()
