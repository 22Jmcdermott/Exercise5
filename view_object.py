import pubsub.pub
from panda3d.core import CollisionBox, CollisionNode
from pubsub import pub

class ViewObject:
    def __init__(self, game_object):
        self.game_object = game_object

        if self.game_object.physics:
            self.node_path = base.render.attachNewNode(self.game_object.physics)
        else:
            self.node_path = base.render.attachNewNode(self.game_object.kind)


        if game_object.kind == "wall":
            self.model = base.loader.loadModel("Models/cube")
            self.model.setTexture(base.loader.loadTexture("Textures/maps/crate.png"))
        elif game_object.kind == "collectible":
            self.model = base.loader.loadModel("Models/Icosahedron")
        elif game_object.kind == "player":
            self.model = base.loader.loadModel("Models/anubus")
            self.model.setTexture(base.loader.loadTexture("Textures/maps/Material_#12_CL.tif"))
            # Scale the model appropriately
            self.model.setScale(0.5, 0.5, 0.5)
        else:
            self.model = base.loader.loadModel("Models/cube")
            self.model.setTexture(base.loader.loadTexture("Textures/crate.png"))

        self.model.reparentTo(self.node_path)
        self.model.setPos(*game_object.position)

        self.model.setTag('selectable', '')
        self.model.setPythonTag("owner", self)

        bounds = self.model.getTightBounds()
        bounds = bounds[1] - bounds[0]
        size = game_object.size
        x_scale = size[0] / bounds[0]
        y_scale = size[1] / bounds[1]
        z_scale = size[2] / bounds[2]
        self.model.setScale(x_scale, y_scale, z_scale)

        if game_object.kind == "collectible":
            self.model.setHpr(0, 0, 0)
            self.model.hprInterval(2.0, (360, 0, 0)).loop()

    def tick(self):
        if self.game_object.physics:
            transform = self.game_object.physics.getTransform()
            pos = transform.getPos()
            self.node_path.setPos(pos)
            self.node_path.setQuat(transform.getQuat())
        else:
            # Fallback to game object's position
            self.node_path.setPos(*self.game_object.position)
            self.node_path.setHpr(self.game_object.z_rotation,
                                  self.game_object.y_rotation,
                                  self.game_object.x_rotation)

    def deleted(self):
        self.node_path.removeNode()