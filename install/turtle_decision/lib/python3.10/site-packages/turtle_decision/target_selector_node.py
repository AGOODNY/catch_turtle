#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from turtlesim.msg import Pose
from std_msgs.msg import String


class TargetSelectorNode(Node):
    def __init__(self):
        super().__init__('target_selector_node')

        self.master_pose = None
        self.create_subscription(Pose, '/turtle1/pose', self.master_pose_cb, 10)

        self.target_pub = self.create_publisher(Point, '/nearest_turtle', 10)

        self.create_subscription(String, '/new_turtle', self.new_turtle_callback, 10)

        self.uncaught_poses = {}

        # 捕捉阈值（可调）
        self.catch_distance = 0.6

        self.timer = self.create_timer(0.1, self.control_callback)

        self.get_logger().info('Target Selector started')

    def master_pose_cb(self, msg):
        self.master_pose = msg

    def new_turtle_callback(self, msg):
        name = msg.data
        self.get_logger().info(f'Received new turtle: {name}')
        self.register_turtle(name)

    def register_turtle(self, name):
        self.uncaught_poses[name] = Pose()

        self.create_subscription(
            Pose,
            f'/{name}/pose',
            lambda msg, n=name: self.other_pose_cb(msg, n),
            10
        )

    def other_pose_cb(self, msg, name):
        if name in self.uncaught_poses:
            self.uncaught_poses[name] = msg

    def control_callback(self):
        if self.master_pose is None or not self.uncaught_poses:
            return

        target_name = None
        min_dist = float('inf')

        valid_targets = {
            n: p for n, p in self.uncaught_poses.items()
            if p.x != 0 or p.y != 0
        }

        if not valid_targets:
            return

        # 找最近
        for name, pose in valid_targets.items():
            dx = pose.x - self.master_pose.x
            dy = pose.y - self.master_pose.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                min_dist = dist
                target_name = name

        if target_name is None:
            return

        # 捕捉逻辑
        if min_dist < self.catch_distance:
            self.get_logger().info(f'Caught {target_name}')
            self.uncaught_poses.pop(target_name)

            # 留给 D 的接口（
            # 可以在这里 publish /caught_turtle

            return  # 本轮不再发布旧目标

        # 正常发布目标
        target_pose = valid_targets[target_name]

        msg = Point()
        msg.x = target_pose.x
        msg.y = target_pose.y
        msg.z = 0.0

        self.target_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TargetSelectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()