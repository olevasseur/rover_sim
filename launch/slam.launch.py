"""Build a map with slam_toolbox (online async) from /scan and odometry.

With sim:=true (the default) this also starts the rover in Gazebo. With
sim:=false it starts only slam_toolbox and RViz, for use with the real
rover once its lidar driver and odometry are running.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('rover_sim')

    sim = LaunchConfiguration('sim')
    rviz = LaunchConfiguration('rviz')

    # The group keeps the included file's arguments (its rviz:=false) from
    # leaking into this file's own launch configurations.
    gazebo = GroupAction([IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'gui': LaunchConfiguration('gui'),
                          'world': LaunchConfiguration('world'),
                          'rviz': 'false'}.items(),
    )], condition=IfCondition(sim))

    # slam_toolbox's own launch file starts the node and walks it through
    # its lifecycle (configure, then activate).
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')),
        launch_arguments={'slam_params_file': os.path.join(share, 'config', 'slam_toolbox.yaml'),
                          'use_sim_time': sim}.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(share, 'rviz', 'slam.rviz')],
        parameters=[{'use_sim_time': sim}],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true',
                              description='Start Gazebo and use the sim clock'),
        DeclareLaunchArgument('gui', default_value='true',
                              description='Open the Gazebo window (sim only)'),
        DeclareLaunchArgument('world', default_value=os.path.join(share, 'worlds', 'room.sdf'),
                              description='Gazebo world file (sim only)'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz with the map'),
        gazebo,
        slam,
        rviz_node,
    ])
