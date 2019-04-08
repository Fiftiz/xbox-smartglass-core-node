var SimplePacket = require('./simple');
var MessagePacket = require('./messagePack');

module.exports = function(type)
{
    var Types = {
        d00d: 'message',
        cc00: 'simple.connect_request',
        cc01: 'simple.connect_response',
        dd00: 'simple.discovery_request',
        dd01: 'simple.discovery_response',
        dd02: 'simple.poweron',
    }

    var loadPacketStructure = function(type, value = false){
        if(type.slice(0, 6) == 'simple'){
            return SimplePacket(type.slice(7), value);
        } else if(type.slice(0, 7) == 'message'){
            return MessagePacket(type.slice(8), value);
        } else {
            throw new Error('[packet/packer.js] Packet format not found: '+type.toString('hex'));
        }
    }

    // Load packet
    var packet_type = type.slice(0,2).toString('hex')
    if(packet_type in Types){
        // We got a packet that we need to unpack
        var packet_value = type;
        type = Types[packet_type];
        var structure = loadPacketStructure(type, packet_value)
    } else {
        var structure = loadPacketStructure(type)
    }

    return {
        type: type,
        structure: structure,
        set: function(key, value){
            this.structure.set(key, value)
        },
        pack: function(device = undefined){
            return structure.pack(device)
        },
        unpack: function(device = undefined){
            return structure.unpack(device)
        }
    }
}