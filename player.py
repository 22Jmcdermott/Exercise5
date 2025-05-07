from panda3d.core import Vec3

from game_object import GameObject
from pubsub import pub


class Player(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)
        self.collected_items = 0
        pub.subscribe(self.handle_input, 'input')  # Changed to handle_input

    def handle_input(self, events):  # Added this method
        # Handle input events here if needed
        pass

    def move(self, move_vec):
        if self.physics:
            # Get current velocity
            current_vel = self.physics.getLinearVelocity()
            # Only modify X and Y components
            new_vel = Vec3(move_vec[0] * 10, move_vec[1] * 10, current_vel.z)
            self.physics.setLinearVelocity(new_vel)

    def collision(self, other):
        if other.kind == "collectible":
            # Remove the collected item
            pub.sendMessage('remove_object', obj_id=other.id)
            self.collected_items += 1

            # Check for win condition
            if self.collected_items >= 3:
                print("You win! Collected all items!")
