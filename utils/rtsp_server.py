# server.py
from flask import Flask, Response
import cv2

app = Flask(__name__)

# USB 웹캠을 초기화합니다. 보통 0번이 기본 웹캠입니다.
# 여러 개의 카메라가 있다면 1, 2 등으로 바꿀 수 있습니다.
video_capture = cv2.VideoCapture(0) # /dev/video0 by defult

def generate_frames():
    """비디오 프레임을 지속적으로 캡처하고 JPEG 형식으로 인코딩하여 반환합니다."""
    while True:
        # 카메라에서 프레임 읽기
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # 프레임을 JPEG 이미지로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # 스트리밍을 위한 HTTP multipart 형식으로 프레임 반환
            # b'--frame\r\n'는 각 프레임의 경계를 나타냅니다.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """비디오 스트리밍 경로. generate_frames 함수를 통해 프레임을 전송합니다."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # host='0.0.0.0'는 서버가 로컬 네트워크의 모든 IP 주소에서 접속을 허용하도록 합니다.
    app.run(host='0.0.0.0', port=5000)
