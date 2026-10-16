"""Spawn the rover in Gazebo with ros2_control driving the wheels."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (Command, LaunchConfiguration, PythonExpression)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('rover_sim')
    model = os.path.join(share, 'urdf', 'rover.urdf.xacro')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')
    rviz = LaunchConfiguration('rviz')

    robot_description = ParameterValue(
        Command(['xacro ', model, ' use_gazebo:=true']), value_type=str)

    # -r starts the simulation running; -s runs the server without a window,
    # and --headless-rendering lets the GPU lidar render without a display.
    gz_args = ['-r -v2 ', world,
               PythonExpression(["'' if '", gui, "' == 'true' else ' -s --headless-rendering'"])]

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'rover',
                   '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'),
                   '-z', '0.01', '-Y', LaunchConfiguration('yaw')],
    )

    # Gazebo -> ROS: the sim clock and the lidar scan.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                   '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        parameters=[{'use_sim_time': True}],
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(share, 'rviz', 'gazebo.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=os.path.join(share, 'worlds', 'room.sdf'),
                              description='Gazebo world file'),
        DeclareLaunchArgument('gui', default_value='true',
                              description='Open the Gazebo window'),
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Also open RViz'),
        DeclareLaunchArgument('x', default_value='-1.8', description='Spawn x [m]'),
        DeclareLaunchArgument('y', default_value='0.0', description='Spawn y [m]'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Spawn heading [rad]'),
        # Lets Gazebo resolve package://rover_sim/meshes/... in the URDF.
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.dirname(share)),
        gazebo,
        robot_state_publisher,
        bridge,
        spawn,
        # Controllers can only load once the robot exists in Gazebo.
        RegisterEventHandler(OnProcessExit(target_action=spawn,
                                           on_exit=[joint_state_broadcaster])),
        RegisterEventHandler(OnProcessExit(target_action=joint_state_broadcaster,
                                           on_exit=[diff_drive_controller])),
        rviz_node,
    ])
