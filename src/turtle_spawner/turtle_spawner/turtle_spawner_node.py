import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
import random
import time

class TurtleSpawnerNode(Node):
    def __init__(self):
        super().__init__('turtle_spawner_node')
        self.spawn_client = self.create_client(Spawn, 'spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for the spawn service...')
        self.spawn_turtles()

        self.timer = self.create_timer(3.0, self.spawn_turtles)
        self.get_logger().info('Turtle Spawner Node has been started.Every 3 Seconds')
    
    def spawn_turtles(self):
        x= random.uniform(0.0, 10.5)
        y= random.uniform(0.0, 10.5)
        theta= random.uniform(0, 6.28)
        name = f'turtle_{int(time.time()*1000)}'

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = name

        self.future = self.spawn_client.call_async(request)
        self.future.add_done_callback(self.spawn_callback)
    
    def spawn_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'Spawned {response.name} at ({response.x}, {response.y}) with theta {response.theta}')
        except Exception as e:
            self.get_logger().error(f'Failed to spawn turtle: {e}')

def main(args=None):
    rclpy.init(args=args)
    turtle_spawner_node = TurtleSpawnerNode()
    rclpy.spin(turtle_spawner_node)
    turtle_spawner_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()