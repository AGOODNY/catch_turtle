import rclpy
from rclpy.node import Node

from turtlesim.srv import Spawn
from turtlesim.srv import SetPen

from std_msgs.msg import String

import random
import time


class TurtleSpawnerNode(Node):

    def __init__(self):
        super().__init__('turtle_spawner_node')

        self.spawn_client = self.create_client(Spawn, 'spawn')

        # 新增：关闭画笔服务
        self.pen_clients = {}

        # 通知 C
        self.new_turtle_pub = self.create_publisher(
            String,
            '/new_turtle',
            10
        )

        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Waiting for the spawn service...'
            )

        self.timer = self.create_timer(
            3.0,
            self.spawn_turtles
        )

        self.get_logger().info(
            'Spawner started (every 3s)'
        )

    def spawn_turtles(self):

        x = random.uniform(0.5, 10.5)
        y = random.uniform(0.5, 10.5)
        theta = random.uniform(0, 6.28)

        name = f'turtle_{int(time.time()*1000)}'

        request = Spawn.Request()

        request.x = x
        request.y = y
        request.theta = theta
        request.name = name

        future = self.spawn_client.call_async(request)

        future.add_done_callback(
            lambda f: self.spawn_callback(f, name)
        )

    def spawn_callback(self, future, name):

        try:
            future.result()

            self.get_logger().info(
                f'Spawned {name}'
            )

            # 通知 C
            msg = String()
            msg.data = name

            self.new_turtle_pub.publish(msg)

            # ===== 关闭轨迹 =====
            self.disable_pen(name)

        except Exception as e:
            self.get_logger().error(f'Failed: {e}')

    def disable_pen(self, turtle_name):

        service_name = f'/{turtle_name}/set_pen'

        pen_client = self.create_client(
            SetPen,
            service_name
        )

        while not pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                f'Waiting for {service_name}...'
            )

        request = SetPen.Request()

        # 核心：关闭画笔
        request.off = 1

        pen_client.call_async(request)

        self.get_logger().info(
            f'Pen disabled for {turtle_name}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = TurtleSpawnerNode()

    # 关闭 turtle1 的轨迹
    node.disable_pen('turtle1')

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()