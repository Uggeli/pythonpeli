let gameState = null; // The current game state
const renderer = new Renderer();
const connection = new Connection(renderer);
const inputManager = new InputManager();

inputManager.listen();
renderer.setup();
connection.setup();

