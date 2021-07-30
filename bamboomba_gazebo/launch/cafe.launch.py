#!/usr/bin/env python3
import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, EnvironmentVariable, PathJoinSubstitution

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = os.path.join(get_package_share_directory('bamboomba_gazebo'),
                         'worlds', 'cafe.world')

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    robot_state_publisher = os.path.join(
        get_package_share_directory('bamboomba_description'),
        'launch',
        'robot_state_publisher.launch.py')

    # We need to append to the GAZEBO_MODEL_PATH for gazebo to find the Bamboomba's meshes
    create_description_path = str(Path(get_package_share_directory('create_description')).parent.absolute())

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='Use simulation (Gazebo) clock if true'),

        SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=[EnvironmentVariable('GAZEBO_MODEL_PATH'), os.pathsep, create_description_path]),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world, 'verbose': ' '}.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(robot_state_publisher),
            launch_arguments={'use_sim_time': use_sim_time}.items()
        ),

        Node(package='gazebo_ros',
             executable='spawn_entity.py',
             arguments=['-entity', 'bamboomba',
                        '-topic', 'robot_description',
                        '-package_to_model',
                        '-z 0.1'],
             output='screen'),
    ])
