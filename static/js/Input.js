class InputManager {
    constructor() {
        this.keys = {
            up: ["ArrowUp", "w"],
            down: ["ArrowDown", "s"],
            left: ["ArrowLeft", "a"],
            right: ["ArrowRight", "d"]
        };
    }

    listen() {
        document.addEventListener("keydown", (event) => {
            Object.keys(this.keys).forEach((direction) => {
                if (this.keys[direction].includes(event.key)) {
                    switch (direction) {
                        case "up":
                            this.movePlayer("up");
                            break;
                        case "down":
                            this.movePlayer("down");
                            break;
                        case "left":
                            this.movePlayer("left");
                            break;
                        case "right":
                            this.movePlayer("right");
                            break;
                    }
                }
            });
        });
    }
    
    // action; required fields:
    // - action: string
    // - target: string
    // - data: object (required but can be empty)
    movePlayer(direction) {
        if (connection.connected) {
            connection.socket.emit('action', { action: 'move', target: direction, data: {} });
        }
    }


}


