import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, EnvironmentVariable
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    network_interface_arg = DeclareLaunchArgument(
        'network_interface',
        default_value=EnvironmentVariable('NETWORK_INTERFACE', default_value='offline'),
        description='Network interface for the Go2 SDK'
    )

    set_env_action = SetEnvironmentVariable(
        name='NETWORK_INTERFACE',
        value=LaunchConfiguration('network_interface')
    )

    # 1. Start the executor immediately
    executor_cmd = ExecuteProcess(
        cmd=['python3', '/root/workspace/src/fast_lio_go2/nav2/execution.py'],
        output='screen'
    )

    # 2. Launch Nav2 after a 4-second delay
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': 'false',
            'use_velocity_smoother': 'true',
            'map': '/root/workspace/src/fast_lio_go2/nav2/global_map.yaml',
            'params_file': '/root/workspace/src/fast_lio_go2/nav2/go2_nav2_params.yaml'
        }.items()
    )
    delayed_nav2_cmd = TimerAction(period=4.0, actions=[nav2_cmd])

    # 3. Launch FAST-LIO after a 10-second delay 
    fast_lio_dir = get_package_share_directory('fast_lio')
    fastlio_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fast_lio_dir, 'launch', 'mapping.launch.py')),
        launch_arguments={
            'use_sim_time': 'false'
        }.items()
    )
    delayed_fastlio_cmd = TimerAction(period=10.0, actions=[fastlio_cmd])

    ld = LaunchDescription()
    ld.add_action(network_interface_arg)
    ld.add_action(set_env_action)
    ld.add_action(executor_cmd)
    ld.add_action(delayed_nav2_cmd)
    ld.add_action(delayed_fastlio_cmd)

    return ld