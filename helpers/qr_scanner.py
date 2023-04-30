import cv2
from pyzbar import pyzbar


async def get_qr_codes(filename: str) -> list:
    """
    Функция, которая возвращает список данных из QR кода с фото.
    :param filename: Имя файла фото в строковом представлении.
    :return: Список данных из QR кода.
    """
    all_data = []
    img = cv2.imread(filename)
    qrcodes = pyzbar.decode(img)
    for qrcode in qrcodes:
        qrcodeData = qrcode.data.decode('utf-8')
        if qrcode.type == 'QRCODE':
            all_data.append(qrcodeData)
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    if bbox is not None and len(str(data)) != 0:
        all_data.append(str(data))
    return all_data
