from flask import Flask, request, jsonify
from marshmallow import ValidationError
from variant20.schemas import UserSchema, AdvertisementSchema
from variant20.database import Session, User, Advertisement, ModifierEnum
import bcrypt


app = Flask(__name__)
session = Session()


@app.route('/advertisements', methods=['GET'])
def get_ads():
    ads = session.query(Advertisement).all()
    return jsonify(AdvertisementSchema(many=True).dump(ads)), 200


@app.route('/advertisements', methods=['POST'])
def create_ad():
    ad_schema = AdvertisementSchema()
    data = request.get_json()
    try:
        ad = ad_schema.load(data)
    except ValidationError as err:
        return err.messages, 400
    session.add(ad)
    session.commit()
    return ad_schema.dump(ad), 201


@app.route('/advertisements/<ad_topic>', methods=['GET'])
def get_ads_by_topic(ad_topic):
    ad_schema = AdvertisementSchema(only=['topic'])
    try:
        ad_schema.load({'topic': ad_topic})
    except ValidationError as err:
        return err.messages, 400
    ads = session.query(Advertisement).filter_by(topic=ad_topic).all()
    return jsonify(AdvertisementSchema(many=True).dump(ads)), 200


@app.route('/advertisements/<ad_topic>/<ad_id>', methods=['GET'])
def get_ad(ad_topic, ad_id):
    ad_schema = AdvertisementSchema(only=['id', 'topic'])
    try:
        ad_schema.load({'id': ad_id, 'topic': ad_topic})
    except ValidationError as err:
        return err.messages, 400
    ad = session.query(Advertisement).filter(Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
    if ad is None:
        return 'Advertisement not found', 404
    return jsonify(AdvertisementSchema().dump(ad)), 200


@app.route('/advertisements/<ad_topic>/<ad_id>', methods=['PUT'])
def edit_ad(ad_topic, ad_id):
    ad_schema = AdvertisementSchema(only=['id', 'topic'])
    try:
        ad_schema.load({'id': ad_id, 'topic': ad_topic})
    except ValidationError as err:
        return err.messages, 400
    ad = session.query(Advertisement).filter(Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
    if ad is None:
        return 'Advertisement not found', 404
    ad_schema = AdvertisementSchema()
    data = request.get_json()
    try:
        ad_schema.load(data)
    except ValidationError as err:
        return err.messages, 400
    ad.summary = data['summary']
    ad.description = data['description']
    ad.topic = data['topic']
    ad.modifier = data['modifier']
    ad.user_id = data['user_id']
    session.commit()
    return ad_schema.dump(ad), 201


@app.route('/advertisements/<ad_topic>/<ad_id>', methods=['DELETE'])
def delete_ad(ad_topic, ad_id):
    ad_schema = AdvertisementSchema(only=['id', 'topic'])
    try:
        ad_schema.load({'id': ad_id, 'topic': ad_topic})
    except ValidationError as err:
        return err.messages, 400
    ad = session.query(Advertisement).filter(Advertisement.id == ad_id, Advertisement.topic == ad_topic).first()
    if ad is None:
        return 'Advertisement not found', 404
    session.delete(ad)
    session.commit()
    return "Advertisement deleted successfully"


@app.route('/users', methods=['GET'])
def get_users():
    users = session.query(User).all()
    return jsonify(UserSchema(many=True).dump(users)), 200


@app.route('/users', methods=['POST'])
def create_user():
    user_schema = UserSchema()
    data = request.get_json()
    if not session.query(User).filter(User.name == data['name']).first() is None:
        return 'The name is already taken', 400
    if not session.query(User).filter(User.email == data['email']).first() is None:
        return 'The email is already taken', 400
    try:
        user = user_schema.load({'name': data['name'], 'email': data['email'],
                                 'password_hash':bcrypt.hashpw(data['password_hash'].encode('utf8'), bcrypt.gensalt())})
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


@app.route('/sign-in', methods=['GET'])
def sign_in():
    email = request.args.get('email')
    password = request.args.get('password')

    user = session.query(User).filter(User.email == email).first()
    if user is None:
        return "Email not found", 400

    if not bcrypt.checkpw(password.encode('utf8'), user.password_hash.encode('utf8')):
        return "Wrong password", 400

    return jsonify(UserSchema().dump(user)), 200


@app.route('/logout', methods=['GET'])
def logout():
    return 'Logout'


if __name__ == '__main__':
    app.run()