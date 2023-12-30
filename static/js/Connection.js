class Connection {
    constructor(renderer) {
        this.renderer = renderer;
        this.socket = null;
        this.connected = false;
    }

    setup() {
        this.socket = io();
        this.socket.on('connect', this.handleConnect.bind(this));
        this.socket.on('disconnect', this.handleDisconnect.bind(this));
        this.socket.on('authenticated', this.handleAuthentication.bind(this));
        this.socket.on('unauthorized', this.handleUnauthorized.bind(this));
        this.socket.on('players', this.handlePlayers.bind(this));
        this.socket.on('gameStateUpdate', this.handleGameStateUpdate.bind(this));
    }

    connect(username, password) {
        this.socket.emit('authentication', { username: username, password: password });
    }

    handleConnect() {
        console.log('Connected to server');
        this.updateConnectionStatus('Connected');
    }

    handleDisconnect() {
        console.log('Disconnected from server');
        this.updateConnectionStatus('Disconnected');
    }

    handleAuthentication(response) {
        if (response.status === "success") {
            console.log('Authenticated successfully');
            document.getElementById('login').style.display = 'none'; // Hide login form
            this.connected = true;
        } else {
            alert('Authentication failed');
        }
    }

    handleUnauthorized(msg) {
        console.log('Unauthorized:', msg.message);
        alert('Authentication failed: ' + msg.message);
    }

    handlePlayers(players) {
        console.log(players);
        var playersDiv = document.getElementById('players');
        playersDiv.innerHTML = '';
        for (var i = 0; i < players.length; i++) {
            var player = players[i];
            var playerDiv = document.createElement('div');
            playerDiv.innerHTML = player.name;
            playersDiv.appendChild(playerDiv);
        }
    }

    handleGameStateUpdate(newState) {
        // Parsing the JSON string into an object
        try {
            const parsedState = JSON.parse(newState);
            gameState = parsedState;
            this.renderer.renderMap(gameState);
        } catch (e) {
            console.error("Error parsing gameState:", e);
        }
    }

    handleAction(action) {
        if (this.connected) {
            this.socket.emit('action', action);
        }
    }

    updateConnectionStatus(status) {
        var connectionStatusDiv = document.getElementById('connectionStatus');
        connectionStatusDiv.innerHTML = status;
    }
}