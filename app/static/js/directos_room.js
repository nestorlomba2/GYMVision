console.log('In main.js!');

var mapPeers = {};       //keep track of peers and their data channels

var chatPage = document.querySelector(".js-chat"); // The chatroom page
var toolbar = document.querySelector(".js-toolbar");

// var username;
// var roomName;
// var userType;

var broadcaster;

var websocket;

function webSocketOnMessage(event) {         //este web socket es solo para la info de señalización
    var parsedData = JSON.parse(event.data);
    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];
    var peerBroadcaster = parsedData['message']['broadcaster'];

    // ignore our own messages
    if (username == peerUsername) {
        return;
    }

    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if (action == 'new-peer') {
        console.log('received new-peer');
        createOfferer(peerUsername, receiver_channel_name, peerBroadcaster);
        return;
    }

    if (action == 'new-offer') {
        var offer = parsedData['message']['sdp'];
        createAnswerer(offer, peerUsername, receiver_channel_name, peerBroadcaster);
        return;
    }

    if (action == 'new-answer') {
        var answer = parsedData['message']['sdp'];
        var peer = mapPeers[peerUsername][0];
        peer.setRemoteDescription(answer);
    }
}

const constraints = {
    'video': true,
    'audio': true
};

window.onload = function () {    //sets username and creates websocket
    // var urlParams = new URLSearchParams(window.location.search);
    // username = urlParams.get('username');
    // var trainer = urlParams.get('trainer');
    // roomName = 'room1';
    if (userType == 'cliente') broadcaster = false;
    else broadcaster = true;

    console.log('username: ', username);
    console.log('room name: ', roomName);
    console.log('is trainer: ', broadcaster);

    if (username == '' || roomName == '') {
        return;
    }

    //wesocket connection and listeners
    var loc = window.location;
    var wsStart = 'ws://';

    if (loc.protocol == 'https:') {
        wsStart = 'wss://';
    }

    var websocketURL = '/directos/ws/chat/' + roomName + '/';

    var endPoint = wsStart + loc.host + websocketURL;

    console.log('endPoint: ', endPoint);

    websocket = new WebSocket(endPoint);

    websocket.addEventListener('open', (e) => {
        console.log('Connection Opened!');

        sendSignal('new-peer', {
            'broadcaster': broadcaster
        }); // on connection WebRTC ---- enviamos el mensaje join ¿¿¿¿¿¿¿¿¿¿PARAMETRO BROADCASTER????????????
    });
    websocket.addEventListener('message', webSocketOnMessage);
    websocket.addEventListener('close', (e) => {
        console.log('Connection Closed!');
    });
    websocket.addEventListener('error', (e) => {
        console.log('Error Occured!');
    });

    if (broadcaster) getMedia();
}

var localStream = new MediaStream();

let btnToggleAudio = document.querySelector('#btn-toggle-audio');
let btnToggleVideo = document.querySelector('#btn-toggle-video');

var userMedia;

function getMedia() {
    userMedia = navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            console.log(constraints);
            localStream = stream;

            var localVideo = createVideo(username);
            localVideo.srcObject = localStream;
            localVideo.muted = true;

            //mute and video off functionalities
            var audioTracks = stream.getAudioTracks();
            var videoTracks = stream.getVideoTracks();

            audioTracks[0].enabled = true;
            videoTracks[0].enabled = true;

            btnToggleAudio.style.visibility = 'visible';
            btnToggleAudio.disabled = false;
            btnToggleVideo.style.visibility = 'visible';
            btnToggleVideo.disabled = false;

            btnToggleAudio.addEventListener('click', () => {
                audioTracks[0].enabled = !audioTracks[0].enabled;
                if (audioTracks[0].enabled) {
                    btnToggleAudio.classList.remove('disable-btn');
                    btnToggleAudio.classList.add('enable-btn');
                    return;
                }
                btnToggleAudio.classList.remove('enable-btn');
                btnToggleAudio.classList.add('disable-btn');
            });

            btnToggleVideo.addEventListener('click', () => {
                videoTracks[0].enabled = !videoTracks[0].enabled;
                if (videoTracks[0].enabled) {
                    btnToggleVideo.classList.remove('disable-btn');
                    btnToggleVideo.classList.add('enable-btn');
                    return;
                }
                btnToggleVideo.classList.remove('enable-btn');
                btnToggleVideo.classList.add('disable-btn');
            });
        })
        .catch(error => {
            console.log('Error accessing media devices: ' + error);
        });
}

window.onunload = function() {
    alert("Hola");          //PROBAR SI FUNCIONA
}


//chat functionality
var messageList = document.querySelector('#message-list');
var messageInput = document.querySelector('#msg');

window.onkeydown = function (event) {
    if (event.which == 13) {
        sendMsgOnClick();
    }
}

function sendMsgOnClick() {
    var message = messageInput.value;

    if (message == '') return;

    var peerUsername = 'Yo';

    var usernameDiv = document.createElement('span');
    usernameDiv.classList.add('my-username');
    usernameDiv.innerHTML = peerUsername;
    var messageBodyDiv = document.createElement('span');
    messageBodyDiv.classList.add('messageBody');
    messageBodyDiv.innerHTML = message;

    var li = document.createElement('li');
    li.classList.add('my-message');
    li.appendChild(messageBodyDiv);
    li.appendChild(usernameDiv);
    messageList.appendChild(li);

    messageList.scrollTop = messageList.scrollHeight;

    var dataChannels = getDataChannels();

    message = username + ':' + message;

    for (index in dataChannels) {
        dataChannels[index].send(message);
    }

    messageInput.value = '';
}


function sendSignal(action, message) {
    //signaling
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action, //new-peer, new-offer, new-answer
        'message': message,
    })

    websocket.send(jsonStr);
}

function createOfferer(peerUsername, receiver_channel_name, peerBroadcaster) {
    var peer = new RTCPeerConnection(null); //solo va a funcionar si ambos dispositivos están en la misma red
    // para distintas redes, necesitamos turn servers y stun servers y especificarlo en un diccionario como parámetro en este constructor
    if (broadcaster) addLocalTracks(peer);

    var dc = peer.createDataChannel('channel'); //data channel
    dc.addEventListener('open', () => {
        console.log('Connection opened!');
    });
    dc.addEventListener('message', dcOnMessage); // when receiving a chat message

    var remoteVideo

    if (peerBroadcaster) {
        remoteVideo = createVideo(peerUsername); //creamos en html el elemento video para el nuevo peer
        setOnTrack(peer, remoteVideo);
    }

    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState

        if (iceConnectionState == 'failed' || iceConnectionState == 'disconnected' || iceConnectionState == 'closed') {
            if (iceConnectionState != 'closed') {
                console.log("peer disconnected");
                peer.close();
            }

            if (peerBroadcaster) removeVideo(remoteVideo); //si algun entrenador se desconecta tenemos que eliminar la visualización de su vídeo
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            //console.log('New ice candidate: ', JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-offer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name,
            'broadcaster': broadcaster
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('Local description set succesfully.');
        });
}

function createAnswerer(offer, peerUsername, receiver_channel_name, peerBroadcaster) {
    var peer = new RTCPeerConnection(null); //solo va a funcionar si ambos dispositivos están en la misma red
    // para distintas redes, necesitamos turn servers y stun servers y especificarlo en un diccionario como parámetro en este constructor
    if (broadcaster) addLocalTracks(peer);

    var remoteVideo;

    if (peerBroadcaster) { //creamos el video y lo mostramos si el nuevo peer es entrenador
        remoteVideo = createVideo(peerUsername); //creamos en html el elemento video para el nuevo peer
        setOnTrack(peer, remoteVideo);
    }

    peer.addEventListener('datachannel', e => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {          //abrimos el canal en el otro usuario tbn
            console.log('Connection opened!');
        });
        peer.dc.addEventListener('message', dcOnMessage);

        mapPeers[peerUsername] = [peer, peer.dc];       // guardamos la asociación
    });

    mapPeers[peerUsername] = [peer, peer.dc];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState

        if (iceConnectionState == 'failed' || iceConnectionState == 'disconnected' || iceConnectionState == 'closed') {
            if (iceConnectionState != 'closed') {
                console.log("peer disconnected");
                peer.close();
            }

            if (peerBroadcaster) removeVideo(remoteVideo); //si algún entrenador se desconecta tenemos que eliminar la visualización de su vídeo
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            //console.log('New ice candidate: ', JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name,
            'broadcaster': broadcaster
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Remote description set succesfully for %s.', peerUsername);

            return peer.createAnswer();
        })
        .then(a => {
            console.log('Answer created!');

            peer.setLocalDescription(a);
        })
}

function addLocalTracks(peer) {      //enviamos nuestro video

    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
        console.log('Sending track');
    });
    return;
}

function dcOnMessage(event) { //datos del chat de texto
    var data = event.data;

    var peerUsername = data.split(':')[0];
    var message = data.split(':')[1];

    var usernameDiv = document.createElement('span');
    usernameDiv.classList.add('username');
    usernameDiv.innerHTML = peerUsername;
    var messageBodyDiv = document.createElement('span');
    messageBodyDiv.classList.add('messageBody');
    messageBodyDiv.innerHTML = message;

    var li = document.createElement('li');
    li.classList.add('message');
    li.appendChild(usernameDiv);
    li.appendChild(messageBodyDiv);
    messageList.appendChild(li);

    messageList.scrollTop = messageList.scrollHeight;
}

function createVideo(peerUsername) {
    var videoContainer = document.querySelector('#video-container');
    var spinner = document.querySelector('.spinner');

    if (spinner != null) videoContainer.removeChild(spinner);

    var remoteVideo = document.createElement('video');
    remoteVideo.classList.add('video-js');
    remoteVideo.classList.add('vjs-default-skin');

    remoteVideo.id = peerUsername + '-video';
    remoteVideo.controls = true;
    remoteVideo.preload = 'auto';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    videoContainer.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo) {     //pasamos el video recibido a nuestro html
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
        console.log('New Track');
    });
}

function removeVideo(video) {
    var videoContainer = video.parentNode;

    videoContainer.removeChild(video);
}

function getDataChannels() {
    var dataChannels = [];

    for (peerUsername in mapPeers) {
        var dataChannel = mapPeers[peerUsername][1];
        if(dataChannel.readyState == 'open') dataChannels.push(dataChannel);
    }

    return dataChannels;
}

//Detalles interfaz
var body = document.body;
var btnToggleChat = document.querySelector('.js-toggle-chat');

btnToggleChat.addEventListener('click', () => {
    if (body.classList.contains('show-chat'))
        body.classList.remove('show-chat');
    else
        body.classList.add('show-chat');

    if (btnToggleChat.classList.contains('enable-btn')) {
        btnToggleChat.classList.remove('enable-btn');
        btnToggleChat.classList.add('disable-btn');
    } else if (btnToggleChat.classList.contains('disable-btn')) {
        btnToggleChat.classList.remove('disable-btn');
        btnToggleChat.classList.add('enable-btn');
    }
})