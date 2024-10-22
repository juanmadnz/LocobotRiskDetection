import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Arguments
    joy_config = LaunchConfiguration('joy_config', default='xbox')

    # Launch descriptions
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource('realsense2_camera rs_launch.py')
    )

    yolov8_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource('yolov8_bringup yolov8.launch.py')
    )

    audio_player_node = Node(
        package='audio_common',
        executable='audio_player_node',
        output='screen'
    )

    tts_node = Node(
        package='tts_ros',
        executable='tts_node',
        output='screen'
    )

    teleop_twist_joy = Node(
        package='teleop_twist_joy',
        executable='teleop-launch.py',
        arguments=[f'joy_config:={joy_config}'],
        output='screen'
    )

    # Launch description
    return LaunchDescription([
        realsense_launch,
        yolov8_launch,
        audio_player_node,
        tts_node,
        teleop_twist_joy,
    ])


