from pop import Psd, delay
psd = Psd()
while True:
    #센서 raw data return 받아 val에 전달
    val = psd.readAverage()#이동평균필터(moving average)
    # val을 calcDist에 인자로 전달하여 cm 값으로 계산된 값을 return 받아 cm에 저장
    distance = psd.calcDist(val)
    print("distance : {:0.2f}cm".format(distance))
    delay(1000)
