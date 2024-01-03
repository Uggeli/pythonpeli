// Renderer.js
class Renderer {
    Textures = {}

    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.cellSize = 30; // Set cell size
    }

    setup() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'GameCanvas';
        this.canvas.width = 300; // Example size
        this.canvas.height = 300;
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
    }

    addTexture(texture) {
        if (this.Textures[texture.name]) {
            return;
        }
        this.Textures[texture.name] = texture;
    }

    getTexture(name) {
        return this.Textures[name];
    }

    renderMap(gameState) {
        if (!gameState || !gameState.tiles) {
            return;
        }
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        // Render each cell of the map
        for (let y = 0; y < gameState.tiles.length; y++) {
            for (let x = 0; x < gameState.tiles[y].length; x++) {
                const cell = gameState.tiles[y][x];
                const texture = this.getTexture(cell);
                if (!texture) {
                    connection.handleRequestTexture(cell);
                }
                else {
                    this.ctx.drawImage(texture, x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
                }
            }
        }
    }
}