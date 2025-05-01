import pubsub.pub
from panda3d.core import CollisionBox, CollisionNode, Vec4
from pubsub import pub


class ViewObject:
    def __init__(self, game_object):
        self.game_object = game_object
        self.model = None  # Initialize model attribute

        if game_object.kind == "wall":
            self.model = base.loader.loadModel("Models/cube1")
            self.model.setColor(Vec4(0.8, 0.6, 0.4, 1))  # Brown
            self.model.setLightOff(True)  # Disable lighting
            self.model.setScale(*game_object.size)
        elif game_object.kind == "floor":
            self.model = base.loader.loadModel("Models/cube1")
            self.model.setTexture(base.loader.loadTexture("Textures/maps/crate.png"))
            self.model.setScale(*game_object.size)
        elif game_object.kind == "collectible":
            self.model = base.loader.loadModel("Models/Icosahedron")
            self.model.setColor(Vec4(1, 1, 0, 1))
            self.model.setLightOff(True)  # Disable lighting
        elif game_object.kind == "player":
            self.model = base.loader.loadModel("Models/Icosahedron")
            self.model.setColor(Vec4(0, 0.5, 1, 1))  # Blue
            self.model.setLightOff(True)
            self.model.setScale(0.5, 0.5, 0.5)
        else:  # Default cube
            self.model = base.loader.loadModel("Models/Cube")
            self.model.setColor(Vec4(0.5, 0.5, 0.5, 1))  # Gray
            self.model.setLightOff(True)
        if self.game_object.physics:
            self.node_path = base.render.attachNewNode(self.game_object.physics)
        else:
            self.node_path = base.render.attachNewNode(self.game_object.kind)


        if self.model:
            self.model.reparentTo(self.node_path)
            bounds = self.model.getTightBounds()
            # bounds is two vectors
            bounds = bounds[1] - bounds[0]
            # bounds is now the widths with bounds[0] the x width, bounds[1] the y depth, bounds[2] the z height
            size = game_object.size

            x_scale = size[0] / bounds[0]
            y_scale = size[1] / bounds[1]
            z_scale = size[2] / bounds[2]

            self.model.setScale(x_scale, y_scale, z_scale)

        self.is_selected = False
        self.texture_on = True
        self.toggle_texture_pressed = False
        pub.subscribe(self.toggle_texture, 'input')

    def deleted(self):
        if self.model:
            self.model.removeNode()
        self.node_path.removeNode()

    def toggle_texture(self, events=None):
        if 'toggleTexture' in events:
            self.toggle_texture_pressed = True

    def tick(self):
        if not self.game_object.physics:
            h = self.game_object.z_rotation
            p = self.game_object.x_rotation
            r = self.game_object.y_rotation
            self.model.setHpr(h, p, r)
            self.model.setPos(*self.game_object.position)

        self.toggle_texture_pressed = False
        self.game_object.is_selected = False