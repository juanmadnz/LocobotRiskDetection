import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolov8_msgs.msg import DetectionArray, Detection
from audio_common_msgs.action import TTS
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor

class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')
        
        # Suscripción a los mensajes de detección
        self.subscription = self.create_subscription(
            DetectionArray,
            '/yolo/detections',
            self.detection_callback,
            10
        )
        self.get_logger().info('Detection Node started.')

        # Publicador para controlar el movimiento del robot
        self.cmd_vel_pub = self.create_publisher(Twist, '/mobile_base/cmd_vel', 10)
        self.moving_forward = False  # Indica si el robot se está moviendo hacia adelante

        # Temporizador para publicar comandos de movimiento a intervalos regulares
        self.timer_period = 0.1  # segundos
        self.timer = self.create_timer(self.timer_period, self.publish_movement)

        # Temporizador para actualizar las detecciones cada 1 segundo
        self.detection_timer_period = 1.0  # segundos
        self.detection_timer = self.create_timer(self.detection_timer_period, self.check_detections)

        # Temporizador para enviar alertas de TTS cada 5 segundos
        self.tts_timer_period = 5.0  # segundos
        self.tts_timer = self.create_timer(self.tts_timer_period, self.send_periodic_tts_alert)

        # Inicializar mensaje de movimiento
        self.move_msg = Twist()
        self.move_msg.linear.x = 0.1  # Velocidad inicial hacia adelante

        # Cliente de acción para TTS (Text-to-Speech)
        self.action_client = ActionClient(self, TTS, '/say')

        self.has_no_helmet = False  # Indicador para saber si se detecta "NO-Hardhat"
        self.tts_alert_sent = False  # Bandera para controlar el envío de alertas de TTS

    def publish_movement(self):
        if self.moving_forward:
            self.cmd_vel_pub.publish(self.move_msg)

    def detection_callback(self, msg: DetectionArray):
        self.get_logger().info('Detections:')
        self.has_no_helmet = False  # Reiniciar el indicador para cada nueva detección

        for detection in msg.detections:
            self.get_logger().info(f'Class: {detection.class_name}, Score: {detection.score}')
            self.get_logger().info(f'Bounding Box Center: ({detection.bbox.center.position.x}, {detection.bbox.center.position.y})')

            if detection.class_name == "NO-Hardhat" and detection.score > 0.5:
                self.get_logger().info('Riesgo detectado')
                self.has_no_helmet = True

        if self.has_no_helmet:
            if self.moving_forward:
                self.stop_locobot_move()
                self.tts_alert_sent = False  # Resetear la bandera de alerta TTS cuando se detiene el robot
        else:
            if not self.moving_forward:  # Comenzar a moverse solo si no ya está en movimiento
                self.start_moving_forward()

    def check_detections(self):
        if self.has_no_helmet and not self.tts_alert_sent:
            self.send_tts_alert("Hay alguien sin casco.")
            self.tts_alert_sent = True  # Marcar que se ha enviado la alerta TTS

    def start_moving_forward(self):
        self.move_msg.linear.x = 0.2  # Velocidad hacia adelante
        self.moving_forward = True
        self.get_logger().info('Locobot moving forward.')
        self.cmd_vel_pub.publish(self.move_msg)

    def stop_locobot_move(self):
        self.move_msg.linear.x = 0.0  # Velocidad cero para detenerse
        self.moving_forward = False
        self.cmd_vel_pub.publish(self.move_msg)
        self.get_logger().info('Locobot stopped.')

    def send_periodic_tts_alert(self):
        if self.has_no_helmet and not self.tts_alert_sent:
            self.send_tts_alert("Hay alguien sin casco.")
            self.tts_alert_sent = True  # Marcar que se ha enviado la alerta TTS

    def send_tts_alert(self, text: str):
        if not self.action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('TTS action server not available!')
            return

        goal_msg = TTS.Goal()
        goal_msg.text = text
        future = self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback):
        self.get_logger().info('Feedback received')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if goal_handle.accepted:
            self.get_logger().info('Goal accepted :)')
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.get_result_callback)
        else:
            self.get_logger().info('Goal rejected :(')
            self.stop_execution()  # Detener la ejecución si el objetivo es rechazado

    def get_result_callback(self, future):
        result = future.result()
        self.get_logger().info('TTS action completed')
        self.tts_alert_sent = False  # Resetear la bandera de alerta TTS al completar la acción
        self.stop_execution()  # Detener la ejecución al completar la acción

    def stop_execution(self):
        self.get_logger().info('Stopping node execution.')
        self.destroy_node()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

