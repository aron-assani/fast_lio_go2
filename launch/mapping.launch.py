import os.path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node

def generate_launch_description():
    package_path = get_package_share_directory('fast_lio')
    default_config_path = os.path.join(package_path, 'config')
    default_rviz_config_path = os.path.join(package_path, 'rviz', 'fastlio.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation clock if true'
    )
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )
    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file', default_value='utlidar.yaml',
        description='Config file'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config path'
    )

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=[
            PathJoinSubstitution([config_path, config_file]),
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(rviz_use)
    )

#   map_to_odom_tf = Node(
#       package='tf2_ros',
#       executable='static_transform_publisher',
#       name='map_to_odom_publisher',
#       parameters=[{'use_sim_time': use_sim_time}],
#       arguments=[
#           '--x', '0.0', '--y', '0.0', '--z', '0.0',
#           '--yaw', '0.0', '--pitch', '0.0', '--roll', '0.0',
#           '--frame-id', 'map', '--child-frame-id', 'odom'
#       ]
#   )

    odom_to_camera_init_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_camera_init_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '--x', '0.0', 
            '--y', '0.0', 
            '--z', '0.0',
            '--yaw', '0.0', 
            '--pitch', '2.878', 
            '--roll', '0.0',
            '--frame-id', 'odom', 
            '--child-frame-id', 'camera_init'
        ]
    )

    body_to_base_link_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='body_to_base_link_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '--x', '0.2894', 
            '--y', '0.0', 
            '--z', '-0.075',
            '--yaw', '0.0', 
            '--pitch', '-2.878', 
            '--roll', '0.0',
            '--frame-id', 'body',
            '--child-frame-id', 'base_link'
        ]
    )

    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[{
            'target_frame': 'odom', 
            'transform_tolerance': 0.05,
            'min_height': 0.25,
            'max_height': 0.45,
            'angle_min': -3.1415,
            'angle_max': 3.1415,
            'angle_increment': 0.0087,
            'scan_time': 0.1,
            'range_min': 0.3,
            'range_max': 15.0,
            'use_inf': True,
            'inf_epsilon': 1.0,
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('cloud_in', '/Laser_map'), 
            ('scan', '/go2_scan')
        ]
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)

    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)
#   ld.add_action(map_to_odom_tf)
    ld.add_action(odom_to_camera_init_tf)
    ld.add_action(body_to_base_link_tf)
    ld.add_action(pointcloud_to_laserscan_node)

    return ld