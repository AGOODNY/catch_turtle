from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. turtlesim 节点（提供仿真环境）
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),

        # 2. 任务A：随机生成乌龟（每3秒）
        Node(
            package='turtle_spawner',
            executable='turtle_spawner_node',
            name='turtle_spawner_node',
            output='screen'
        ),

        # 3. 任务C：目标选择器（发现最近乌龟，发布 /nearest_turtle）
        Node(
            package='turtle_decision',
            executable='target_selector_node',
            name='target_selector_node',
            output='screen'
        ),

        # 4. 任务B：控制器（让 turtle1 移动到目标）
        Node(
            package='turtle_control',
            executable='turtle_controller_node',
            name='turtle_controller_node',
            output='screen'
        ),

        # 5. 任务D：链管理器（处理捕获后建立跟随链）
        Node(
            package='turtle_chain',
            executable='chain_manager',
            name='chain_manager',
            output='screen'
        ),
    ])