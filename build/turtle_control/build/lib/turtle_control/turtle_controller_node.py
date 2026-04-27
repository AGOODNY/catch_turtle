import rclpy 
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from turtlesim.msg import Pose
import math

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')

        # 当前位姿
        self.pose = None

        # ❗ 不再设置默认目标（必须由 C 提供）
        self.target_x = None
        self.target_y = None

        # 是否接收到外部目标
        self.has_external_target = False

        # 参数（可调）
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 4.0)
        self.declare_parameter('angle_tolerance', 0.1)
        self.declare_parameter('distance_tolerance', 0.5)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.angle_tolerance = self.get_parameter('angle_tolerance').value
        self.distance_tolerance = self.get_parameter('distance_tolerance').value

        # 订阅自身位置
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # ✅ 订阅 C 提供的目标
        self.create_subscription(Point, '/nearest_turtle', self.target_callback, 10)

        # 发布控制
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 控制循环
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Turtle Controller started.')

    def pose_callback(self, msg: Pose):
        self.pose = msg

    def target_callback(self, msg: Point):
        # 接收来自 C 的目标
        self.target_x = msg.x
        self.target_y = msg.y
        self.has_external_target = True

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def control_loop(self):
        # ❗ 没有位姿 or 没有目标 → 不动
        if self.pose is None or not self.has_external_target:
            return

        dx = self.target_x - self.pose.x
        dy = self.target_y - self.pose.y

        distance = math.sqrt(dx * dx + dy * dy)
        angle_to_target = math.atan2(dy, dx)
        angle_diff = self.normalize_angle(angle_to_target - self.pose.theta)

        twist = Twist()

        # 控制逻辑
        if distance < self.distance_tolerance:
            # 到达目标（不再主动停止，由 C 决定下一目标）
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            if abs(angle_diff) > self.angle_tolerance:
                # 先转向
                twist.angular.z = self.angular_speed * angle_diff
                twist.linear.x = 0.0
            else:
                # 再前进（带减速）
                twist.linear.x = min(self.linear_speed, distance)
                twist.angular.z = 0.0

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()