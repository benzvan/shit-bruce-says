from flask import Flask, render_template, request, redirect, url_for, abort
import boto3
import datetime

application = Flask(__name__)

MAX_INPUT_LENGTH = 300

def init_dynamodb_table():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table_name = 'bruce-quotes'
    return dynamodb.Table(table_name)

table = init_dynamodb_table()

def convert_timestamp(quote):
    if 'timestamp' in quote:
        quote['timestamp'] = datetime.datetime.strptime(quote['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
    return quote

def add_quote_to_table(quote, table):
    quote_id = int(datetime.datetime.now().timestamp())
    timestamp = str(datetime.datetime.now())
    table.put_item(Item={'quote_id': quote_id, 'quote': quote, 'timestamp': timestamp})

@application.route('/')
def index():
    response = table.scan()
    quotes = sorted(response.get('Items', []), key=lambda x: x.get('quote_id', 0), reverse=True)
    quotes = [convert_timestamp(quote) for quote in quotes]
    return render_template('index.html', quotes=quotes)

@application.route('/add_quote', methods=['POST'])
def add_quote():
    quote = request.form['quote']
    if len(quote) > MAX_INPUT_LENGTH:
        abort(400, description=f"Input length exceeds maximum limit of {MAX_INPUT_LENGTH} characters.")
    add_quote_to_table(quote, table)
    return redirect(url_for('index'))

if __name__ == '__main__':
    application.run()
