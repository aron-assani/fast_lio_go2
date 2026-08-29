import sys
import os
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_system_default

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

class Nav2Executor(Node):
    def __init__(self, is_offline=False):
        super().__init__('nav2_executor')
        
        self.is_offline = is_offline
        self.sport_client = None
        
        if not self.is_offline and SDK_AVAILABLE:
            self.sport_client = SportClient()
            self.sport_client.SetTimeout(10.0)
            self.sport_client.Init()
            
            self.get_logger().info("Initializing robot posture...")
            self.sport_client.RecoveryStand()
            time.sleep(3.0)
            self.get_logger().info("Execution Bridge Online. Listening for /cmd_vel.")
        else:
            self.get_logger().warn("OFFLINE MODE: Hardware clients bypassed.")

        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, qos_profile_system_default)
        
        self.last_cmd_time = self.get_clock().now()
        self.is_moving = False 
        self.watchdog_timer = self.create_timer(0.5, self.watchdog_check)

    def cmd_vel_callback(self, msg: Twist):
        self.last_cmd_time = self.get_clock().now()
        
        vx = msg.linear.x
        vy = msg.linear.y
        yaw_rate = msg.angular.z

        # Deadbands for the Go2 gait
        MIN_LIN_VEL = 0.06
        MIN_ANG_VEL = 0.15

        if abs(vx) < MIN_LIN_VEL: vx = 0.0
        if abs(vy) < MIN_LIN_VEL: vy = 0.0
        if abs(yaw_rate) < MIN_ANG_VEL: yaw_rate = 0.0

        if vx == 0.0 and vy == 0.0 and yaw_rate == 0.0:
            if self.is_moving:
                if self.sport_client: 
                    self.sport_client.StopMove()
                self.is_moving = False
            return

        if self.sport_client:
            self.sport_client.Move(vx, vy, yaw_rate)
        self.is_moving = True

    def watchdog_check(self):
        # Stop moving if planner stops sending commands using the ROS 2 clock
        time_since_last_cmd = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if time_since_last_cmd > 0.5 and self.is_moving:
            self.get_logger().warn("Watchdog triggered: No cmd_vel received in 0.5s. Stopping.")
            if self.sport_client: 
                self.sport_client.StopMove()
            self.is_moving = False

    def shutdown_clients(self):
        if self.sport_client:
            self.sport_client.StopMove()
            time.sleep(0.5)
            self.sport_client.StandDown()

def main(args=None):
    iface = os.environ.get('NETWORK_INTERFACE', 'offline')
    if iface != 'offline' and SDK_AVAILABLE:
        ChannelFactoryInitialize(0, iface)
    
    rclpy.init(args=args)
    node = Nav2Executor(is_offline=(iface == 'offline'))
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown_clients()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
