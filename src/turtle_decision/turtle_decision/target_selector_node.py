#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from turtlesim.msg import Pose


class TargetSelectorNode(Node):
    def __init__(self):
        super().__init__('target_selector_node')

        # 主龟位姿
        self.master_pose = None
        self.create_subscription(Pose, '/turtle1/pose', self.master_pose_cb, 10)

        # 发布最近目标（给 B 用）
        self.target_pub = self.create_publisher(Point, '/nearest_turtle', 10)

        # 状态管理（只负责“未捕获乌龟”）
        self.uncaught_poses = {}   # name -> Pose

        # 定时器（持续计算最近目标）
        self.control_timer = self.create_timer(0.1, self.control_callback)

        self.get_logger().info('Target Selector Node started.')

    # ---------- 回调 ----------
    def master_pose_cb(self, msg):
        self.master_pose = msg

    def other_pose_cb(self, msg, name):
        """由 A 或系统注册订阅"""
        if name in self.uncaught_poses:
            self.uncaught_poses[name] = msg

    # ---------- 提供给 A 的接口 ----------
    def register_turtle(self, name):
        """
        A 在 spawn 成功后调用：
        告诉 C 有新乌龟
        """
        self.get_logger().info(f'Register turtle: {name}')

        self.uncaught_poses[name] = Pose()

        self.create_subscription(
            Pose,
            f'/{name}/pose',
            lambda msg, n=name: self.other_pose_cb(msg, n),
            10
        )

    def remove_turtle(self, name):
        """
        D（或系统）在“捕获后”调用
        """
        if name in self.uncaught_poses:
            self.uncaught_poses.pop(name)

    # ---------- 核心：选最近 ----------
    def control_callback(self):
        if self.master_pose is None:
            return

        if not self.uncaught_poses:
            return

        target_name = None
        min_dist = float('inf')

        # 过滤无效数据（还没收到位姿）
        valid_targets = {
            n: p for n, p in self.uncaught_poses.items()
            if p.x != 0 or p.y != 0
        }

        if not valid_targets:
            return

        for name, pose in valid_targets.items():
            dx = pose.x - self.master_pose.x
            dy = pose.y - self.master_pose.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                min_dist = dist
                target_name = name

        if target_name is None:
            return

        target_pose = valid_targets[target_name]

        # 👉 发布给 B（唯一输出接口）
        msg = Point()
        msg.x = target_pose.x
        msg.y = target_pose.y
        msg.z = 0.0

        self.target_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TargetSelectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()