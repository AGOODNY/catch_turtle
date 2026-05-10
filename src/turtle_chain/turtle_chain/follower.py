import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math


class Follower(Node):

    def __init__(self, follower_name, target_name):
        super().__init__(f'{follower_name}_follower')

        self.follower_name = follower_name
        self.target_name = target_name

        self.pose = None
        self.target_pose = None

        self.pose_subscriber = self.create_subscription(
            Pose,
            f'/{follower_name}/pose',
            self.pose_callback,
            10
        )

        self.target_subscriber = self.create_subscription(
            Pose,
            f'/{target_name}/pose',
            self.target_callback,
            10
        )
        self.velocity_publisher = self.create_publisher(
            Twist,
            f'/{follower_name}/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.follow_target)

    def pose_callback(self, msg):
        self.pose = msg

    def target_callback(self, msg):
        self.target_pose = msg

    def follow_target(self):
        if self.pose is None or self.target_pose is None:
            return

        dx = self.target_pose.x - self.pose.x
        dy = self.target_pose.y - self.pose.y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        target_angle = math.atan2(dy, dx)

        angle_diff = target_angle - self.pose.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        cmd = Twist()
        if distance > 0.5:
            cmd.linear.x = min(2.0, 1.5 * distance)
            cmd.angular.z = 4.0 * angle_diff
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.velocity_publisher.publish(cmd)

