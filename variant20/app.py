import bcrypt
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from marshmallow import ValidationError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sqlalchemy

from variant20.database import User, Advertisement, RoleEnum, Base
from variant20.schemas import UserSchema, AdvertisementSchema


def create_app(is_test=False):
    app = Flask(__name__)
    if not is_test:
        engine = create_engine(
            'mysql+pymysql://sqlalchemy:flaskpass@localhost/flask_app?charset=utf8mb4')
    else:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session: sqlalchemy.orm.session.Session = Session()

    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(email, password):
        user = session.query(User).filter(User.email == email).first()
        if user is not None and \
                bcrypt.checkpw(password.encode('utf8'),
                               user.password_hash.encode('utf8')):
            return user
        else:
            return "Unauthorized"

    @app.route('/advertisements', methods=['GET'])
    @auth.login_required
    def get_ads():
        user: object = auth.current_user()
        if user == "Unauthorized":
            ads = session.query(Advertisement).filter(
                Advertisement.modifier == "public").all()
        else:
            ads = session.query(Advertisement).all()
        return jsonify(AdvertisementSchema(many=True).dump(ads)), 200

    @app.route('/advertisements', methods=['POST'])
    @auth.login_required
    def create_ad():
        user = auth.current_user()
        if user == "Unauthorized":
            return "You do not have sufficient editing rights", 403
        ad_schema = AdvertisementSchema()
        data = request.get_json()
        data['user_id'] = auth.current_user().id
        try:
            ad = ad_schema.load(data)
        except ValidationError as err:
            return err.messages, 400
        session.add(ad)
        session.commit()
        return ad_schema.dump(ad), 201

    @app.route('/advertisements/<ad_topic>', methods=['GET'])
    @auth.login_required
    def get_ads_by_topic(ad_topic):
        ad_schema = AdvertisementSchema(only=['topic'])
        try:
            ad_schema.load({'topic': ad_topic})
        except ValidationError as err:
            return err.messages, 400
        user: object = auth.current_user()
        if user == "Unauthorized":
            ads = session.query(Advertisement).filter(
                Advertisement.modifier == "public",
                Advertisement.topic == ad_topic
            ).all()
        else:
            ads = session.query(Advertisement).filter(
                Advertisement.topic == ad_topic).all()
        return jsonify(AdvertisementSchema(many=True).dump(ads)), 200

    @app.route('/advertisements/<ad_topic>/<ad_id>', methods=['GET'])
    def get_ad(ad_topic, ad_id):
        ad_schema = AdvertisementSchema(only=['id', 'topic'])
        try:
            ad_schema.load({'id': ad_id, 'topic': ad_topic})
        except ValidationError as err:
            return err.messages, 400
        ad = session.query(Advertisement).filter(
            Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
        if ad is None:
            return 'Advertisement not found', 404
        app.logger.info(ad.modifier)
        return jsonify(AdvertisementSchema().dump(ad)), 200

    @app.route('/advertisements/<ad_topic>/<ad_id>', methods=['PUT'])
    @auth.login_required
    def edit_ad(ad_topic, ad_id):
        user = auth.current_user()
        if user == "Unauthorized":
            return "You do not have sufficient editing rights", 403
        ad_schema = AdvertisementSchema(only=['id', 'topic'])
        try:
            ad_schema.load({'id': ad_id, 'topic': ad_topic})
        except ValidationError as err:
            return err.messages, 400
        ad = session.query(Advertisement).filter(
            Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()

        if ad is None:
            return 'Advertisement not found', 404
        ad_schema = AdvertisementSchema()
        data = request.get_json()
        data['topic'] = ad_topic
        data['id'] = ad_id
        if auth.current_user().role == RoleEnum.master or \
                auth.current_user().id == ad.user_id == auth.current_user().id:
            try:
                ad_schema.load(data)
            except ValidationError as err:
                return err.messages, 400
            ad.summary = ad.summary if 'summary' not in data else data['summary']
            ad.description = ad.description if 'description' not in data else data[
                'description']
            ad.topic = ad.topic if 'topic' not in data else data['topic']
            ad.modifier = ad.modifier if 'modifier' not in data else data['modifier']
            ad.user_id = ad.user_id if 'user_id' not in data else data['user_id']
            session.commit()
            return ad_schema.dump(ad), 201
        return "You do not have sufficient editing rights", 403

    @app.route('/advertisements/<ad_topic>/<ad_id>', methods=['DELETE'])
    @auth.login_required
    def delete_ad(ad_topic, ad_id):
        user = auth.current_user()
        if user == "Unauthorized":
            return "You do not have sufficient editing rights", 403
        ad_schema = AdvertisementSchema(only=['id', 'topic'])
        try:
            ad_schema.load({'id': ad_id, 'topic': ad_topic})
        except ValidationError as err:
            return err.messages, 400
        ad = session.query(Advertisement).filter(
            Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
        if auth.current_user().role == RoleEnum.master or \
                auth.current_user().id == ad.user_id == auth.current_user().id:
            ad = session.query(Advertisement).filter(
                Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
            if ad is None:
                return 'Advertisement not found', 404
            session.delete(ad)
            session.commit()

            return "Advertisement deleted successfully", 200
        return "You do not have sufficient editing rights", 403

    @app.route('/users', methods=['GET'])
    def get_users():
        users = session.query(User).all()
        return jsonify(UserSchema(many=True).dump(users)), 200

    @app.route('/users', methods=['POST'])
    def create_user():
        user_schema = UserSchema()
        data = request.get_json()

        if not session.query(User).filter(User.email == data['email']).first() is None:
            return 'The email is already taken', 400
        try:
            user = user_schema.load({'name': data['name'], 'email': data['email'],
                                     'password_hash': bcrypt.hashpw(data['password_hash'].encode('utf8'),
                                                                    bcrypt.gensalt())})
            user.role = user.role if 'role' not in data else data['role']
        except ValidationError as err:
            return err.messages, 400
        session.add(user)
        session.commit()
        return user_schema.dump(user), 201

    @app.route('/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        user_schema = UserSchema(only=['id'])
        try:
            user_schema.load({'id': user_id})
        except ValidationError as err:
            return err.messages, 400
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            return 'User not found', 404
        return jsonify(UserSchema().dump(user)), 200

    return app
