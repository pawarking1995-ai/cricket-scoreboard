import requests
from urllib.parse import quote

class VMixController:
    def __init__(self, ip="127.0.0.1", port="8088"):
        self.base_url = f"http://{ip}:{port}/api/?"

    def send_cmd(self, params):
        try:
            url = self.base_url + params
            requests.get(url, timeout=0.5)
        except Exception as e:
            print(f"vMix Connection Error: {e}")

    def set_text(self, input_no, selected_name, text_value):
        encoded_text = quote(str(text_value))
        encoded_name = quote(str(selected_name))
        cmd = f"Function=SetText&Input={input_no}&SelectedName={encoded_name}&Value={encoded_text}"
        self.send_cmd(cmd)

    def set_image(self, input_no, selected_name, image_path):
        clean_path = str(image_path).replace("\\", "/")
        encoded_path = quote(clean_path)
        encoded_name = quote(str(selected_name))
        cmd = f"Function=SetImage&Input={input_no}&SelectedName={encoded_name}&Value={encoded_path}"
        self.send_cmd(cmd)

    def overlay_in(self, input_no, overlay_no=1):
        cmd = f"Function=OverlayInput{overlay_no}In&Input={input_no}"
        self.send_cmd(cmd)

    def overlay_out(self, input_no, overlay_no=1):
        cmd = f"Function=OverlayInput{overlay_no}Out&Input={input_no}"
        self.send_cmd(cmd)

    def set_striker_arrow(self, input_no, slot):
        if slot == 1:
            self.send_cmd(f"Function=SetImageVisibleOn&Input={input_no}&SelectedName=StrikerArrow1.Source")
            self.send_cmd(f"Function=SetImageVisibleOff&Input={input_no}&SelectedName=StrikerArrow2.Source")
        else:
            self.send_cmd(f"Function=SetImageVisibleOff&Input={input_no}&SelectedName=StrikerArrow1.Source")
            self.send_cmd(f"Function=SetImageVisibleOn&Input={input_no}&SelectedName=StrikerArrow2.Source")
