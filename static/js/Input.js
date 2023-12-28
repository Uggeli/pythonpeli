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
                    console.log(`Key ${event.key} pressed for ${direction} direction.`);
                    // Add your logic here for handling the key press
                }
            });
        });
    }
}

