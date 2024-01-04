class Connection {
    constructor(renderer) {
        this.renderer = renderer;
        this.socket = null;
        this.connected = false;
        this.updateConnectionStatus('Disconnected');
    }

    connect() {
        this.socket = io();
        this.socket.on('connect', this.handleConnect.bind(this));
        this.socket.on('disconnect', this.handleDisconnect.bind(this));
        this.socket.on('authenticated', this.handleAuthenticationResponse.bind(this));
        this.socket.on('unauthorized', this.handleUnauthorized.bind(this));
        this.socket.on('players', this.handlePlayers.bind(this));
        this.socket.on('gameStateUpdate', this.handleGameStateUpdate.bind(this));
        this.socket.on('action', this.handleAction.bind(this));
        this.socket.on('textureResponse', textureManager.handleTextureResponse.bind(textureManager));
    }

    disconnect() {
        this.socket.disconnect();
        this.socket = null;
    }

    AuthUser(username, password) {
        if (!this.socket) {
            this.connect();
        }
        this.socket.emit('authentication', { username: username, password: password });
        this.updateConnectionStatus('Authenticating...');
    }

    handleConnect() {
        console.log('Connected to server');
        this.connected = true;
        this.updateConnectionStatus('Connected');
    }

    handleDisconnect() {
        console.log('Disconnected from server');
        this.updateConnectionStatus('Disconnected');
    }

    updateConnectionStatus(status) {
        const statusDiv = document.getElementById('connectionStatus');
        if (this.connected) {
            let disconnect_button = document.createElement('button');
            disconnect_button.innerHTML = 'Disconnect';
            disconnect_button.onclick = this.disconnect.bind(this);
        }
        else {
            let connect_button = document.createElement('button');
            connect_button.innerHTML = 'Connect';
            connect_button.onclick = this.connect.bind(this);
        }
        statusDiv.innerHTML = status;
    }

    handleAuthenticationResponse(response) {
        if (response.status === "success") {
            console.log('Authenticated successfully');
            document.getElementById('login').style.display = 'none'; // Hide login form
            this.connected = true;
        } else {
            alert('Authentication failed');
        }
        this.updateConnectionStatus('Authenticated');
    }

    handleUnauthorized(msg) {
        try {
            msg = JSON.parse(msg);
        }
        catch (e) {
            console.log('Unauthorized:', msg.status);
            flash('Authentication failed: ' + msg.status);
            // reset the connection
            this.socket.disconnect();
            document.getElementById('login').style.display = 'block'; // Show login form
        }
        console.log('Unauthorized:', msg.status);
        flash('Authentication failed: ' + msg.status);
        // reset the connection
        this.socket.disconnect();
        document.getElementById('login').style.display = 'block'; // Show login form
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
            renderer.renderMap(gameState);
        } catch (e) {
            console.error("Error parsing gameState:", e);
        }
    }

    handleAction(action) {
        if (this.connected) {
            this.socket.emit('action', action);
        }
    }
}