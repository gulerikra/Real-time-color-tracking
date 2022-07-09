"""
kamera yardımıyla mavi ve kırmızı rengi algılıyor ve bounding box'a alıyor.
mavi rengin en ve boy değerlerini sql yardımıyla database kaydediyor.

"""
import cv2
import numpy as np
import sqlite3 #sqlite kütüphnesi

con = sqlite3.connect("renkler.db") # bağlantı kurma 
cursor = con.cursor() # cursor tanımlama

def tablo_olustur(): #sql içi tablo oluşturma fonksiyonu
    cursor.execute("CREATE TABLE IF NOT EXISTS boyut (en FLOAT, boy FLOAT)")  # tablo oluşturma sorgusu
    con.commit() #execute sorgusunun çalışması için
tablo_olustur()

cap = cv2.VideoCapture(0)
while True:        
    _, img = cap.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
    
    # red color
    red_lower = np.array([170,50,50])
    red_upper = np.array([180,255,255])

    # blue color
    blue_lower = np.array([100,150,0],np.uint8) 
    blue_upper = np.array([140,255,255],np.uint8)  

    # two color together
    red = cv2.inRange(hsv, red_lower, red_upper)
    blue = cv2.inRange(hsv, blue_lower, blue_upper)

    # Morfoloji işlemler, Dilation
    kernal = np.ones((5, 5), "uint8")
    
    red = cv2.dilate(red, kernal)
    res_red = cv2.bitwise_and(img, img, mask = red)

    blue = cv2.dilate(blue, kernal)
    res_blue = cv2.bitwise_and(img, img, mask = blue)

    # Tracking red
    (contours, hierarchy)=cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(img, "Red Detected ", (0, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
  

    # Tracking blue
    (contours, hierarchy)=cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, "Blue Detected ", (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
            print("w: ",w)
            print("h: ",h)

            # tabloya veri ekleme 
            def veri_ekle():
                cursor.execute("INSERT INTO boyut VALUES(?, ?)",(w,h)) # 'w' ve 'h' değerlerini ekleme
                con.commit()
            veri_ekle()

    cv2.imshow("RENK ALGILAMA", img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break

    