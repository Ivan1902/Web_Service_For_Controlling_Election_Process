from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy();

class ElectionParticipant( database.Model ):
    __tablename__ = "electionparticipants";

    id = database.Column ( database.Integer, primary_key= True);
    electionId = database.Column( database.Integer, database.ForeignKey("elections.id"), nullable=False);
    participantId = database.Column (database.Integer, database.ForeignKey("participants.id"), nullable=False);

    pollNumber = database.Column(database.Integer, nullable=False);

class Participant ( database.Model ):
    __tablename__ = "participants";

    id = database.Column( database.Integer, primary_key=True);
    name = database.Column ( database.String( 256 ), nullable=False);
    individual = database.Column ( database.Boolean, nullable=False);
    elections = database.relationship('Election', secondary=ElectionParticipant.__table__, back_populates='participants')

class Election ( database.Model ):
    __tablename__ = "elections";

    id = database.Column ( database.Integer, primary_key=True);
    start = database.Column (database.String(256), nullable=False);
    end = database.Column (database.String(256), nullable=False);
    individual = database.Column( database.Boolean, nullable=False);
    participants = database.relationship("Participant", secondary= ElectionParticipant.__table__, back_populates= "elections");


class Vote ( database.Model ):
    __tablename__ = "votes";

    id = database.Column( database.Integer, primary_key=True);
    ballotGuid = database.Column (database.String(256), nullable=False);
    pollNumber = database.Column(database.Integer, nullable=False);
    electionOfficialJmbg = database.Column(database.String(256), nullable=False);
    idElection = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False);
    reason = database.Column(database.String(256), nullable=True);