"""Show the rover model in RViz with sliders for the wheel joints."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('rover_sim')
    default_model = os.path.join(share, 'urdf', 'rover.urdf.xacro')
    default_rviz = os.path.join(share, 'rviz', 'display.rviz')

    model = LaunchConfiguration('model')
    rviz_config = LaunchConfiguration('rviz_config')

    robot_description = ParameterValue(Command(['xacro ', model]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=default_model,
                              description='Path to the robot xacro file'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz,
                              description='Path to the RViz config file'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
        ),
    ])
