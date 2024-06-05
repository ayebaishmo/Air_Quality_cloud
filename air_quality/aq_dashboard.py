from flask import Flask, jsonify
from air_quality import openaq
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

def create_app():
    app = Flask(__name__)

    api = openaq.OpenAQ()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB = SQLAlchemy(app)

    class Record(DB.Model):
        id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
        date_and_time = DB.Column(DB.DateTime)
        value = DB.Column(DB.Float, nullable=False)

        def __repr__(self):
            return f"<Record id={self.id}, datetime={self.date_and_time}, value={self.value}>"

    @app.route('/')
    def root():
        """Base view"""
        records = Record.query.all()
        records_list = [
            {
                'id': record.id,
                'date_and_time': record.date_and_time.strftime('%Y-%m-%d %H:%M:%S'),
                'value': record.value
            }
            for record in records
        ]
        return jsonify(records_list)

    @app.route('/refresh')
    def refresh():
        inspector = DB.inspect(DB.engine)
        if inspector.has_table('record'):
            # Drop the table if it exists to ensure schema correctness
            DB.drop_all()
        DB.create_all()

        status, body = api.measurements(city='Los Angeles')
        results = body['results'][:1]

        for result in results:
            datetime_str = result['date']['utc']
            date_and_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            value = result['value']

            record = Record(date_and_time=date_and_time, value=value)
            DB.session.add(record)

        DB.session.commit()
        return "Database created, table created, and data inserted"

    return app
