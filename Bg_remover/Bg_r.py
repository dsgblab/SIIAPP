import cv2
from dis_bg_remover import remove_background as rb 
model_path="C:\JoseDavidL\APIS\isnet_dis.onnx"
image_path="cafe.jpg"

img, mask = rb(model_path,image_path)

cv2.imwrite('generated.png',img)
cv2.imwrite('mask.png',mask)