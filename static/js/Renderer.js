// Renderer.js
class Renderer {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.cellSize = 30; // Set cell size
    }

    setup() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'GameCanvas';
        this.canvas.width = 800; 
        this.canvas.height = 800;
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
    }

    renderMap(gameState) {
        if (!gameState || !gameState.tiles) {
            return;
        }
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        // Render each cell of the map
        let missingTextures = [];
        for (let y = 0; y < gameState.tiles.length; y++) {
            for (let x = 0; x < gameState.tiles[y].length; x++) {
                const cell = gameState.tiles[y][x];
                const textureObj = textureManager.getTexture(cell);
                console.log(textureManager)
                console.log(textureObj)
                if (!textureObj) {
                    if (!missingTextures.includes(cell)) {
                        missingTextures.push(cell);
                    }
                    continue;
                } else {
                    this.ctx.drawImage(textureObj.texture, x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
                }
            }
        }
        if (missingTextures.length > 0) {
            console.warn(`Missing textures: ${missingTextures.join(', ')}`);
            textureManager.requestTextures(missingTextures);
        }
    }
}