from abc import ABC, abstractmethod

class MessageAPI(ABC):
    @abstractmethod
    def send_message(self, topic: str, message: str) -> bool:
        pass

    @abstractmethod
    def receive_message(self, topic: str, callback) -> bool:
        pass

class MQTTMessageAPI(MessageAPI):
    def __init__(self, client):
        self.client = client
        self.callbacks = {}

    def send_message(self, topic: str, message: str) -> bool:
        try:
            self.client.publish(topic, message)
            return True
        except Exception as e:
            print(f"MQTT 發佈失敗: {e}")
            return False

    def receive_message(self, topic: str, callback) -> bool:
        try:
            self.callbacks[topic] = callback
            self.client.subscribe(topic)
            def on_message(client, userdata, msg):
                topic = msg.topic
                if topic in self.callbacks:
                    self.callbacks[topic](topic, msg.payload.decode())
            self.client.on_message = on_message
            return True
        except Exception as e:
            print(f"MQTT 訂閱失敗: {e}")
            return False

class Device:
    def __init__(self, message_api: MessageAPI):
        self.message_api = message_api

    def enable(self) -> bool:
        return self.message_api.send_message("light/command", "on")

    def disable(self) -> bool:
        return self.message_api.send_message("light/command", "off")

    def get_status(self, callback) -> bool:
        return self.message_api.receive_message("light/status", callback)

    def set_status(self, status: str) -> bool:
        return self.message_api.send_message("light/command", status)

def enable_api(device: Device) -> bool:
    return device.enable()

def disable_api(device: Device) -> bool:
    return device.disable()

def get_status_api(device: Device, callback) -> bool:
    return device.get_status(callback)

def set_status_api(device: Device, status: str) -> bool:
    if status not in ["on", "off"]:
        print(f"無效的狀態值: {status}")
        return False
    return device.set_status(status)