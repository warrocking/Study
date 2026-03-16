 #---------------------
    # 프로그램 open
def main():
    file = open("basic.txt", "w", encoding="utf-8")
    file.write("Hello Python")
    file.close()
    
    # with 키워드
    # 조건문과 반복문이 들어가다 보면 파일을 열고 닫지 않는 실수를 하는 경우가 생길 수 있음.
    # 이런 실수 방지를 위해 with키워드가 있다.
    
    with open("basic.txt", "w", encoding="utf-8") as file:
        file.write("Hello Pythonss")
    #위와 같이 작성하면 with 구문이 종료될 때 자동으로 파일이 닫힘.
    
    with open("basic.txt", "r") as file:
        contents = file.read()
    print(contents)
    
    # 랜덤하게 1000명의 키와 몸무게 만들기
    import random
    hanguls =list("가나다라마바사아자차카타파하")
    with open("info.txt", "w") as file:
        for i in range(1000):
            name = random.choice(hanguls) + random.choice(hanguls)
            weight = random.randrange(40, 100)
            height = random.randrange(140, 200)
            file.write("{}, {}, {}\n".format(name, weight, height))
    
    with open("info.txt", "r") as file:
        for line in file:
            (name, weight, height) = line.strip().split(", ")
            if(not name or not weight or not height):
                continue
            bmi = int(weight)/((int(height)/100)**2)
            result = ""
            if(25<=bmi):
                result = "과체중"
            elif(18.5<=bmi):
                result = "정상체중"
            else:
                result = "저체중"
            
            print("\n".join([
                "이름 : {}",
                "몸무게 : {}",
                "키 : {}",
                "BMI : {}",
                "결과 : {}"
            ]).format(name, weight, height, bmi, result))
            print()
    
    
    

if __name__ == "__main__":
    main()