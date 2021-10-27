from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
from models import database, User, UserRole;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
import re;
from adminDecorator import roleCheck;

application = Flask ( __name__ );
application.config.from_object ( Configuration );

def calculate(jmbg):
    a = int(jmbg[0]);
    b = int(jmbg[1]);
    c = int(jmbg[2]);
    d = int(jmbg[3]);
    e = int(jmbg[4]);
    f = int(jmbg[5]);
    g = int(jmbg[6]);
    h = int(jmbg[7]);
    i = int(jmbg[8]);
    j = int(jmbg[9]);
    k = int(jmbg[10]);
    l = int(jmbg[11]);

    m =  11 - ((7 * (a + g) + 6 * (b + h) + 5 * (c + i) + 4 * (d + j) + 3 * (e + k) + 2 * (f + l)) % 11);

    if( m in range (1, 10)):
        return m;
    else:
        return 0;


@application.route ( "/register", methods = ["POST"] )
def register ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );
    forename = request.json.get ( "forename", "" );
    surname = request.json.get ( "surname", "" );
    jmbg = request.json.get("jmbg", "");

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;
    forenameEmpty = len ( forename ) == 0;
    surnameEmpty = len ( surname ) == 0;
    jmbgEmpty = len (jmbg) == 0;

    if (jmbgEmpty):
        return jsonify(message="Field jmbg is missing."), 400
    if (forenameEmpty):
        return jsonify(message="Field forename is missing."), 400
    if (surnameEmpty):
        return jsonify(message="Field surname is missing."), 400
    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400
    if (passwordEmpty):
        return jsonify(message="Field password is missing."), 400

    if( len(jmbg) == 13):
        if( int (jmbg[0:2]) in range (1, 32)):
            if (int(jmbg[2:4]) in range (1, 13)):
                if(int(jmbg[4:7]) in range (000, 1000)):
                    if(int(jmbg[7:9]) in range (70, 100)):
                        if(int(jmbg[9:12]) in range (0, 1000)):
                            if(int(jmbg[12]) != calculate(jmbg)):
                                return jsonify(message="Invalid jmbg."), 400
                        else:
                            return jsonify(message="Invalid jmbg."), 400
                    else:
                        return jsonify(message="Invalid jmbg."), 400
                else:
                    return jsonify(message="Invalid jmbg."), 400
            else:
                return jsonify(message="Invalid jmbg."), 400
        else:
            return jsonify(message="Invalid jmbg."), 400
    else:
        return jsonify(message="Invalid jmbg."), 400

    if (len(forename) > 256):
        return jsonify(message="Forename have more than 256 characters!"), 400

    if (len(surname) > 256):
        return jsonify(message="Surname have more than 256 characters!"), 400

    if(len(email) > 256):
        return jsonify(message="Invalid email."), 400
    result = parseaddr ( email );
    # if ( len ( result[1] ) == 0 ):
    #     return jsonify(message="Invalid email."), 400
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b';
    if(not (re.match(regex, email))):
        return jsonify(message="Invalid email."), 400

    if(len(password) < 8 or len(password) > 256):
        return jsonify(message="Invalid password."), 400

    regex = "(?=.*[a-z])(?=.*[A-Z])(?=.*\d)";

    if(not re.search(regex, password)):
        return jsonify(message="Invalid password."), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify(message='Email already exists.'), 400

    user = User ( email = email, password = password, forename = forename, surname = surname, jmbg= jmbg );
    database.session.add ( user );
    database.session.commit ( );

    userRole = UserRole ( userId = user.id, roleId = 2 );
    database.session.add ( userRole );
    database.session.commit ( );

    return Response (status = 200 );

jwt = JWTManager ( application );

@application.route ( "/login", methods = ["POST"] )
def login ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;

    if ( emailEmpty ):
        return jsonify(message="Field email is missing."), 400
    if ( passwordEmpty ):
        return jsonify(message="Field password is missing."), 400

    if (len(email) > 256):
        return jsonify(message="Invalid email."), 400
    result = parseaddr(email);
    # if (len(result[1]) == 0):
    #     return jsonify(message="Invalid email."), 400
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (not (re.match(regex, email))):
        return jsonify(message="Invalid email."), 400

    if (len(password) > 256):
        return jsonify(message="Password have more than 256 characters!"), 400

    user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( );

    if ( not user ):
        return jsonify(message="Invalid credentials."), 400
    additionalClaims = {
            "jmbg": user.jmbg,
            "forename": user.forename,
            "surname": user.surname,
            "roles": [ str ( role ) for role in user.roles ]
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    return jsonify ( accessToken = accessToken, refreshToken = refreshToken ),200


@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):

    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    additionalClaims = {
            "jmbg": refreshClaims["jmbg"],
            "forename": refreshClaims["forename"],
            "surname": refreshClaims["surname"],
            "roles": refreshClaims["roles"]
    };

    accessToken = create_access_token ( identity = identity, additional_claims = additionalClaims );

    return jsonify(accessToken= accessToken), 200

@application.route("/delete", methods=["POST"])
@roleCheck(role = "admin")
def delete():
    email = request.json.get("email", "");

    emailEmpty = len(email) == 0;

    if(emailEmpty):
        return jsonify(message="Field email is missing."), 400

    if (len(email) > 256):
        return jsonify(message="Invalid email."), 400
    # result = parseaddr(email);
    # if (len(result[1]) == 0):
    #     return jsonify(message="Invalid email."), 400
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b';
    if (not (re.match(regex, email))):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if (not user):
        return jsonify(message="Unknown user."), 400

    userRoles = UserRole.query.filter(UserRole.userId == user.id).all();

    for userRole in userRoles:
        database.session.delete(userRole);
        database.session.commit();

    database.session.delete(user);
    database.session.commit();

    return Response(status=200)


@application.route ( "/", methods = ["GET"] )
def index ( ):
    return "Hello world!";

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5001 );