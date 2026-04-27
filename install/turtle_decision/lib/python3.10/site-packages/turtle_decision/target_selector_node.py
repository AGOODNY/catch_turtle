#!/usr/bin/env python3
import math
import random
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from turtlesim.msg import Pose
from turtlesim.srv import Spawn


class TargetSelectorNode(Node):
    def __init__(self):
        super().__init__('target_selector_node')

        # Spawn 服务客户端
        self.spawn_client = self.create_client(Spawn, '/spawn')

        # 主龟位姿
        self.master_pose = None
        self.create_subscription(Pose, '/turtle1/pose', self.master_pose_cb, 10)

        # 发布最近目标（给 B 用）
        self.target_pub = self.create_publisher(Point, '/nearest_turtle', 10)

        # 状态管理
        self.spawn_count = 1
        self.uncaught_poses = {}   # name -> Pose

        # 定时器
        self.spawn_timer = self.create_timer(3.0, self.spawn_callback)
        self.control_timer = self.create_timer(0.1, self.control_callback)

        self.get_logger().info('Target Selector Node started.')

    # ---------- 回调 ----------
    def master_pose_cb(self, msg):
        self.master_pose = msg

    def other_pose_cb(self, msg, name):
        if name in self.uncaught_poses:
            self.uncaught_poses[name] = msg

    # ---------- spawn ----------
    def spawn_callback(self):
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Spawn service not available')
            return

        self.spawn_count += 1
        name = f'turtle{self.spawn_count}'

        req = Spawn.Request()
        req.x = random.uniform(0.5, 10.5)
        req.y = random.uniform(0.5, 10.5)
        req.theta = random.uniform(0, 2 * math.pi)
        req.name = name

        future = self.spawn_client.call_async(req)
        future.add_done_callback(lambda f, n=name: self.spawn_done(f, n))

    def spawn_done(self, future, name):
        try:
            future.result()
            self.get_logger().info(f'Spawned {name}')

            self.create_subscription(
                Pose,
                f'/{name}/pose',
                lambda msg, n=name: self.other_pose_cb(msg, n),
                10
            )

            self.uncaught_poses[name] = Pose()

        except Exception as e:
            self.get_logger().error(f'Failed to spawn {name}: {e}')

    # ---------- 核心：选最近 ----------
    def control_callback(self):
        if self.master_pose is None:
            return

        if not self.uncaught_poses:
            return

        target_name = None
        min_dist = float('inf')

        # 过滤无效数据
        valid_targets = {
            n: p for n, p in self.uncaught_poses.items()
            if p.x != 0 or p.y != 0
        }

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

        # 👉 发布给 B
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