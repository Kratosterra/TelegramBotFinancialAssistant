import cv2
from pyzbar import pyzbar


async def get_qr_codes(filename):
    all_data = []
    img = cv2.imread(filename)
    qrcodes = pyzbar.decode(img)
    for qrcode in qrcodes:
        qrcodeData = qrcode.data.decode('utf-8')
        if qrcode.type == 'QRCODE':
            all_data.append(qrcodeData)
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    if bbox is not None:
        all_data.append(str(data))
    return all_data
