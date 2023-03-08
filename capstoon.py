from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
db = SQLAlchemy(app)

# the Model from here 

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    devices = db.relationship('Device', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.id}: {self.name}>"


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    device_state = db.Column(db.String(200))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    def __repr__(self):
        return f"<Device {self.id}: {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'device_state': self.device_state,
            'room_id': self.room_id
        }
        
# the controller from here 
@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices])


@app.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get(device_id)
    if device:
        return jsonify(device.to_dict())
    else:
        return jsonify({'error': 'Device not found'})


@app.route('/devices', methods=['POST'])
def create_device():
    data = request.get_json()
    name = data.get('name')
    device_state = data.get('device_state')
    room_id = data.get('room_id')

    if not all([name, device_state]):
        return jsonify({'error': 'Invalid input'})

    device = Device(name=name, device_state=device_state, room_id=room_id)
    db.session.add(device)
    db.session.commit()
    return jsonify(device.to_dict())


@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get(device_id)
    if device:
        data = request.get_json()
        name = data.get('name')
        device_state = data.get('device_state')
        room_id = data.get('room_id')

        if not all([name, device_state]):
            return jsonify({'error': 'Invalid input'})

        device.name = name
        device.device_state = device_state
        device.room_id = room_id
        db.session.commit()
        return jsonify(device.to_dict())
    else:
        return jsonify({'error': 'Device not found'})


@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': f'Device {device_id} deleted successfully'})
    else:
        return jsonify({'error': 'Device not found'})


@app.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    name = data.get('name')
    device_name = data.get('device_name')
    device_state = data.get('device_state')

    if not all([name, device_name, device_state]):
        return jsonify({'error': 'Invalid input'})

    room = Room.query.filter_by(name=name).first()
    if not room:
        room = Room(name=name)
        db.session.add(room)
        db.session.commit()

    device = Device(name=device_name, device_state=device_state, room_id=room.id)
    
    # Controller for deleting a room
@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get(room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
        return jsonify({'message': f'Room {room_id} deleted successfully'})
    else:
        return jsonify({'error': 'Room not found'})

# Controller for updating a room
@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.query.get(room_id)
    if room:
        data = request.get_json()
        room.name = data['name']
        db.session.commit()
        return jsonify({'id': room.id, 'name': room.name})
    else:
        return jsonify({'error': 'Room not found'})
    
    # Controller for updating a device's room
@app.route('/devices/<int:device_id>/room', methods=['PUT'])
def update_device_room(device_id):
    device = Device.query.get(device_id)
    if device:
        data = request.get_json()
        room_name = data['room_name']

        room = Room.query.filter_by(name=room_name).first()
        if not room:
            room = Room(name=room_name)
            db.session.add(room)
            db.session.commit()

        device.room = room
        db.session.commit()

        return jsonify({'id': device.id, 'name': device.name, 'Device_State': device.Device_State, 'room': {'id': room.id, 'name': room.name}})
    else:
        return jsonify({'error': 'Device not found'})