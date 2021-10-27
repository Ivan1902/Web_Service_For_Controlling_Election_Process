import json

from flask import Flask, request, jsonify;
from configuration import Configuration;
from models import database, Participant, Election, ElectionParticipant, Vote;
from redis import Redis;
from adminDecorator import roleCheck;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
import datetime;
from sqlalchemy import and_;
from decimal import *;

application = Flask ( __name__ );
application.config.from_object ( Configuration )
jwt = JWTManager ( application );

@application.route("/", methods=["GET"])
def index ():
    return "Hello World!";

@application.route("/createParticipant", methods=["POST"])
@roleCheck(role = "admin")
def createParticipant():

    name = request.json.get("name", "");
    individual = request.json.get("individual", "") ;

    nameEmpty = len(name) == 0;
    individualEmpty = (not isinstance(individual, bool));

    if(nameEmpty):
        return jsonify(message="Field name is missing."), 400

    if (individualEmpty):
        return jsonify(message="Field individual is missing."), 400

    participant = Participant(name=name, individual=individual);

    database.session.add(participant);
    database.session.commit();

    return jsonify(id=participant.id), 200


@application.route("/getParticipants", methods=["GET"])
@roleCheck(role = "admin")
def getParticipants():

    allParticipants = Participant.query.all();
    participants = [ ];
    for participant in allParticipants:
        object = {
            "name" : participant.name,
            "individual" : participant.individual,
            "id": participant.id
        }
        participants.append(object);

    return jsonify(participants=participants), 200

def isDatesValidWithoutTimeZone(start, end):
    #first string cast into iso8601, this may have exception
    try:
        startIso = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S");
        endIso = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S");

        if(startIso > endIso):
            return False;

        elections = Election.query.all();
        for election in elections:
            electionStartIso = datetime.datetime.strptime(election.start, "%Y-%m-%dT%H:%M:%S");
            electionEndIso = datetime.datetime.strptime(election.end, "%Y-%m-%dT%H:%M:%S");

            if((startIso > electionStartIso and startIso < electionEndIso)or (endIso > electionStartIso and endIso < electionEndIso)):
                return False;
        return True;

    except Exception:
        return False;

def isDatesValidWithTimeZone(start, end):
    #first string cast into iso8601, this may have exception
    try:
        startIso = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z");
        endIso = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z");

        if(startIso > endIso):
            return False;

        elections = Election.query.all();
        for election in elections:
            electionStartIso = datetime.datetime.strptime(election.start, "%Y-%m-%dT%H:%M:%S%z");
            electionEndIso = datetime.datetime.strptime(election.end, "%Y-%m-%dT%H:%M:%S%z");

            if((startIso > electionStartIso and startIso < electionEndIso)or (endIso > electionStartIso and endIso < electionEndIso)):
                return False;
        return True;

    except Exception:
        return False;


@application.route("/createElection", methods=["POST"])
@roleCheck(role = "admin")
def createElection():

    start = request.json.get("start", "");
    end = request.json.get("end", "");
    individual = request.json.get("individual", "");
    participants = request.json.get("participants", "");

    startEmpty = len(start) == 0;
    endEmpty = len(end) == 0;
    individualEmpty = (not isinstance(individual, bool));
    participantsEmpty = len(str (participants) ) == 0;

    if(startEmpty):
        return jsonify(message="Field start is missing."), 400

    if(endEmpty):
        return jsonify(message="Field end is missing."), 400

    if(individualEmpty):
        return jsonify(message="Field individual is missing."), 400

    if(participantsEmpty):
        return jsonify(message="Field participants is missing."), 400

    # na redu je preklapanje izbora

    if(not isDatesValidWithTimeZone(start=start, end=end) and not isDatesValidWithoutTimeZone(start=start, end=end)):
        return jsonify(message="Invalid date and time."), 400

    if(len(participants) < 2):
        return jsonify(message="Invalid participants."), 400

    for participantId in participants:
        if not isinstance(participantId, int):
            return jsonify(message="Invalid participants."), 400
        participant = Participant.query.filter(Participant.id == participantId).first();
        if((not participant) or (participant.individual != individual)):
            return jsonify(message="Invalid participants."), 400

    election = Election(start=start, end=end, individual=individual);
    database.session.add ( election );
    database.session.commit();

    pollNumber = 1;
    pollNumbers = [ ];

    for participantId in participants:
        electionParticipant = ElectionParticipant ( electionId= election.id, participantId=participantId, pollNumber=pollNumber);
        pollNumbers.append(pollNumber);
        pollNumber = pollNumber + 1;
        database.session.add ( electionParticipant );
        database.session.commit( );

    return jsonify(pollNumbers=pollNumbers), 200


@application.route("/getElections", methods=["GET"])
@roleCheck(role = "admin")
def getElections():

    allElections = Election.query.all();
    elections = [];
    for election in allElections:
        participants = [ ];
        for participant in election.participants:
            object = {
                "id" : participant.id,
                "name" : participant.name
            }
            participants.append(object);
        objectElection = {
            "id" : election.id,
            "start" : election.start,
            "end" : election.end,
            "individual" : election.individual,
            "participants" : participants
        }
        elections.append(objectElection);

    return jsonify(elections=elections), 200

def isElectionOngoingWithoutTimeZone(start, end):
    startIso = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S");
    endIso = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S");

    current = datetime.datetime.now().isoformat("T", "seconds");
    currentIso = datetime.datetime.strptime(current, "%Y-%m-%dT%H:%M:%S");

    if(currentIso > startIso and currentIso < endIso):
        return True;
    else:
        return False;

def isElectionOngoingWithTimeZone(start, end):
    startIso = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z");
    endIso = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z");

    current = datetime.datetime.now().isoformat("T", "seconds");
    currentIso = datetime.datetime.strptime(current, "%Y-%m-%dT%H:%M:%S%z");

    if(currentIso > startIso and currentIso < endIso):
        return True;
    else:
        return False;


@application.route("/getResults", methods=["GET"])
@roleCheck(role = "admin")
def getResults():

    id = request.args.get("id", "");

    idEmpty = len(id) == 0;

    if( idEmpty ):
        return  jsonify(message="Field id is missing."), 400

    election = Election.query.filter(Election.id == id).first();

    if(not election):
        return jsonify(message="Election does not exist."), 400

    if(isElectionOngoingWithoutTimeZone(start=election.start, end=election.end)
            or isDatesValidWithTimeZone(start=election.start, end=election.end)):
        return jsonify(message="Election is ongoing."), 400

    getcontext().prec = 2;

    if(election.individual): #predsednicki
        allValidVotes = Vote.query.filter(and_(Vote.idElection == election.id, Vote.reason.is_(None))).all();
        votesParticipants = { }; #dictionary for every separate participant
        sumVotes = 0;
        for vote in allValidVotes:
            sumVotes = sumVotes + 1;
            if vote.pollNumber in votesParticipants:
                votesParticipants[vote.pollNumber] = votesParticipants[vote.pollNumber] + 1;
            else:
                votesParticipants[vote.pollNumber] = 1;

        participants = [ ];
        for key, value in votesParticipants.items():
            participant = Participant.query.join(ElectionParticipant).filter(and_(
                ElectionParticipant.pollNumber == key, ElectionParticipant.electionId == election.id)).first();
            result = Decimal(value) / Decimal(sumVotes);
            object = {
                "pollNumber" : key,
                "name" : participant.name,
                "result" : float(result)
            }
            participants.append(object);

        allInvalidVotes = Vote.query.filter(and_(Vote.idElection == election.id, Vote.reason.isnot(None))).all();
        invalidVotes = [ ];
        for invalidVote in allInvalidVotes:
            object = {
                "electionOfficialJmbg" : invalidVote.electionOfficialJmbg,
                "ballotGuid" : invalidVote.ballotGuid,
                "pollNumber" : invalidVote.pollNumber,
                "reason" : invalidVote.reason
            }
            invalidVotes.append(object);

        return jsonify(participants=participants, invalidVotes=invalidVotes), 200

    else: #parlamentarni
        allValidVotes = Vote.query.filter(and_(Vote.idElection == election.id, Vote.reason.is_(None))).all();
        print(str(allValidVotes))
        votesParticipants = {};  # dictionary for every separate participant
        sumVotes = 0;
        for vote in allValidVotes:
            sumVotes = sumVotes + 1;
            if vote.pollNumber in votesParticipants:
                votesParticipants[vote.pollNumber] = votesParticipants[vote.pollNumber] + 1;
            else:
                votesParticipants[vote.pollNumber] = 1;

        class CalculatingResults :
            def __init__(self, pollNumber, voices, name, result, valid):
                self.pollNumber = pollNumber;
                self.voices = voices;
                self.name = name;
                self.result = result;
                self.valid = valid;

        calculateResult = [];
        #print('c')
        for key, value in votesParticipants.items():
            #print('b')
            if(value >= 0.05 * sumVotes):
                #print('a')
                participant = Participant.query.join(ElectionParticipant).filter(and_(
                    ElectionParticipant.pollNumber == key, ElectionParticipant.electionId == election.id)).first();
                calculateResult.append(CalculatingResults(key, value, participant.name, 0, True));
            else:
                participant = Participant.query.join(ElectionParticipant).filter(and_(
                    ElectionParticipant.pollNumber == key, ElectionParticipant.electionId == election.id)).first();
                calculateResult.append(CalculatingResults(key, value, participant.name, 0, False));


        for i in range(250):
            max = -1;
            index = -1;
            j = 0;
            for calcuResult in calculateResult:
                if(calcuResult.valid):
                    if ((calcuResult.voices / (calcuResult.result + 1)) > max):
                        max = calcuResult.voices / (calcuResult.result + 1);
                        index = j;
                j = j + 1;
            if(index != - 1) :
                calculateResult[index].result = calculateResult[index].result + 1;

        for tmp in calculateResult:
            print (tmp.pollNumber)
            print(tmp.voices)

        participants = [ ];
        for calcResult in calculateResult:
            object = {
                "pollNumber" : calcResult.pollNumber,
                "name" : calcResult.name,
                "result" : calcResult.result
            }
            participants.append(object);

        allInvalidVotes = Vote.query.filter(and_(Vote.idElection == election.id, Vote.reason.isnot(None))).all();
        invalidVotes = [];
        for invalidVote in allInvalidVotes:
            object = {
                "electionOfficialJmbg": invalidVote.electionOfficialJmbg,
                "ballotGuid": invalidVote.ballotGuid,
                "pollNumber": invalidVote.pollNumber,
                "reason": invalidVote.reason
            }
            invalidVotes.append(object);

        return jsonify(participants=participants, invalidVotes=invalidVotes), 200



if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5002 );