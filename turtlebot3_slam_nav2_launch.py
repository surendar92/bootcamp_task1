#!/usr/bin/env python3
"""
turtlebot3_slam_nav2_launch.py

Single launch file for Task 1:
  - Starts Gazebo with the TurtleBot3 world and spawns the robot
  - Starts slam_toolbox (online async) to build a map from LIDAR + odom
  - Brings up the full Nav2 stack so the robot can be sent to a goal pose
  - Opens RViz2 with the TurtleBot3 navigation config

Usage:
  export TURTLEBOT3_MODEL=burger
  ros2 launch turtlebot3_slam_nav2_launch.py

Assumes the standard turtlebot3, turtlebot3_gazebo, slam_toolbox and
nav2_bringup packages are installed / built in your workspace.
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # --- Package share directories -----------------------------------
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    # --- Launch arguments ----------------------------------------------
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml_file = LaunchConfiguration('map', default='')
    params_file = LaunchConfiguration(
        'params_file',
        default=os.path.join(nav2_bringup_dir, 'params', 'nav2_params.yaml'),
    )
    slam_params_file = LaunchConfiguration(
        'slam_params_file',
        default=os.path.join(
            get_package_share_directory('slam_toolbox'),
            'config',
            'mapper_params_online_async.yaml',
        ),
    )
    rviz_config_file = LaunchConfiguration(
        'rviz_config',
        default=os.path.join(
            get_package_share_directory('nav2_bringup'), 'rviz', 'nav2_default_view.rviz'
        ),
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock',
    )
    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value='',
        description='Full path to map yaml file to load (leave empty when SLAM builds it live)',
    )
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=params_file,
        description='Full path to the Nav2 parameters file',
    )
    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=slam_params_file,
        description='Full path to the slam_toolbox parameters file',
    )

    # --- 1) Gazebo + TurtleBot3 world (spawns the robot too) -----------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    # --- 2) SLAM (online async) -----------------------------------------
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox_dir, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items(),
    )

    # --- 3) Nav2 bringup (planner, controller, behavior tree, etc.) ----
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_yaml_file,
            'params_file': params_file,
            'slam': 'True',
        }.items(),
    )

    # --- 4) RViz2 for visualization + sending goal poses ----------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    return LaunchDescription(
        [
            declare_use_sim_time,
            declare_map_yaml,
            declare_params_file,
            declare_slam_params_file,
            gazebo,
            slam,
            nav2,
            rviz,
        ]
    )
