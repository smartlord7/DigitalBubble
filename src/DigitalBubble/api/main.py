##
# =============================================
# ============== Bases de Dados ===============
# ============== LEI  2021/2022 ===============
# =============================================
# === Department of Informatics Engineering ===
# =========== University of Coimbra ===========
# =============================================
##
# Authors:
# André Colaço       <andrecolaco@student.dei.uc.pt>
# Sancho Simoes      <sanchosimoes@student.dei.uc.pt>

import jwt
import flask
import logging
import psycopg2
from hashlib import sha512
from functools import wraps
from flask import request, jsonify
from http import HTTPStatus
from psycopg2 import extensions
from data.enum.role_enum import Roles
from data.enum.product_enum import ProductType
from data.model.classification import Classification
from data.model.comment import Comment
from data.model.seller import Seller
from data.model.user import User
from data.model.computer import Computer
from data.model.smartphone import Smartphone
from data.model.television import Television
from data.model.product import Product
from db.connection_factory import ConnectionFactory

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'
app.config['HOST'] = '127.0.0.1'
app.config['APP_PORT'] = 8080
app.config['DB_PORT'] = 5432
app.config['DATABASE'] = 'DigitalBubble'
app.config['USER'] = 'digitalbubbleadmin'
app.config['PASSWORD'] = 'digitalbubble123#'

logger = None
conn_fac = None


def _setup_logger():
    global logger
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _setup_connection():
    global conn_fac
    conn_fac = ConnectionFactory()
    conn_fac.host = app.config['HOST']
    conn_fac.port = app.config['DB_PORT']
    conn_fac.database = app.config['DATABASE']
    conn_fac.user = app.config['USER']
    conn_fac.password = app.config['PASSWORD']


def _start_app():
    host = app.config['HOST']
    port = app.config['APP_PORT']
    logger.info(f'API v1 online: http://{host}:{port}//{app.config["API_PREFIX"]}')
    app.run(host=host, debug=True, port=port)


def authorization(roles):
    def authorization_(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if not request:
                return None
            token = None
            if "HTTP_AUTHORIZATION" in request.environ:
                token = request.environ["HTTP_AUTHORIZATION"].replace("Bearer ", "")

            if not token:
                return jsonify({'error': 'A valid token is missing'}), HTTPStatus.UNAUTHORIZED
            try:
                data = jwt.decode(
                    token, app.config['SECRET_KEY'], algorithms=["HS256"])
                if roles != 'all' and data['role'] not in roles:
                    return jsonify({}), HTTPStatus.UNAUTHORIZED
            except:
                return jsonify({'error': 'Token is invalid'}), HTTPStatus.UNAUTHORIZED

            return f(*args, **kwargs)

        return decorator

    return authorization_


def get_session():
    token = None

    if "HTTP_AUTHORIZATION" in request.environ:
        token = request.environ["HTTP_AUTHORIZATION"]

    if not token:
        return None
    try:
        token = token.replace("Bearer ", "")
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        return data
    except:
        return None


@app.route(f'/{app.config["API_PREFIX"]}')
def landing_page():
    return """
            Hello World! Welcome to DigitalBubble, a digital platform where you can sell your products!<br/>
            <br/>
            Check the sources for instructions on how to use the endpoints!<br/>
            <br/>
            Digital Bubble<br/>
            <br/>
            """


@app.route(f'/{app.config["API_PREFIX"]}/user/', methods=['POST'])
def register():
    """Function that allows the registration of users
    """

    logger.info('POST /user')
    payload = flask.request.get_json()
    logger.debug(f'POST /user - payload: {payload}')

    response = dict()
    status = HTTPStatus.OK
    role = None

    if 'role' in payload:
        role = payload['role']

        if role == Roles['Admin'] or role == Roles['Seller']:
            session = get_session()

            if not session:
                return jsonify({'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED

            if session["role"] != Roles["Admin"]:
                return jsonify({}), HTTPStatus.UNAUTHORIZED

    if role == Roles['Seller']:
        u = Seller()
    else:
        u = User()

    model_errors = u.bind_json(payload)

    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    password_hash = sha512(payload['password'].encode()).hexdigest()

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()

        stmt = 'INSERT INTO "user" (user_name, first_name, email, tin, role, last_name, phone_number, password_hash, \
            house_no, street_name, city, state, zip_code) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id'
        val = (u.user_name, u.first_name, u.email, u.tin, u.role, u.last_name,
               u.phone_number, password_hash, u.house_no, u.street_name,
               u.city, u.state, u.zip_code)

        cur.execute(stmt, val)
        user_id = cur.fetchone()

        if role == Roles['Admin']:
            statement = 'INSERT INTO admin (user_id) VALUES (%s)'
            values = user_id
        elif role == Roles['Seller']:
            statement = 'INSERT INTO seller (user_id, company_name) VALUES (%s, %s)'
            values = (user_id, u.company_name)
        else:
            statement = 'INSERT INTO buyer (user_id) VALUES (%s)'
            values = user_id

        response['result'] = user_id

        cur.execute(statement, values)
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/user/', methods=['PUT'])
def login():
    """
    Function that allows an user to login using its username and password
    """

    logger.info('PUT /user')
    payload = flask.request.get_json()
    logger.debug(f'POST /user - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    user_name = payload['user_name']

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()
        stmt = 'SELECT id, role, password_hash  ' \
               'FROM "user" ' \
               'WHERE user_name = %s'
        val = (user_name, )

        cur.execute(stmt, val)
        rows = cur.fetchone()

        if not rows or len(rows) == 0:
            error = f'User {user_name} not found'
            logger.error(f'PUT /user/ - error: {error}')
            response['error'] = str(error)
            status = HTTPStatus.NOT_FOUND
        else:
            user = rows
            password = payload['password']
            password_hash_given = sha512(password.encode()).hexdigest()
            user_id = user[0]
            role = user[1]
            password_hash_db = user[2]

            if password_hash_given != password_hash_db:
                error = f'Wrong password'
                logger.error(f'PUT /user/ - error: {error}')
                response['error'] = str(error)
                status = HTTPStatus.BAD_REQUEST
            else:
                token_data = {
                    "id": user_id,
                    "user_name": user_name,
                    "role": role
                }

                token = jwt.encode(
                    payload=token_data,
                    key=app.config['SECRET_KEY'],
                    algorithm='HS256',
                )

                response['result'] = token

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/product/', methods=['POST'])
@authorization(roles=[Roles["Seller"]])
def create_product():
    """Function that allows the creation of a new product
    """

    logger.info('POST /product')
    payload = flask.request.get_json()
    logger.debug(f'POST /product - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    session = get_session()
    seller_id = session['id']
    type_product = None

    if 'type' in payload:
        type_product = payload['type']

        if type_product == ProductType['Computer']:
            p = Computer()
        elif type_product == ProductType['Television']:
            p = Television()
        elif type_product == ProductType['Smartphone']:
            p = Smartphone()
        else:
            p = Product()
    else:
        p = Product()

    model_errors = p.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()

        stmt = 'INSERT INTO product ' \
               '(id, name, price, stock, description, category, seller_id, version, update_timestamp) ' \
               'VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM product), %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) ' \
               'returning id '
        val = (p.name, p.price, p.stock, p.description, p.category, seller_id, 1)

        cur.execute(stmt, val)
        product_id = cur.fetchone()

        if type_product:
            if type_product == ProductType['Computer']:
                stmt = 'INSERT INTO computer ' \
                       '(cpu, gpu, product_id, product_version) ' \
                       'VALUES (%s, %s, %s, %s)'
                val = (p.cpu, p.gpu, product_id, 1)
            elif type_product == Roles['Smartphone']:
                stmt = 'INSERT INTO smartphone ' \
                       '(model, operative_system, product_id, product_version) ' \
                       'VALUES (%s, %s, %s)'
                val = (p.model, p.operative_system, product_id, 1)
            elif type_product == Roles['Television']:
                stmt = 'INSERT INTO television ' \
                       '(size, technology, product_id, product_version) ' \
                       'VALUES (%s, %s, %s, %s)'
                val = (p.size, p.technology, product_id, 1)

            cur.execute(stmt, val)
        connection.commit()

        response['result'] = product_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/product/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['PUT'])
@authorization(roles=[Roles["Seller"]])
def update_product(product_id):
    """Function that allows the update an existing product
    """

    logger.info('PUT /product/<product_id>')
    logger.debug(f'product_id: {product_id}')
    payload = flask.request.get_json()
    logger.debug(f'POST /product - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    session = get_session()
    connection = conn_fac.get_connection()
    cur = connection.cursor()

    user_id = session['id']

    try:
        product_statement = 'SELECT id, version, seller_id, type ' \
                            'FROM product ' \
                            'WHERE id = %s AND version = (SELECT MAX(version)' \
                            '                             FROM product ' \
                            '                             WHERE id = %s )'
        values = (product_id, product_id)

        cur.execute(product_statement, values)
        product = cur.fetchone()
        product_id = product[0]

        if product_id is None:
            return jsonify({}), HTTPStatus.NOT_FOUND

        version = product[1]
        seller_id = product[2]
        type_product = product[3]

        if seller_id != user_id:
            return jsonify({}), HTTPStatus.UNAUTHORIZED

        if type_product == ProductType['Computer']:
            p = Computer()
        elif type_product == ProductType['Television']:
            p = Television()
        elif type_product == ProductType['Smartphone']:
            p = Smartphone()
        else:
            p = Product()

        model_errors = p.bind_json(payload)
        if model_errors:
            return model_errors, HTTPStatus.BAD_REQUEST
        statement_product = 'INSERT INTO product ' \
                            '(id, name, price, stock, description, category,' \
                            'type, seller_id, version, update_timestamp) ' \
                            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'
        values_product = (
            product_id, p.name, p.price, p.stock, p.description, p.category, type_product, seller_id, version + 1)

        cur.execute(statement_product, values_product)

        if type_product:
            if type_product == ProductType['Computer']:
                stmt = 'INSERT INTO computer ' \
                            '(cpu, gpu, product_id, product_version) ' \
                            'VALUES (%s, %s, %s, %s)'
                val = (p.cpu, p.gpu, product_id, version + 1)
            elif type_product == Roles['Smartphone']:
                stmt = 'INSERT INTO smartphone ' \
                            '(model, operative_system, product_id, product_version) ' \
                            'VALUES (%s, %s, %s, %s)'
                val = (p.model, p.operative_system, product_id, version + 1)
            else:
                stmt = 'INSERT INTO television ' \
                            '(size, technology, product_id, product_version) ' \
                            'VALUES (%s, %s, %s, %s)'
                val = (p.size, p.technology, product_id, version + 1)

            cur.execute(stmt, val)

        connection.commit()

        response['result'] = product_id
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT {app.config["API_PREFIX"]}/product/<product_id> - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()
    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/rating/<product_id>', methods=['POST'])
@authorization(roles=[Roles["Admin"], Roles["Buyer"]])
def rate_product(product_id):
    """Function that allows the rating of a product with a value between 0 and 5 and a comment
    """

    logger.info('POST /rating/<product_id>')
    logger.debug(f'product_id: {product_id}')
    payload = flask.request.get_json()
    logger.debug(f'POST /rating/<product_id> - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    session = get_session()
    buyer_id = session['id']

    c = Classification()

    model_errors = c.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()
        stmt = 'SELECT name ' \
               'FROM product ' \
               'WHERE id = %s'
        val = (product_id,)

        cur.execute(stmt, val)
        product = cur.fetchone()

        if product[0] is None:
            return jsonify({}), HTTPStatus.NOT_FOUND

        stmt = 'INSERT INTO classification ' \
               '(rating, comment, buyer_id, product_id) ' \
               'VALUES (%s, %s, %s, %s) returning id'
        val = (c.rating, c.comment, buyer_id, product_id)

        cur.execute(stmt, val)
        connection.commit()

        classification_id = cur.fetchone()
        response['result'] = classification_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT {app.config["API_PREFIX"]}/product/<product_id> - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()
    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/order/', methods=['POST'])
@authorization(roles=[Roles["Admin"], Roles["Buyer"]])
def create_order():
    logger.info('POST /order')
    payload = flask.request.get_json()
    logger.debug(f'POST /order - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    session = get_session()
    buyer_id = session['id']

    try:
        connection = conn_fac.get_connection()
        connection.set_isolation_level(extensions.ISOLATION_LEVEL_SERIALIZABLE)
        cur = connection.cursor()

        stmt = 'INSERT INTO "order"' \
               '(order_timestamp, buyer_id, is_complete)' \
               'VALUES (CURRENT_TIMESTAMP, %s, %s) returning id'
        val = (buyer_id, '0')

        cur.execute(stmt, val)
        order_id = cur.fetchone()

        cart = payload['cart']

        for item in cart:
            product_id = item[0]
            product_quantity = item[1]

            stmt = 'SELECT stock ' \
                   'FROM product ' \
                   'WHERE id = %s'
            val = (product_id,)
            cur.execute(stmt, val)

            stock = cur.fetchone()[0]

            if stock is None:
                status = HTTPStatus.NOT_FOUND

                break

            if stock < product_quantity:
                status = HTTPStatus.BAD_REQUEST

                response['error'] = 'Insufficient stock for product %d: have %d' % (product_id, stock)

                break

            stmt = "UPDATE product " \
                   "SET stock = stock - %s " \
                   "WHERE id = %s"
            val = (product_quantity, product_id)

            cur.execute(stmt, val)

            stmt = 'INSERT INTO item' \
                   '(quantity, product_id, order_id)' \
                   'VALUES (%s, %s, %s)'
            val = (product_quantity, product_id, order_id)

            cur.execute(stmt, val)

        stmt = 'UPDATE "order"' \
               'SET is_complete = %s' \
               'WHERE id = %s'
        val = ('1', order_id)

        cur.execute(stmt, val)
        connection.commit()

        response['result'] = order_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/order/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/', methods=['POST'])
@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/<parent_comment_id>', methods=['POST'])
@authorization(roles="all")
def create_comment(product_id, parent_comment_id=None):
    """Function that allows the creation of a comment.
    """

    logger.info('POST /questions/<product_id>')
    logger.debug(f'product_id: {product_id}, parent_comment_id: {parent_comment_id}')
    payload = flask.request.get_json()
    logger.debug(f'POST /questions/<product_id> - payload: {payload}')

    response = dict()
    connection = None
    status = HTTPStatus.OK
    session = get_session()
    user_id = session['id']

    c = Comment()

    model_errors = c.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()

        stmt = 'SELECT name ' \
               'FROM product ' \
               'WHERE id = %s'
        val = (product_id,)
        cur.execute(stmt, val)

        name = cur.fetchone()[0]

        if name is None:
            status = HTTPStatus.NOT_FOUND

            return jsonify({}), status

        stmt = 'INSERT INTO comment ' \
               '(text, parent_id, user_id, product_id)' \
               'VALUES (%s, %s, %s, %s) returning id'
        val = (c.text, parent_comment_id, user_id, product_id)

        cur.execute(stmt, val)
        connection.commit()

        comment_id = cur.fetchone()
        response['result'] = comment_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/questions/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['GET'])
@authorization(roles="all")
def get_product(product_id):
    """Function that allows the retrieval of the information of a product, including its history.
    """

    logger.info('GET /product/<product_id>')

    logger.debug(f'product_id: {product_id}')

    response = dict()
    connection = None
    status = HTTPStatus.OK

    connection = conn_fac.get_connection()
    cur = connection.cursor()

    logger.debug(f'GET /product/<product_id>')

    try:
        statement = 'SELECT description, name, stock, category, 0 AS "Order", \'0\' AS "sub_order" FROM product WHERE ' \
                    'id = 1 AND version = (SELECT MAX(version) FROM product WHERE id = 1) ' \
                    'UNION ' \
                    'SELECT CAST(price AS VARCHAR), CAST(update_timestamp AS VARCHAR) as "time", NULL, NULL, ' \
                    '1 AS "Order", '\
                    'CAST(EXTRACT(EPOCH FROM update_timestamp) AS VARCHAR) AS "sub_order" FROM product WHERE id = 1 ' \
                    'UNION ' \
                    'SELECT CAST(ROUND(AVG(rating), 2) AS VARCHAR), NULL, NULL, NULL, 2 AS "Order", \'0\' AS ' \
                    '"sub_order" '\
                    'FROM classification WHERE product_id = 1 ' \
                    'UNION ' \
                    'SELECT comment, NULL, NULL, NULL, 3 AS "Order", \'0\' AS "sub_order" FROM classification WHERE ' \
                    'product_id = 1 '\
                    'ORDER BY "Order", "sub_order" DESC'
        values = (product_id, product_id)

        cur.execute(statement, values)

        rows = cur.fetchall()
        prices = list()
        comments = list()
        rating = None

        for row in rows:
            if row[4] == 1:
                prices.append(row[1] + " - " + row[0])
            elif row[4] == 2:
                rating = row[0]
            elif row[4] == 3:
                comments.append(row[0])

        response['result'] = {
            'description': rows[0][0],
            'name': rows[0][1],
            'stock': rows[0][2],
            'category': rows[0][3],
            'prices': prices,
            'ratings': rating,
            'comments': comments
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET {app.config["API_PREFIX"]}/product/<product_id> - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/report/year', methods=['GET'])
@authorization(roles=[Roles["Admin"]])
def get_stats():
    """Function that gets a set of global statistics of the platform."""

    logger.debug(f'GET /report/year:')

    response = dict()
    status = HTTPStatus.OK

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()
        stmt = 'SELECT CAST(EXTRACT(MONTH FROM CURRENT_DATE) AS INTEGER), 0 AS "Order" ' \
               'UNION ' \
               'SELECT COUNT(*), 1 AS "Order" ' \
               'FROM "order" ' \
               'WHERE order_timestamp > date_trunc(\'month\', CURRENT_DATE) - INTERVAL \'1 year\' ' \
               'UNION ' \
               'SELECT SUM(i.quantity * (SELECT price ' \
               ' FROM product p ' \
               'WHERE p.id = i.product_id AND ' \
               'p.version = (SELECT MAX(version) ' \
               'FROM product p ' \
               'WHERE p.id = i.product_id))), 2 AS "Order" ' \
               'FROM "order" ' \
               'JOIN item i ON order_id = id ' \
               'WHERE order_timestamp > date_trunc(\'month\', CURRENT_DATE) - INTERVAL \'1 year\'' \
               'ORDER BY "Order"'

        cur.execute(stmt)

        stats = cur.fetchall()

        month = int(stats[0][0])
        total_value = stats[1][0]
        orders = int(stats[2][0])

        response['result'] = {
            'month': month,
            'total_value': total_value,
            'orders': orders
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/questions/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/notifications', methods=['GET'])
@authorization(roles="all")
def get_notifications():
    logger.debug(f'GET /notifications/')

    response = dict()
    status = HTTPStatus.OK

    session = get_session()
    user_id = session['id']

    try:
        connection = conn_fac.get_connection()
        cur = connection.cursor()

        stmt = 'SELECT id, title, description, user_id ' \
               'FROM notification ' \
               'WHERE user_id = %s'
        val = (user_id,)

        cur.execute(stmt, val)
        notifications = cur.fetchall()

        results = list()
        for notification in notifications:
            results.append({
                "id": notification[0],
                "title": notification[1],
                "description": notification[2],
                "user_id": notification[3],
            })
        response['results'] = results

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/order/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        connection.rollback()

    finally:
        if connection is not None:
            connection.close()

    return jsonify(response), status


def main():
    _setup_logger()
    _setup_connection()
    _start_app()


if __name__ == "__main__":
    main()
