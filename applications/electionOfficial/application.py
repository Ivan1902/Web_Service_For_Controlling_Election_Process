import csv
import io

from flask import Flask, request, jsonify, Response;
from configuration import Configuration;
from models import database, Participant, Election, ElectionParticipant, Vote;
from redis import Redis;
from electionOfficialDecorator import roleCheck;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity;
import datetime;
from sqlalchemy import and_;

application = Flask ( __name__ );
application.config.from_object ( Configuration )
jwt = JWTManager ( application );

@application.route("/", methods=["GET"])
def index ():
    return "Hello World!";

@application.route("/vote", methods=["POST"])
@roleCheck(role = "electionOfficial")
def vote():
    #identity = get_jwt_identity();
    refreshClaims = get_jwt();

    content = request.files.get("file", "");

    contentEmpty = content == "";

    if(contentEmpty):
        return jsonify(message="Field file is missing."), 400

    stream = io.StringIO ( content.stream.read( ).decode("utf-8"));
    reader = csv.reader( stream );

    class Row :
        def __init__(self, ballotGuid, pollNumber):
            self.ballotGuid = ballotGuid;
            self.pollNumber = pollNumber;

    votes = [ ];
    i = 0;

    for row in reader:
        if( len(row) != 2 ):
            return jsonify(message="Incorrect number of values on line {}.".format(i)), 400
        try:
            vote = int ( row[1] );
        except:
            return jsonify(message="Incorrect poll number on line {}.".format(i)), 400
        if(int( row[1] ) < 1):
            return jsonify(message="Incorrect poll number on line {}.".format(i)), 400

        i = i + 1;
        votes.append(Row(row[0], row[1]));

    electionOfficialJmbg = refreshClaims["jmbg"];

    with Redis ( Configuration.REDIS_HOST ) as redis:
        for vote in votes:
            nowIso = datetime.datetime.strptime(str(datetime.datetime.now().isoformat("T", "seconds")),
                                                "%Y-%m-%dT%H:%M:%S");
            print(nowIso);
            redis.rpush( Configuration.REDIS_VOTES_LIST , str (vote.ballotGuid + "," + vote.pollNumber + "," +
                                                               electionOfficialJmbg + "," + str(nowIso)));

    return Response(status=200);

if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True,host = "0.0.0.0", port = 5003 );