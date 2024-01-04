// game.js

let gameState = null; // The current game state
const renderer = new Renderer();
const connection = new Connection();
const inputManager = new InputManager();
const textureManager = new TextureManager();

inputManager.listen();
renderer.setup();
connection.connect();

