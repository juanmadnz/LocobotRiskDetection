#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from math import pi

class LocobotSquareMove(Node):
    def __init__(self):
        super().__init__('locobot_square_move')
        self.cmd_vel_pub = self.create_publisher(Twist, 'mobile_base/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.state = 'forward'  # Inicialmente, el robot camina hacia adelante
        self.distance_travelled = 0
        self.angular_speed = 0.1  # Velocidad angular
        self.linear_speed = 0.1  # Velocidad lineal
        self.distance_to_travel = 10  # Distancia a recorrer en metros
        self.angle_to_rotate = 2* pi  # Ángulo a rotar en radianes
        self.angular_tolerance = 0.01  # Tolerancia angular
        self.angle_travelled = 0  # Nuevo atributo para el seguimiento del ángulo recorrido

    def timer_callback(self):
        if self.state == 'forward':
            self.move_forward()
        elif self.state == 'rotate':
            self.rotate()

    def move_forward(self):
        if self.distance_travelled < self.distance_to_travel:
            self.publish_twist(self.linear_speed, 0.0)  # Asegúrate de que el valor sea un float
            self.distance_travelled += self.linear_speed
        else:
            self.state = 'rotate'
            self.distance_travelled = 0

    def rotate(self):
        self.publish_twist(0.0, float(self.angular_speed))  # Asegúrate de que el valor sea un float
        self.get_logger().info('Rotating...')
        self.angle_travelled += self.angular_speed
        if abs(self.angle_travelled) >= self.angle_to_rotate - self.angular_tolerance:
            self.state = 'forward'
            self.angle_travelled = 0

    def publish_twist(self, linear_speed, angular_speed):
        twist = Twist()
        twist.linear.x = linear_speed
        twist.angular.z = angular_speed
        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    locobot_square_move = LocobotSquareMove()
    rclpy.spin(locobot_square_move)
    locobot_square_move.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
