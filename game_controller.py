from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.bullet import BulletDebugNode
from panda3d.core import CollisionNode, GeomNode, CollisionRay, CollisionHandlerQueue, CollisionTraverser, MouseButton, \
    WindowProperties, Quat
from pubsub import pub
import sys

from world_view import WorldView
from game_world import GameWorld

controls = {
    'escape': 'toggleMouseMove',
    't': 'toggleTexture',
    'mouse1': 'toggleTexture',
    'w': 'forward',
    'a': 'left',
    's': 'backward',
    'd': 'right',
    'w-repeat': 'forward',
    'a-repeat': 'left',
    's-repeat': 'backward',
    'd-repeat': 'right',
}

held_keys = {
    'w': 'moveForward',
    's': 'moveBackward',
    'a': 'moveLeft',
    'd': 'moveRight',
}

class Main(ShowBase):
    def go(self):
        self.cTrav = CollisionTraverser()

        self.game_world.load_world()

        picker_node = CollisionNode('mouseRay')
        picker_np = self.camera.attachNewNode(picker_node)
        picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        picker_node.set_into_collide_mask(0)
        self.pickerRay = CollisionRay()
        picker_node.addSolid(self.pickerRay)
        # picker_np.show()
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(picker_np, self.rayQueue)

        self.taskMgr.add(self.tick)

        self.input_events = {}
        for key in controls:
            self.accept(key, self.input_event, [controls[key]])

        for key in held_keys:
            inputState.watchWithModifiers(held_keys[key], key)

        self.SpeedRot = 0.05
        self.CursorOffOn = 'Off'
        self.props = WindowProperties()
        self.props.setCursorHidden(True)
        self.win.requestProperties(self.props)

        self.run()

    def get_nearest_object(self):
        self.pickerRay.setFromLens(self.camNode, 0, 0)
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            entry = self.rayQueue.getEntry(0)
            picked_np = entry.getIntoNodePath()
            picked_np = picked_np.findNetTag('selectable')
            if not picked_np.isEmpty() and picked_np.getPythonTag("owner"):
                return picked_np.getPythonTag("owner")

        return None

    def input_event(self, event):
        self.input_events[event] = True


    def tick(self, task):
        if 'toggleMouseMove' in self.input_events:
            if self.CursorOffOn == 'Off':
                self.CursorOffOn = 'On'
                self.props.setCursorHidden(False)
            else:
                self.CursorOffOn = 'Off'
                self.props.setCursorHidden(True)
            self.win.requestProperties(self.props)

        pub.sendMessage('input', events=self.input_events)

        # Top-down camera setup
        if self.player:
            x, y, z = self.player.position
            # Position camera above player looking down
            self.camera.setPos(x, y, z + 55)
            self.camera.lookAt(x, y, z)
            #print(f"Camera at {self.camera.getPos()}, looking at {self.camera.getHpr()}")

        # Handle player movement
        move_speed = 2
        move_vec = [0, 0]
        if inputState.isSet('moveForward'):  # W key
            move_vec[1] += move_speed
        if inputState.isSet('moveBackward'):  # S key
            move_vec[1] -= move_speed
        if inputState.isSet('moveLeft'):  # A key
            move_vec[0] -= move_speed
        if inputState.isSet('moveRight'):  # D key
            move_vec[0] += move_speed

        if self.player and (move_vec[0] != 0 or move_vec[1] != 0):
            self.player.move(move_vec)

        self.game_world.tick(globalClock.getDt())
        self.player_view.tick()

        if self.game_world.get_property("quit"):
            sys.exit()

        self.input_events.clear()
        return Task.cont

    def new_player_object(self, game_object):
        if game_object.kind != 'player':
            return

        self.player = game_object

    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.render.setShaderAuto()

        self.instances = []
        self.player = None
        pub.subscribe(self.new_player_object, 'create')

        # Debug visualization for physics objects
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugNP = render.attachNewNode(debugNode)
        debugNP.show()

        # create model and view
        self.game_world = GameWorld(debugNode)
        self.player_view = WorldView(self.game_world)

        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(True)  # Make sure this is enabled
        debugNP = render.attachNewNode(debugNode)
        debugNP.show()


if __name__ == '__main__':
    main = Main()
    main.go()