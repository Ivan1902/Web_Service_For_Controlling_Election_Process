import csv
import io

from flask import Flask, request, jsonify, Response;
from configuration import Configuration;
from models import database, Participant, Election, ElectionParticipant, Vote;
from redis import Redis;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
import datetime;
from sqlalchemy import and_;
from datetime import timedelta;

application = Flask ( __name__ );
application.config.from_object ( Configuration )
jwt = JWTManager ( application );

def getCurrentElectionWithoutTimeZone(nowIsoTime):
    nowIso = datetime.datetime.strptime(nowIsoTime, "%Y-%m-%d %H:%M:%S");
    elections = Election.query.all();
    nowIso = nowIso + timedelta(hours=2);
    print(nowIso)
    #print(str(nowIso))
    for election in elections:
        startIso = datetime.datetime.strptime(election.start, "%Y-%m-%dT%H:%M:%S");
        endIso = datetime.datetime.strptime(election.end, "%Y-%m-%dT%H:%M:%S");

        if(nowIso > startIso and nowIso < endIso):
            return election;

    return None;

def getCurrentElectionWithTimeZone():
    nowIso = datetime.datetime.strptime(str(datetime.datetime.now().isoformat("T", "seconds") ),
                                     "%Y-%m-%dT%H:%M:%S%z");
    elections = Election.query.all();
    for election in elections:
        startIso = datetime.datetime.strptime(election.start, "%Y-%m-%dT%H:%M:%S%z");
        endIso = datetime.datetime.strptime(election.end, "%Y-%m-%dT%H:%M:%S%z");

        if(nowIso > startIso and nowIso < endIso):
            return election;

    return None;


if (__name__ == "__main__"):
    database.init_app ( application );
    print('c')
    with application.app_context():
        while True:
            with Redis ( Configuration.REDIS_HOST ) as redis:
                _, bytes = redis.blpop ( Configuration.REDIS_VOTES_LIST );
                row = bytes.decode ("utf-8");
                #print(row);

                data = row.split(",");
                ballotGuid = data [0];
                pollNumber = data [1];
                electionOfficialJmbg = data [2];
                nowIso = data [3];

                election = getCurrentElectionWithoutTimeZone(nowIso);
                #print('b')
                if(election is not None):
                    #('a')
                    reason = None;
                    if(Vote.query.filter(Vote.ballotGuid == ballotGuid).first()):
                        reason = "Duplicate ballot.";
                    if( not ( ElectionParticipant.query.filter(and_(ElectionParticipant.electionId == election.id,
                                                                    ElectionParticipant.pollNumber == pollNumber)
                                                               ).first()) ):
                        reason = "Invalid poll number.";

                    vote = Vote(ballotGuid=ballotGuid, pollNumber=pollNumber, electionOfficialJmbg=electionOfficialJmbg,
                                idElection=election.id, reason=reason);
                    database.session.add(vote);
                    database.session.commit( );

