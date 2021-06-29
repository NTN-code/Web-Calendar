from flask import Flask, abort
import sys

app = Flask(__name__)

# write your code here
from flask_restful import Api, Resource, reqparse, fields, marshal_with, inputs
from flask_sqlalchemy import SQLAlchemy, request
import datetime

api = Api(app)
parser = reqparse.RequestParser()
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


class Event(db.Model):
    __tablename__ = "Event"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()

parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)

resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.DateTime(dt_format='iso8601')
}


class GetEventsToday(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return Event.query.filter(Event.date == datetime.date.today()).all()


class GetEvents(Resource):
    @marshal_with(resource_fields)
    def get(self):
        try:
            start_time = datetime.datetime.strptime(request.args["start_time"], '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(request.args["end_time"], '%Y-%m-%d').date()
            events = Event.query.filter(start_time <= Event.date).filter(Event.date <= end_time).all()
            return events
        except:
            return Event.query.all()

    def post(self):
        args = parser.parse_args()
        if not args['date']:
            response = {'message': {
                "date": args['date']
            }
            }
            return response
        elif not args['event']:
            response = {'message': {
                "event": args['event']
            }
            }
            return response
        args['date'] = str(args['date'].date())
        args['message'] = 'The event has been added!'

        buff_date = datetime.datetime.strptime(args['date'], "%Y-%m-%d")
        event = Event(event=args['event'], date=buff_date)
        db.session.add(event)
        db.session.commit()
        return args


class GetEventID(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        event = Event.query.filter(Event.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            return event

    def delete(self, id):
        event = Event.query.filter(Event.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            Event.query.filter_by(id=id).delete()
            db.session.commit()
            return {"message":  "The event has been deleted!"}


api.add_resource(GetEventsToday, '/event/today')
api.add_resource(GetEvents, '/event')
api.add_resource(GetEventID, '/event/<int:id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
