# Example config:
{
    'textures': {
        'texture': {
            'path': 'path/to/texture.png',
            'type': 'texture',
            'format': 'png',
            'h_texture': 64,
            'v_texture': 64,
        },
        'spritesheet': {
            'path': 'path/to/texture.png',
            'type': 'spritesheet',
            'format': 'png',
            'h_texture': 64,
            'v_texture': 64,
            'h_spritesheet': 8,
            'v_spritesheet': 8,
            'sprites': [],  # list of tuples (x, y), optional
            'sprite_names': [],  # list of names, optional
            'sprite_num': 64  # number of sprites, required
        },
        'animation': {
            'path': 'path/to/texture.png',
            'type': 'animation',
            'format': 'png',
            'h_texture': 64,
            'v_texture': 64,
            'h_animation': 8,
        },

    }
}