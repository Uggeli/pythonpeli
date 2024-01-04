class TextureManager {
    constructor() {
        this.Textures = {};
        this.IsTextureRequestPending = false;
    }

    addTexture(texture) {
        if (this.Textures[texture.name]) {
            return;
        }
        this.Textures[texture.name] = texture;
    }

    getTexture(name) {
        console.log(`Getting texture ${name}`)
        if (!this.Textures[name]) {
            return null;
        }
        return this.Textures[name];
    }

    requestTextures(names) {
        if (this.IsTextureRequestPending) {
            return;
        }
        this.IsTextureRequestPending = true;
        connection.socket.emit('requestTexture', names);
    }

    handleTextureResponse(response) {
        response = JSON.parse(response);
        if (!response) return;
        response.forEach(element => {
            let texture_name = element.name;
            let texture = new Image();
            texture.src = 'data:image/png;base64,' + element.data; // Ensure correct data URL format
            texture.onload = () => {
                this.addTexture({ name: texture_name, texture: texture });
            };
            texture.onerror = () => {
                console.error(`Failed to load texture: ${texture_name}`);
            };
        });
        this.IsTextureRequestPending = false;
    }
}
