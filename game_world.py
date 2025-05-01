from panda3d.bullet import BulletWorld, BulletBoxShape, BulletRigidBodyNode, BulletCapsuleShape, ZUp
from panda3d.core import Vec3, VBase3, TransformState
from pubsub import pub
from game_object import GameObject
from player import Player

class GameWorld:
    def __init__(self, debugNode=None):
        self.properties = {}
        self.game_objects = {}

        self.next_id = 0
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))
        self.setup_collision_groups()

        if debugNode:
            self.physics_world.setDebugNode(debugNode)
        self.kind_to_shape = dict(wall=self.create_box, player=self.create_capsule, collectible=self.create_box,floor=self.create_box)

    def setup_collision_groups(self):
        self.wall_group = 1 << 0
        self.player_group = 1 << 1
        self.floor_group = 1 << 2
        self.collectible_group = 1 << 3

        # Apply masks to existing objects
        for obj in self.game_objects.values():
            if obj.physics:
                if obj.kind == "wall":
                    obj.physics.setIntoCollideMask(self.wall_group)
                    obj.physics.setCollideMask(self.player_group)  # Player collides with walls
                elif obj.kind == "player":
                    obj.physics.setIntoCollideMask(self.player_group)
                    obj.physics.setCollideMask(self.wall_group | self.floor_group | self.collectible_group)
                elif obj.kind == "floor":
                    obj.physics.setIntoCollideMask(self.floor_group)
                    obj.physics.setCollideMask(self.player_group)  # Player collides with floor
                elif obj.kind == "collectible":
                    obj.physics.setIntoCollideMask(self.collectible_group)
                    obj.physics.setCollideMask(self.player_group)  # Player collides with collectibles

    def create_box(self, position, size, kind, mass):
        # Make sure size fits visual
        half_extents = Vec3(size[0] / 2, size[1] / 2, size[2] / 2)
        shape = BulletBoxShape(half_extents)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(*position)))
        self.physics_world.attachRigidBody(node)
        return node

    def create_capsule(self, position, size, kind, mass):
        # Size[0] = radius, size[1] = height
        shape = BulletCapsuleShape(size[0], size[1] - 2 * size[0], ZUp)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(*position)))
        self.physics_world.attachRigidBody(node)
        return node

    def remove_object(self, obj_id):
        if obj_id in self.game_objects:
            pub.sendMessage('delete', game_object=self.game_objects[obj_id])
            del self.game_objects[obj_id]


    def create_physics_object(self, position, kind, size, mass):
        if kind in self.kind_to_shape:
            node = self.kind_to_shape[kind](position, size, kind, mass)
            if kind == 'player':
                node.setLinearDamping(0.5)  # Add damping to prevent drifting
            return node
        return None

    def create_object(self, position, kind, size, mass, subclass):
        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, physics)

        self.next_id += 1
        self.game_objects[obj.id] = obj

        pub.sendMessage('create', game_object=obj)
        return obj

    def tick(self, dt):
        for id in self.game_objects:
            self.game_objects[id].tick()

        self.physics_world.do_physics(dt)

    def load_world(self):

        # Floor
        self.create_object([0, 0, 0], "floor", (100, 100, 1), 0, GameObject)

        # Walls
        self.create_object([0, -20, 1], "wall", (0.5, 40, 15), 0, GameObject)  # Vertical
        self.create_object([0, -20, 1], "wall", (40, 0.5, 15), 0, GameObject)  # Horizontal

        # Collectible items
        self.create_object([-6, 0, 1], "collectible", (0.5, 0.5, 0.5), 0, GameObject)
        self.create_object([6, 0, 1], "collectible", (0.5, 0.5, 0.5), 0, GameObject)
        #self.create_object([0, 0, 1], "collectible", (0.5, 0.5, 0.5), 0, GameObject)

        # Player
        self.create_object([0, 0, 2], "player", (1, 1, 1), 10, Player)

    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]

        return None

    def set_property(self, key, value):
        self.properties[key] = value
